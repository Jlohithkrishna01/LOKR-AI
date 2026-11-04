from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.user import UserResponse, UserUpdateRequest, ChangePasswordRequest
from app.middleware.auth_deps import get_current_user
from app.services.file_service import save_avatar_file
from app.services.security import verify_password, hash_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile")
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv_count = db.query(func.count(Conversation.id)).filter(Conversation.user_id == current_user.id).scalar() or 0
    msg_count = db.query(func.count(Message.id))\
        .join(Conversation, Message.conversation_id == Conversation.id)\
        .filter(Conversation.user_id == current_user.id).scalar() or 0

    return {
        "user": UserResponse.model_validate(current_user),
        "stats": {
            "conversation_count": conv_count,
            "message_count": msg_count
        }
    }

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if req.name is not None:
        current_user.name = req.name.strip()
    if req.bio is not None:
        current_user.bio = req.bio.strip()

    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)

@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    avatar_url = await save_avatar_file(file)
    current_user.profile_image = avatar_url
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)

@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.password_hash:
        provider_name = current_user.provider.capitalize() if current_user.provider else "social"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This account is signed in with {provider_name}. Password changes are managed through {provider_name}."
        )

    if not verify_password(req.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The current password you entered is incorrect."
        )

    current_user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"message": "Password changed successfully."}
