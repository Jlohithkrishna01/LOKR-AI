from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class SourceResponse(BaseModel):
    id: int
    title: str
    url: str
    source_name: str
    snippet: Optional[str] = None

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    created_at: datetime
    sources: List[SourceResponse] = []

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0
    last_message: Optional[str] = None

    class Config:
        from_attributes = True

class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Chat"

class ConversationUpdate(BaseModel):
    title: str

class SendMessageRequest(BaseModel):
    conversation_id: Optional[int] = None
    content: str
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    file_extracted_text: Optional[str] = None
    enable_web_search: Optional[bool] = None
    enable_image_generation: Optional[bool] = None
    model: Optional[str] = None
    client_timezone: Optional[str] = "Asia/Kolkata"
