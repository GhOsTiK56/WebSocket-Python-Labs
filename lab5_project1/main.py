import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from loguru import logger

from src.models import Riddle, Player
from src.all_riddles import riddles

# Создаем ASGI приложение
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

# Подключаем socketio к ASGI приложению
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


# Обрабатываем подключение пользователя
@sio.event
async def connect(sid, environ):
    logger.info(f"Пользователь {sid} подключился")


# Обрабатываем запрос очередного вопроса
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


# Обрабатываем отправку ответа
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


# Обрабатываем отключение пользователя
@sio.event
async def disconnect(sid):
    logger.info(f"Пользователь {sid} отключился")
     
    # Удаляем игрока при отключении
    if sid in players:
        del players[sid]


if __name__ == '__main__':
    uvicorn.run(socket_app, host='127.0.0.1', port=8000)
