from typing import Optional

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ChatBase(BaseModel):
    chat_name: str
    user_id: int


class ChatCreate(ChatBase):
    pass


class ChatUpdate(ChatBase):
    user_id: Optional[int] = None


class Chat(ChatBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Item
class MessageBase(BaseModel):
    user_id: int
    message: str
    chat_id: int


class MessageCreate(MessageBase):
    pass


class MessageUpdate(MessageBase):
    user_id: Optional[int] = None
    message: Optional[str] = None
    chat_id: Optional[int] = None


class Message(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
