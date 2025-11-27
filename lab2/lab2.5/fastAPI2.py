import socketio
import uvicorn
from fastapi import FastAPI

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi')
socket_app = socketio.ASGIApp(sio, app)

# создаем счетсик пользователей
storage = {"user_counter": 0}

@sio.event
async def connect(sid, environ):
		# меняем счетчик пользователей
    storage["user_counter"] += 1
    print(f"Пользователь {sid} подключился")

@app.get("/")
async def get_index():
    # отдаем счетчик пользователей
    return f"user_counter = {storage['user_counter']}"

uvicorn.run(socket_app, host='0.0.0.0', port=80)
