import socketio
import uvicorn
from fastapi import FastAPI

# Создаём экземпляр FastAPI приложения
app = FastAPI()

# Создаём экземпляр сервера Socket.IO с поддержкой асинхронного режима
sio = socketio.AsyncServer(async_mode='asgi')
# Оборачиваем FastAPI в Socket.IO ASGI приложение
socket_app = socketio.ASGIApp(sio, app)

@sio.event
async def connect(sid, environ):
    print(f"Пользователь {sid} подключился")

@sio.event
async def disconnect(sid):
    print(f"Пользователь {sid} отключился")

@app.get("/")
async def get_index():
    return "it works"

uvicorn.run(socket_app, host='0.0.0.0', port=80)
