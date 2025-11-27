import socketio
import eventlet

# Создаем экземпляр сервера Socket.IO
sio = socketio.Server()

# Создаем WSGI приложение и связываем его с Socket.IO
app = socketio.WSGIApp(sio)

# Обработчик события подключения
@sio.event
def connect(sid, environ):
    print(f"Клиент {sid} подключен")

# Обработчик события отключения
@sio.event
def disconnect(sid):
    print(f"Клиент {sid} отключен")

# Запускаем Eventlet WSGI сервер
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 80)), app)
