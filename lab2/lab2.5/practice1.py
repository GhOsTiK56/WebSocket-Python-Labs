import socketio
import uvicorn
from fastapi import FastAPI, Request
import json

# Создаём экземпляр FastAPI приложения
app = FastAPI()

# Создаём экземпляр сервера Socket.IO с поддержкой асинхронного режима
sio = socketio.AsyncServer(async_mode='asgi')
# Оборачиваем FastAPI в Socket.IO ASGI приложение
socket_app = socketio.ASGIApp(sio, app)

# Список для хранения идентификаторов подключенных пользователей
connected_users = []

# Счетчик обращений
visit_counter = 0

@sio.event
async def connect(sid, environ):
    print(f"Пользователь {sid} подключился")
    # Добавляем идентификатор соединения в список
    connected_users.append(sid)

@sio.event
async def disconnect(sid):
    print(f"Пользователь {sid} отключился")
    # Удаляем идентификатор из списка при дисконнекте
    if sid in connected_users:
        connected_users.remove(sid)

@app.get("/")
async def get_index():
    global visit_counter
    # Увеличиваем счетчик обращений
    visit_counter += 1
    # Отправляем событие всем пользователям
    await sio.emit('message', {"text": "someone visited over http"})
    # Возвращаем страницу содержимым списка идентификаторов соединений
    return connected_users

@app.post("/")
async def handle_post(request: Request):
    # Получаем JSON-данные из запроса
    data = await request.json()
    message = data.get("message", "")
    # Отправляем событие message всем пользователям с телом сообщения
    await sio.emit('message', {"text": message})
    return {"status": "message sent"}

if __name__ == "__main__":
    uvicorn.run(socket_app, host='0.0.0.0', port=80)