import socketio
import uvicorn
from fastapi import FastAPI, Request

# -----------------------------
# FastAPI
# -----------------------------
app = FastAPI()

# -----------------------------
# Socket.IO сервер
# -----------------------------
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, app)

# -----------------------------
# Подключённые пользователи
# -----------------------------
connected_users = []

# -----------------------------
# Socket.IO события
# -----------------------------
@sio.event
async def connect(sid, environ):
    print("Пользователь подключился:", sid)
    connected_users.append(sid)

@sio.event
async def disconnect(sid):
    print("Пользователь отключился:", sid)
    if sid in connected_users:
        connected_users.remove(sid)

# -----------------------------
# HTTP маршруты
# -----------------------------

@app.get("/")
async def root():
    """
    Задание 1 + 2:
    - Возвращает список подключённых пользователей
    - Рассылает событие message всем клиентам
    """
    await sio.emit("message", {"text": "someone visited over http"})
    return connected_users

@app.post("/broadcast")
async def broadcast(request: Request):
    """
    Задание 3:
    - POST {"message": "..."} рассылает сообщение всем подключённым пользователям
    """
    data = await request.json()
    msg = data.get("message", "")
    await sio.emit("message", {"text": msg})
    return {"status": "message sent"}

# -----------------------------
# Запуск
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
