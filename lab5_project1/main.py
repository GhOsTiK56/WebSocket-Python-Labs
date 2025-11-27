import eventlet
import socketio
from eventlet import wsgi
from loguru import logger

from src.all_riddles import riddles

# Заставляем работать пути к статике
static_files = {'/': 'static/index.html', '/static': './static'}
sio = socketio.Server(cors_allowed_origins='*', async_mode='eventlet')
app = socketio.WSGIApp(sio, static_files=static_files)


# Обрабатываем подключение пользователя
@sio.event
def connect(sid, environ):
    logger.info(f"Пользователь {sid} подключился")


# Обрабатываем запрос очередного вопроса
@sio.on('next')
def next_event(sid, data):
    ...


# Обрабатываем отправку ответа
@sio.on('answer')
def receive_answer(sid, data):
    ...


# Обрабатываем отключение пользователя
@sio.event
def disconnect(sid):
    logger.info(f"Пользователь {sid} отключился")


if __name__ == '__main__':
    wsgi.server(eventlet.listen(("127.0.0.1", 8000)), app)
