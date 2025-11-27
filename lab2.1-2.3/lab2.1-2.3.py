'''
Акобян К.А. ИС 1.1

Этот код создает простой сервер Socket.IO, который слушает подключения на порту 8000.

sid – это идентификатор пользователя, например Ix1RoDSgQ5BytHmFAAAB. 
Это строка, которая нужна, чтобы отличать одного пользователя от другого. Например, при рассылке сообщений.

environ – Это объект в котором передается информация о запросе. 
В нашем случае – о подключении. Это техническая информация о соединении и она не понадобится нам 
(по крайней мере до тех пор, пока вебсокеты работают нормально)
'''
import eventlet
import socketio
from datetime import datetime

# Создает экземпляр сервера Socket.IO с разрешенной корс-политикой (cors_allowed_origins='*'), 
# что означает, что сервер позволяет подключения от всех источников.
sio = socketio.Server(cors_allowed_origins='*')

# Словарь для хранения времени подключения каждого клиента
# Ключ - идентификатор сокета (sid), значение - объект datetime с временем подключения
connection_times = {}

def get_server_status(count):
    """
    Функция для определения статуса сервера в зависимости от количества подключенных пользователей
    :param count: количество подключенных пользователей
    :return: строка статуса сервера
    """
    if count == 0:
        return "Сервер пуст"
    elif count == 1:
        return "Пользователь один"
    else:  # count >= 2
        return "Команда в сборе"

# Создаем WSGI (Web Server Gateway Interface) приложение и связываем его с экземпляром сервера Socket.IO.
app = socketio.WSGIApp(sio)

# Объект для учета количества запросов без обработчиков
lost_queries = {"count": 0}

# Словарь для хранения счетов пользователей
user_scores = {}

# Выводим начальный статус сервера
print(get_server_status(len(connection_times)))


'''
Обработчик события подключения, используем для чтобы поприветствовать клиента, обновить счетчик посетителей на сайте, 
отправить информацию, которая пригодится при использовании сервера.
'''

@sio.event # Декоратор
def connect(sid, environ):
    # Выводим сообщение о подключении (для отладки)
    print(sid, "connected")
    
    # Записываем время подключения клиента в словарь
    # Ключ - идентификатор сокета (sid), значение - объект datetime с текущим временем
    connection_times[sid] = datetime.now()
    
    # Выводим сообщение о подключении клиента
    print(f"Клиент {sid} подключился")
    
    # Выводим статус сервера в зависимости от количества подключенных пользователей
    print(get_server_status(len(connection_times)))
    
    # Отправляем новому клиенту информацию о количестве пользователей онлайн
    sio.emit("message", {"online": len(connection_times)}, to=sid)
    
    # Отправляем обновленное количество пользователей всем подключенным клиентам, кроме нового
    sio.emit("message", {"online": len(connection_times)}, skip_sid=sid)


'''
Обработчик события message, принимает и обрабатывает сообщения от клиента.
'''
 
# Обработчик события message
@sio.on("message")
def handle_message(sid, data):
    # Отправляем сообщение всем подключенным пользователям, кроме отправителя
    sio.emit("message", data, skip_sid=sid)


'''
Обработчик события get_users_online, возвращает количество пользователей онлайн.
'''
 
# Обработчик события get_users_online
@sio.on("get_users_online")
def handle_get_users_online(sid, data):
    # Отправляем количество пользователей онлайн
    sio.emit("users", {"online": len(connection_times)}, room=sid)


'''
Обработчик события count_queries, возвращает количество потерянных запросов.
'''
 
# Обработчик события count_queries
@sio.on("count_queries")
def handle_count_queries(sid, data):
    # Отправляем количество потерянных запросов
    sio.emit("queries", {"lost": lost_queries["count"]}, room=sid)

'''
Обработчик события increase, увеличивает счет пользователя на 1.
'''
 
# Обработчик события increase
@sio.on("increase")
def handle_increase(sid, data):
    # Увеличиваем счет пользователя на 1
    if sid in user_scores:
        user_scores[sid] += 1
    else:
        user_scores[sid] = 1


'''
Обработчик события decrease, уменьшает счет пользователя на 1.
'''
 
# Обработчик события decrease
@sio.on("decrease")
def handle_decrease(sid, data):
    # Уменьшаем счет пользователя на 1
    if sid in user_scores:
        user_scores[sid] -= 1
    else:
        user_scores[sid] = -1


'''
Обработчик события get_score, возвращает текущий счет пользователя.
'''
 
# Обработчик события get_score
@sio.on("get_score")
def handle_get_score(sid, data):
    # Отправляем счет пользователя
    score = user_scores.get(sid, 0)
    sio.emit("score", {"score": score}, room=sid)


'''
Универсальный обработчик событий, обрабатывает все события, для которых нет специфических обработчиков.
Увеличивает счетчик потерянных запросов и отправляет сообщение об ошибке клиенту.
'''
 
# Универсальный обработчик событий
@sio.on('*')
def catch_all(event, sid, data):
    # Увеличиваем счетчик запросов без обработчиков
    lost_queries["count"] += 1
    # Отправляем сообщение об ошибке только если событие не является системным
    if event not in ["connect", "disconnect"]:
        sio.emit("error", {"message": f"No handler for event {event}"}, room=sid)

'''
Для обработки отключения мы используем декоратор sio.event и функцию disconnect.
При отключении можно уменьшить счетчик пользователей, сообщить другим клиентам, что пользователь потерялся. 
Событие disconnect срабатывает и тогда, когда пользователь отправил фрейм CLOSE, и когда сежду клиентом и сервером пропала связь. 
Если соединение не было закрыто пользователем, после восстановления связи клиент попробует восстановить соединение.
'''
# Обработчик события отключения
@sio.event # Декоратор
def disconnect(sid):
    # Получаем время подключения клиента
    connect_time = connection_times[sid]
    
    # Удаляем запись о клиенте из словаря
    del connection_times[sid]
    
    # Вычисляем продолжительность сессии
    session_duration = datetime.now() - connect_time
    
    # Выводим сообщение об отключении клиента и продолжительность его сессии
    print(f"Клиент {sid} отключился, время сессии: {session_duration}")
    
    # Выводим статус сервера после отключения клиента
    print(get_server_status(len(connection_times)))
    
    # Отправляем обновленное количество пользователей всем оставшимся подключенным клиентам
    sio.emit("message", {"online": len(connection_times)})

# Запускает eventlet WSGI сервер, слушая подключения на порту 8000 и используя ранее созданное приложение app.
eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
