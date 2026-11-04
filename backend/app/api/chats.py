from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_

from app.database.session import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.source import Source
from app.schemas.chat import (
    ConversationResponse,
    ConversationDetailResponse,
    ConversationCreate,
    ConversationUpdate,
    MessageResponse,
)
from app.middleware.auth_deps import get_current_user

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.get("", response_model=List[ConversationResponse])
def get_conversations(
    q: Optional[str] = Query(None, description="Search term for conversation titles or message content"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Conversation).filter(Conversation.user_id == current_user.id)

    if q and q.strip():
        search_term = f"%{q.strip()}%"
        # Join with messages to search both title and messages
        matching_conv_ids_subquery = (
            db.query(Message.conversation_id)
            .filter(Message.content.like(search_term))
            .subquery()
        )
        query = query.filter(
            or_(
                Conversation.title.like(search_term),
                Conversation.id.in_(matching_conv_ids_subquery)
            )
        )

    conversations = query.order_by(desc(Conversation.updated_at)).all()

    if not conversations:
        return []

    conv_ids = [c.id for c in conversations]

    # Batch 1: Fetch message counts grouped by conversation
    counts_sub = (
        db.query(Message.conversation_id, func.count(Message.id))
        .filter(Message.conversation_id.in_(conv_ids))
        .group_by(Message.conversation_id)
        .all()
    )
    counts_map = {row[0]: row[1] for row in counts_sub}

    # Batch 2: Fetch last message content for each conversation in single pass
    latest_msg_sub = (
        db.query(Message.conversation_id, func.max(Message.id).label("max_id"))
        .filter(Message.conversation_id.in_(conv_ids))
        .group_by(Message.conversation_id)
        .subquery()
    )
    latest_msgs = (
        db.query(Message.conversation_id, Message.content)
        .join(latest_msg_sub, Message.id == latest_msg_sub.c.max_id)
        .all()
    )
    latest_msg_map = {row[0]: row[1] for row in latest_msgs}

    results = []
    for conv in conversations:
        msg_count = counts_map.get(conv.id, 0)
        last_content = latest_msg_map.get(conv.id)
        if last_content and len(last_content) > 60:
            last_content = last_content[:60] + "..."

        results.append(
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count,
                last_message=last_content
            )
        )

    return results

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    req: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = Conversation(
        user_id=current_user.id,
        title=req.title.strip() if req.title else "New Chat"
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0,
        last_message=None
    )

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return ConversationDetailResponse.model_validate(conv)

@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: int,
    req: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    conv.title = req.title.strip()
    db.commit()
    db.refresh(conv)

    msg_count = db.query(func.count(Message.id)).filter(Message.conversation_id == conv.id).scalar() or 0
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=msg_count,
        last_message=None
    )

@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted successfully."}

@router.delete("")
def clear_all_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(Conversation).filter(Conversation.user_id == current_user.id).delete()
    db.commit()
    return {"message": "All conversations have been cleared."}
