from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User, UserSettings
from app.schemas.settings import UserSettingsResponse, UserSettingsUpdate
from app.middleware.auth_deps import get_current_user
from app.services.security import verify_password

router = APIRouter(prefix="/settings", tags=["Settings"])

class DeleteAccountRequest(BaseModel):
    password: str

@router.get("", response_model=UserSettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return UserSettingsResponse.model_validate(settings)

@router.put("", response_model=UserSettingsResponse)
def update_settings(
    req: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    if req.theme is not None:
        settings.theme = req.theme
    if req.enter_to_send is not None:
        settings.enter_to_send = req.enter_to_send
    if req.show_timestamps is not None:
        settings.show_timestamps = req.show_timestamps
    if req.default_model is not None:
        settings.default_model = req.default_model
    if req.system_prompt is not None:
        settings.system_prompt = req.system_prompt

    db.commit()
    db.refresh(settings)
    return UserSettingsResponse.model_validate(settings)

@router.delete("/account")
def delete_account(
    req: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(req.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password. Account deletion canceled."
        )

    db.delete(current_user)
    db.commit()
    return {"message": "Your LOKR AI account has been permanently deleted."}
