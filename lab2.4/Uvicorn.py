import socketio
import uvicorn

# Создаем экземпляр асинхронного сервера Socket.IO
sio = socketio.AsyncServer(async_mode='asgi')

# Создаем ASGI приложение и связываем его с Socket.IO
app = socketio.ASGIApp(sio)

# Обработчик события подключения
@sio.event
async def connect(sid, environ):
    print(f"Клиент {sid} подключен")

# Обработчик события отключения
@sio.event
async def disconnect(sid):
    print(f"Клиент {sid} отключен")

# Запускаем сервер с помощью Uvicorn
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)
