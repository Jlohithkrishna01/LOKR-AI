import logging
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import httpx
import jwt
from jwt import PyJWKClient

from app.config import settings
from app.database.session import get_db
from app.models.user import User, UserSettings
from app.schemas.auth import (
    UserSignupRequest,
    UserLoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    GoogleAuthRequest,
    AppleAuthRequest,
)
from app.schemas.user import UserResponse
from app.services.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_random_token,
)
from app.middleware.auth_deps import get_current_user

logger = logging.getLogger("lokr.auth")

APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_TOKEN_EXCHANGE_URL = "https://oauth2.googleapis.com/token"

_apple_jwk_client: Optional[PyJWKClient] = None

def get_apple_jwk_client() -> PyJWKClient:
    global _apple_jwk_client
    if _apple_jwk_client is None:
        _apple_jwk_client = PyJWKClient(APPLE_JWKS_URL, cache_keys=True, max_cached_keys=16)
    return _apple_jwk_client

async def verify_google_token(
    credential: Optional[str] = None,
    access_token: Optional[str] = None,
    code: Optional[str] = None
) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Case 1: Server-side authorization code exchange (if code provided)
        if code and settings.GOOGLE_CLIENT_SECRET:
            try:
                token_resp = await client.post(
                    GOOGLE_TOKEN_EXCHANGE_URL,
                    data={
                        "code": code,
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "grant_type": "authorization_code",
                        "redirect_uri": "postmessage",
                    }
                )
                if token_resp.status_code == 200:
                    token_data = token_resp.json()
                    credential = token_data.get("id_token") or credential
                    access_token = token_data.get("access_token") or access_token
            except Exception as e:
                logger.warning(f"Google code exchange failed: {e}")

        # Case 2: OpenID Connect ID Token (credential)
        if credential:
            res = await client.get(f"{GOOGLE_TOKENINFO_URL}?id_token={credential}")
            if res.status_code != 200:
                logger.error(f"Google tokeninfo validation failed: {res.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired Google authentication token. Please sign in again."
                )
            data = res.json()
            if settings.GOOGLE_CLIENT_ID and data.get("aud") != settings.GOOGLE_CLIENT_ID:
                logger.error(f"Google client ID mismatch: aud={data.get('aud')} vs configured={settings.GOOGLE_CLIENT_ID}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google authentication token was issued for an unauthorized client ID."
                )
            return {
                "sub": data.get("sub"),
                "email": data.get("email"),
                "name": data.get("name") or data.get("email", "").split("@")[0],
                "picture": data.get("picture"),
                "email_verified": data.get("email_verified") in (True, "true"),
            }

        # Case 3: Google Access Token (Userinfo endpoint)
        if access_token:
            res = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if res.status_code != 200:
                logger.error(f"Google userinfo validation failed: {res.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired Google access token. Please sign in again."
                )
            data = res.json()
            return {
                "sub": data.get("sub"),
                "email": data.get("email"),
                "name": data.get("name") or data.get("email", "").split("@")[0],
                "picture": data.get("picture"),
                "email_verified": data.get("email_verified") in (True, "true"),
            }

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authentication requires either an ID token or access token."
        )

