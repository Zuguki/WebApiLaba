from __future__ import annotations

from sqlalchemy.orm import Session

import schemas
from message_model import Message
from chat_model import Chat


def create_message(db: Session, schema: schemas.MessageCreate):
    db_message = Message(**schema.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_messages(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Message).offset(skip).limit(limit).all()


def get_message(db: Session, chat_id: int):
    return db.query(Message).join(Chat).filter(Chat.id == chat_id).all()


def update_message(db: Session, message_id: int, message_data: schemas.MessageUpdate | dict):
    db_message = db.query(Message).filter_by(id=message_id).first()

    message_data = message_data if isinstance(message_data, dict) else message_data.model_dump()

    if db_message:
        for key, value in message_data.items():
            if hasattr(db_message, key):
                setattr(db_message, key, value)

        db.commit()
        db.refresh(db_message)
        return db_message
    return None


def delete_message(db: Session, message_id: int):
    db_message = db.query(Message).filter_by(id=message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
        return True
    return False
