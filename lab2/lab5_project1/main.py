'''
Акобян К.А. ИС 1.1

Этот код создает сервер Socket.IO для игры в загадки, который слушает подключения на порту 8000.
Пользователи могут подключаться к серверу и отвечать на загадки, зарабатывая очки за правильные ответы.
'''
import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from loguru import logger

from src.models import Riddle, Player
from src.all_riddles import riddles

'''
Создает экземпляр асинхронного сервера Socket.IO с разрешенной корс-политикой (cors_allowed_origins='*'),
что означает, что сервер позволяет подключения от всех источников.
CORS-политика (Cross-Origin Resource Sharing) — это механизм браузера,
который ограничивает запросы к серверу с других доменов,
протоколов или портов. По умолчанию браузер блокирует такие «кросс-доменные» запросы ради безопасности.
'''
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
app = FastAPI()

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Обслуживаем главную страницу
@app.get("/")
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

'''
ASGI (Asynchronous Server Gateway Interface) — это стандартный протокол взаимодействия между Python-веб-приложением и асинхронным веб-сервером.
Он определяет, как сервер (например, Uvicorn) вызывает Python-код, передаёт ему HTTP-запросы и получает ответы.

В контексте Socket.IO:
я создаю ASGI-совместимое приложение, которое объединяет обычный HTTP-сервер и Socket.IO-транспорт.

То есть ASGIApp:
    принимает HTTP-запросы (включая WebSocket-upgrade),
    маршрутизирует их в Socket.IO-сервер (`sio`),
    обеспечивает совместимость с любым ASGI-сервером (uvicorn, daphne, hypercorn).

Итог: это адаптер, который позволяет Socket.IO-серверу работать поверх стандартного питоновского асинхронного веб-серверного интерфейса.
'''
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Заставляем работать пути к статике
# Статические файлы теперь обрабатываются через FastAPI

# Словарь для хранения информации об игроках
players = {}

# Словарь для хранения информации об игроках
players = {}


def create_riddles():
    """
    Создает список объектов Riddle из данных
    """
    riddle_objects = []
    for riddle_data in riddles:
        riddle_obj = Riddle(
            number=riddle_data["number"],
            text=riddle_data["text"],
            answer=riddle_data["answer"]
        )
        riddle_objects.append(riddle_obj)
    return riddle_objects


# Создаем список загадок
riddle_list = create_riddles()


'''
Обработчик события подключения, используем для того, чтобы поприветствовать клиента, обновить счетчик посетителей на сайте,
отправить информацию, которая пригодится при использовании сервера.

Декораторы в Python — это механизм, который позволяет оборачивать функции или методы другой функцией
для изменения их поведения без изменения их исходного кода.

Это декоратор, потому что строка: @sio.event
оборачивает функцию `connect` в специальный обработчик событий Socket.IO.

Технически это работает так:
`sio.event` — это функция, которая принимает другую функцию.
Когда Python видит `@decorator`, он делает следующее: connect = sio.event(connect)

То есть функция передаётся методу `sio.event`, который:
регистрирует её как обработчик события `connect`;
возвращает обёрнутую функцию (или саму же), но уже привязанную к Socket.IO-серверу.

Таким образом, `@sio.event` — это декоратор, который автоматически
регистрирует функцию как обработчик события Socket.IO,
без необходимости вручную вызывать `sio.on('connect', connect)`.
'''
@sio.event
async def connect(sid, environ):
    logger.info(f"Пользователь {sid} подключился")


'''
Обработчик события next, который отправляет следующую загадку пользователю.
'''
@sio.on('next')
async def next_event(sid, data):
    # Создаем игрока, если он еще не существует
    if sid not in players:
        players[sid] = Player(sid)
    
    player = players[sid]
    
    # Проверяем, не закончились ли загадки
    if player.riddle_index >= len(riddle_list):
        # Игра закончена, отправляем сигнал "over"
        await sio.emit('over', {}, room=sid)
        # Сбрасываем игру для пользователя
        player.reset_game()
        # Отправляем обновленный счет (0) пользователю
        await sio.emit('score', {'value': player.score}, room=sid)
        return
    
    # Получаем текущую загадку
    current_riddle = riddle_list[player.riddle_index]
    player.set_current_riddle(current_riddle)
    
    # Отправляем загадку пользователю
    await sio.emit('riddle', current_riddle.to_dict(), room=sid)


'''
Обработчик события answer, принимает и обрабатывает ответ пользователя на загадку.
'''
@sio.on('answer')
async def receive_answer(sid, data):
    # Получаем игрока
    player = players.get(sid)
    if not player or not player.current_riddle:
        # Если игрока нет или у него нет текущей загадки, игнорируем
        return
    
    # Проверяем ответ
    user_answer = data.get('text', '')
    is_correct = player.current_riddle.check_answer(user_answer)
    
    # Подготавливаем данные для отправки результата
    result_data = {
        'riddle': player.current_riddle.to_dict(),
        'is_correct': is_correct
    }
    
    # Отправляем результат пользователю
    await sio.emit('result', result_data, room=sid)
    
    if is_correct:
        # Увеличиваем счет игрока
        player.increment_score()
    
    # Переходим к следующей загадке (вне зависимости от правильности ответа)
    player.riddle_index += 1
     
    # Отправляем обновленный счет пользователю
    await sio.emit('score', {'value': player.score}, room=sid)


'''
Для обработки отключения мы используем декоратор sio.event и функцию disconnect.
При отключении можно уменьшить счетчик пользователей, сообщить другим клиентам, что пользователь потерялся.
Событие disconnect срабатывает и тогда, когда пользователь отправил фрейм CLOSE, и когда сежду клиентом и сервером пропала связь.
Если соединение не было закрыто пользователем, после восстановления связи клиент попробует восстановить соединение.
'''
@sio.event
async def disconnect(sid):
    logger.info(f"Пользователь {sid} отключился")
     
    # Удаляем игрока при отключении
    if sid in players:
        del players[sid]


if __name__ == '__main__':
    uvicorn.run(socket_app, host='127.0.0.1', port=8000)
