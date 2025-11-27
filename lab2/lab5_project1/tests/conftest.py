'''
Конфигурационный файл для тестов (conftest.py) в проекте "Игра в загадки".
Содержит фикстуры для тестирования веб-сокетов с использованием pytest и socketio.
'''
import pytest
import socketio


@pytest.fixture
def client():
    """
    Фикстура для создания клиента Socket.IO
    """
    sio = socketio.Client()
    yield sio
    sio.disconnect()


@pytest.fixture
def events(client):
    """
    Фикстура для отлова всех эвентов которые приходят от бэка клиенту
    """
    all_events = {}

    def event_handler(event, data):
        all_events[event] = data

    client.on('*', event_handler)
    yield all_events


@pytest.fixture
def riddles():
    """
    Фикстура для получения ответа на задачу по тексту вопроса
    """
    from src.all_riddles import riddles

    result = {riddle['text']: riddle['answer'] for riddle in riddles}

    def get_riddle(text):
        return result.get(text)

    return get_riddle
