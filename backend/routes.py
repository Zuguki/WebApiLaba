from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

import schemas
from database import get_db
from sqlalchemy.orm import Session
from message_crud import (
    create_message, get_messages, get_message, update_message, delete_message
)
from chat_crud import (
    create_chat, get_chats, get_chat, update_chat, delete_chat,
)

router_websocket = APIRouter()
router_chats = APIRouter(prefix='/chats', tags=['chats'])
router_messages = APIRouter(prefix='/messages', tags=['messages'])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect_to_chat(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()

        try:
            self.active_connections[chat_id].append(websocket)
        except:
            self.active_connections[chat_id] = []
            self.active_connections[chat_id].append(websocket)

    def disconnect_from_chat(self, websocket: WebSocket, chat_id: int):
        self.active_connections[chat_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_chat(self, message: str, chat_id: int):
        for connection in self.active_connections[chat_id]:
            await connection.send_text(message)

    async def broadcast_chat_without_sender(self, message: str, chat_id: int, websocket: WebSocket):
        for connection in self.active_connections[chat_id]:
            if connection != websocket:
                await connection.send_text(message)


manager = ConnectionManager()


async def notify_clients(message: str, chat_id: int = -1):
    if chat_id == -1:
        for _, value in manager.active_connections.items():
            for connection in value:
                await connection.send_text(message)
    else:
        for connection in manager.active_connections[chat_id]:
            await connection.send_text(message)


@router_websocket.websocket("/ws/{chat_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, client_id: int):
    await manager.connect_to_chat(websocket, chat_id)
    await manager.broadcast_chat(f"Пользователь #{client_id} подключился к чату", chat_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_personal_message(f"Пользователь #{data['user_id']} сказал: {data['message']}", websocket)
    except WebSocketDisconnect:
        manager.disconnect_from_chat(websocket, chat_id)
        await manager.broadcast_chat_without_sender(f"Пользователь #{client_id} покинул чат", chat_id, websocket)


@router_chats.post("/", response_model=schemas.Chat)
async def create_chat_route(chat_data: schemas.ChatCreate, db: Session = Depends(get_db)):
    chat = create_chat(db, chat_data)
    await notify_clients(f"Chat created: {chat.chat_name}")
    return chat


@router_chats.get("/", response_model=List[schemas.Chat])
async def read_chats(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    chats = get_chats(db, skip=skip, limit=limit)
    return chats


@router_chats.get("/{chat_id}", response_model=schemas.Chat)
async def read_category(chat_id: int, db: Session = Depends(get_db)):
    chats = get_chat(db, chat_id)
    return chats


@router_chats.patch("/{chat_id}", response_model=schemas.Chat)
async def update_chat_route(chat_id: int, chat_data: schemas.ChatUpdate, db: Session = Depends(get_db)):
    updated_chat = update_chat(db, chat_id, chat_data)
    if updated_chat:
        await notify_clients(f"Chat updated: {updated_chat.user_id}")
        return updated_chat
    return {"message": "Chat not found"}


@router_chats.delete("/{chat_id}")
async def delete_category_route(chat_id: int, db: Session = Depends(get_db)):
    deleted = delete_chat(db, chat_id)
    if deleted:
        await notify_clients(f"Chat deleted: ID {chat_id}")
        return {"message": "Chat deleted"}
    return {"message": "Chat not found"}


@router_messages.post("/", response_model=schemas.Message)
async def create_message_route(schema: schemas.MessageCreate, db: Session = Depends(get_db)):
    message = create_message(db, schema)
    await notify_clients(f"Пользователь: {message.user_id} говорит: {message.message}", message.chat_id)
    return message


@router_messages.get("/", response_model=List[schemas.Message])
async def read_messages(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    messages = get_messages(db, skip=skip, limit=limit)
    return messages


@router_messages.get("/{chat_id}", response_model=List[schemas.Message])
async def read_message_in_chat(chat_id: int, db: Session = Depends(get_db)):
    message = get_message(db, chat_id)
    return message


@router_messages.patch("/{message_id}")
async def update_message_route(message_id: int, schema: schemas.MessageUpdate, db: Session = Depends(get_db)):
    updated_message = update_message(db, message_id, schema)
    if updated_message:
        await notify_clients(f"Message updated: {updated_message.user_id}", updated_message.chat_id)
        return updated_message
    return {"message": "Item not found"}


@router_messages.delete("/{message_id}")
async def delete_item_route(message_id: int, db: Session = Depends(get_db)):
    deleted = delete_message(db, message_id)
    if deleted:
        await notify_clients(f"Message deleted: ID {message_id}")
        return {"message": f"Message {message_id} deleted"}
    return {"message": "Item not found"}
