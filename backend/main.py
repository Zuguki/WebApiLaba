from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from routes import router_websocket, router_chats, router_messages
import chat_model
import message_model

chat_model.Base.metadata.create_all(bind=engine)
message_model.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI(
    title="Guskov Laba",
    summary="Лабораторка webApi",
    version="0.0.1",
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     http_protocol = request.headers.get("x-forwarded-proto", "http")
#     ws_protocol = "wss" if http_protocol == "https" else "ws"
#     server_urn = request.url.netloc
#     return templates.TemplateResponse("index.html",
#                                       {"request": request,
#                                        "http_protocol": http_protocol,
#                                        "ws_protocol": ws_protocol,
#                                        "server_urn": server_urn})


app.include_router(router_websocket)
app.include_router(router_chats)
app.include_router(router_messages)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='localhost', port=8000, reload=True)
