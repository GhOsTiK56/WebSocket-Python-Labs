import socketio
from werkzeug.serving import run_simple

# Создаем WSGI приложение и связываем его с Socket.IO
sio = socketio.Server()
app = socketio.WSGIApp(sio)

# Обработчик события подключения
@sio.event
def connect(sid, environ):
    print(f"Клиент {sid} подключен")

# Обработчик события отключения
@sio.event
def disconnect(sid):
    print(f"Клиент {sid} отключен")

# Запускаем WSGI сервер
if __name__ == '__main__':
    run_simple('0.0.0.0', 80, app, use_reloader=True, use_debugger=True)