def verify_apple_token(id_token: str) -> dict:
    try:
        jwks_client = get_apple_jwk_client()
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        decode_options = {"verify_aud": bool(settings.APPLE_CLIENT_ID)}
        payload = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.APPLE_CLIENT_ID if settings.APPLE_CLIENT_ID else None,
            issuer="https://appleid.apple.com",
            options=decode_options,
        )
        return {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "email_verified": payload.get("email_verified") in (True, "true"),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Apple authentication token has expired. Please sign in again."
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Apple token decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Apple authentication token. Signature verification failed."
        )
    except Exception as e:
        logger.exception(f"Unexpected error verifying Apple token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify Apple authentication credentials."
        )

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(req: UserSignupRequest, db: Session = Depends(get_db)):
    # Check duplicate email
    existing_user = db.query(User).filter(User.email == req.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    pw_hash = hash_password(req.password)
    user = User(
        name=req.name.strip(),
        email=req.email.lower(),
        password_hash=pw_hash
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create default settings for user
    settings = UserSettings(user_id=user.id)
    db.add(settings)
    db.commit()

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials and try again."
        )

    if not user.password_hash:
        provider_name = user.provider.capitalize() if user.provider else "social"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This account is registered via {provider_name}. Please sign in using 'Continue with {provider_name}'."
        )

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials and try again."
        )

    # 30 days if remember_me, else standard 7 days
    expires_delta = timedelta(days=30) if req.remember_me else None
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=expires_delta
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/google", response_model=TokenResponse)
async def google_auth(req: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate or auto-register user using Google OAuth / OpenID Connect token."""
    info = await verify_google_token(
        credential=req.credential,
        access_token=req.access_token,
        code=req.code
    )
    email = info.get("email")
    sub = info.get("sub")
    name = info.get("name") or (email.split("@")[0] if email else "Google User")
    picture = info.get("picture")

    if not email or not sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not provide a valid email or user identifier."
        )

    # Check for existing user by google_id, legacy provider_id, or email
    user = db.query(User).filter(
        (User.google_id == sub) | ((User.provider == "google") & (User.provider_id == sub))
    ).first()

    if not user:
        user = db.query(User).filter(User.email == email.lower()).first()

    if user:
        # Existing user - link Google ID and preserve all existing data and chat history
        user.google_id = sub
        if not user.provider_id:
            user.provider_id = sub
        if not user.provider or user.provider == "email":
            user.provider = "google"
        if not user.profile_image and picture:
            user.profile_image = picture
        if not user.name or user.name in ("Google User", "Apple User"):
            user.name = name.strip()
        db.commit()
        db.refresh(user)
    else:
        # Auto-create new user
        user = User(
            name=name.strip(),
            email=email.lower(),
            password_hash=None,
            profile_image=picture,
            provider="google",
            provider_id=sub,
            google_id=sub,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create user default settings
        settings_record = UserSettings(user_id=user.id)
        db.add(settings_record)
        db.commit()

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/apple", response_model=TokenResponse)
def apple_auth(req: AppleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate or auto-register user using Apple Sign in with Apple JWT token."""
    info = verify_apple_token(req.id_token)
    email = info.get("email")
    sub = info.get("sub")

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apple authentication token is missing user identifier."
        )

    # Format user's name if passed in initial Apple authorization payload
    name = None
    if req.user and req.user.name:
        parts = [req.user.name.firstName or "", req.user.name.lastName or ""]
        name = " ".join(p for p in parts if p).strip()

    # Check for existing user by apple_id, legacy provider_id, or email
    user = db.query(User).filter(
        (User.apple_id == sub) | ((User.provider == "apple") & (User.provider_id == sub))
    ).first()

    if not user and email:
        user = db.query(User).filter(User.email == email.lower()).first()

    if user:
        # Existing user - link Apple ID and preserve all existing data and chat history
        user.apple_id = sub
        if not user.provider_id:
            user.provider_id = sub
        if not user.provider or user.provider == "email":
            user.provider = "apple"
        if name and (not user.name or user.name in ("Apple User", "Google User")):
            user.name = name.strip()
        db.commit()
        db.refresh(user)
    else:
        user_email = email.lower() if email else f"{sub[:12]}@privaterelay.appleid.com"
        display_name = name or (user_email.split("@")[0] if user_email else "Apple User")
        user = User(
            name=display_name.strip(),
            email=user_email,
            password_hash=None,
            provider="apple",
            provider_id=sub,
            apple_id=sub,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        settings_record = UserSettings(user_id=user.id)
        db.add(settings_record)
        db.commit()

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/link/google", response_model=UserResponse)
async def link_google(req: GoogleAuthRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Link Google account to currently authenticated user."""
    info = await verify_google_token(
        credential=req.credential,
        access_token=req.access_token,
        code=req.code
    )
    sub = info.get("sub")
    picture = info.get("picture")
    if not sub:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google authentication failed.")

    existing = db.query(User).filter(
        (User.google_id == sub) | ((User.provider == "google") & (User.provider_id == sub))
    ).first()
    if existing and existing.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This Google account is already linked to another LOKR AI user."
        )

    current_user.google_id = sub
    if not current_user.profile_image and picture:
        current_user.profile_image = picture
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)

@router.post("/link/apple", response_model=UserResponse)
def link_apple(req: AppleAuthRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Link Apple account to currently authenticated user."""
    info = verify_apple_token(req.id_token)
    sub = info.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apple authentication failed.")

    existing = db.query(User).filter(
        (User.apple_id == sub) | ((User.provider == "apple") & (User.provider_id == sub))
    ).first()
    if existing and existing.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This Apple account is already linked to another LOKR AI user."
        )

    current_user.apple_id = sub
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)

@router.get("/linked-accounts")
def get_linked_accounts(current_user: User = Depends(get_current_user)):
    """Get connected authentication providers for current user."""
    return {
        "google": bool(current_user.google_id or (current_user.provider == "google" and current_user.provider_id)),
        "apple": bool(current_user.apple_id or (current_user.provider == "apple" and current_user.provider_id)),
        "has_password": bool(current_user.password_hash),
        "email": current_user.email,
    }

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user:
        # Avoid user enumeration in public API
        return {
            "message": "If this email is registered, password reset instructions have been created.",
            "reset_token": None
        }

    token = generate_random_token(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    db.commit()

    return {
        "message": "Password reset token generated successfully.",
        "reset_token": token,
        "reset_url": f"/reset-password?token={token}"
    }

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == req.token).first()
    if not user or not user.reset_token_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset link. Please request a new one."
        )

    # Check expiry
    expiry = user.reset_token_expiry
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset token has expired. Please request a new one."
        )

    user.password_hash = hash_password(req.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()

    return {"message": "Your password has been successfully reset! You can now log in."}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
