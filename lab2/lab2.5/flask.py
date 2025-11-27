import eventlet
from flask import Flask
import socketio

sio = socketio.Server()

# Создаем экземпляр Flask приложения
flask_app = Flask(__name__)

app = socketio.WSGIApp(sio, flask_app)

@sio.event
def connect(sid, environ):
    print(f"Пользователь {sid} подключился")

@sio.event
def disconnect(sid):
    print(f"Пользователь {sid} отключился")

@flask_app.route("/")
def page_index():
    return "It works"

eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 80)), app)
