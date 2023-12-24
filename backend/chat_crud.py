from __future__ import annotations

from sqlalchemy.orm import Session

import schemas
from chat_model import Chat


def create_chat(db: Session, schema: schemas.ChatCreate):
    db_chat = Chat(**schema.model_dump())
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def get_chats(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Chat).offset(skip).limit(limit).all()


def get_chat(db: Session, chat_id: int):
    return db.query(Chat).filter_by(id=chat_id).first()


def update_chat(db: Session, chat_id: int, chat_data: schemas.ChatUpdate | dict):
    db_chat = db.query(Chat).filter_by(id=chat_id).first()

    chat_data = chat_data if isinstance(chat_data, dict) else chat_data.model_dump()

    if db_chat:
        for key, value in chat_data.items():
            if hasattr(db_chat, key):
                setattr(db_chat, key, value)

        db.commit()
        db.refresh(db_chat)

    return db_chat


def delete_chat(db: Session, chat_id: int):
    db_chat = db.query(Chat).filter_by(id=chat_id).first()
    if db_chat:
        db.delete(db_chat)
        db.commit()
        return True
    return False
