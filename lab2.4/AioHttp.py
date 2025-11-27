import socketio
from aiohttp import web

# Создаем экземпляр сервера Socket.IO
sio = socketio.AsyncServer(async_mode='aiohttp')

# Создаем aiohttp веб-приложение и связываем его с Socket.IO
app = web.Application()
sio.attach(app)

# Обработчик события подключения
@sio.event
async def connect(sid, environ):
    print(f"Клиент {sid} подключен")

# Обработчик события отключения
@sio.event
def disconnect(sid):
    print(f"Клиент {sid} отключен")

# Запускаем aiohttp веб-сервер
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=80)
