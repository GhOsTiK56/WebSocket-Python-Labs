'''
Для обслуживания статических файлов по HTTP с использованием eventlet и socket.io, 
вы можете определить маппинг статических файлов в параметре static_files при конструировании socketio.WSGIApp. 
Предположим, что у вас есть файл index.html в каталоге static вашего проекта. Вот так:

Теперь при запросе к 0.0.0.0 мы увидим страничку index.html.

При этом и статика, и сокет-сервер будут использовать один и тот же порт. 
Http-порт, например, 80 будет использоваться для хендшейка, а сам обмен данными по протоколу WebSocket будет переадресован на другой порт.
'''


import eventlet
import socketio

# Путь к статике
static_files = { '/': 'static/index.html' }

sio = socketio.Server(cors_allowed_origins='*', async_mode='eventlet')

app = socketio.WSGIApp(sio, static_files=static_files)

@sio.event
def connect(sid, environ):
    print(f"Пользователь {sid} подключился")

@sio.event
def disconnect(sid):
    print(f"Пользователь {sid} отключился")

eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 80)), app)
