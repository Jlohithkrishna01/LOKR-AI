from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(191), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    profile_image = Column(String(500), nullable=True)
    bio = Column(String(255), nullable=True)
    provider = Column(String(50), default="email", nullable=False)
    provider_id = Column(String(255), nullable=True, index=True)
    google_id = Column(String(255), nullable=True, index=True)
    apple_id = Column(String(255), nullable=True, index=True)
    reset_token = Column(String(255), nullable=True, index=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")

    @property
    def preferred_name(self):
        from app.services.greeting_service import extract_preferred_name
        return extract_preferred_name(self.name)

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme = Column(String(20), default="system")  # light, dark, system
    enter_to_send = Column(Boolean, default=True)
    show_timestamps = Column(Boolean, default=True)
    default_model = Column(String(100), default="qwen/qwen3.8-27b")
    system_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="settings")
