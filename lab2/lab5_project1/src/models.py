'''
Класс Riddle представляет собой модель загадки в приложении.
'''
class Riddle:
    """
    Класс для представления загадки
    """
    def __init__(self, number, text, answer):
        self.number = number  # Номер загадки
        self.text = text      # Текст загадки
        self.answer = answer  # Правильный ответ на загадку

    def check_answer(self, user_answer):
        """
        Проверяет, совпадает ли ответ пользователя с правильным ответом
        """
        # Сравниваем ответы без учета регистра и пробелов
        return self.answer.lower().strip() == user_answer.lower().strip()

    def to_dict(self):
        """
        Возвращает словарь с данными загадки
        """
        return {
            "number": self.number,
            "text": self.text,
            "answer": self.answer
        }


'''
Класс Player представляет собой модель игрока в приложении.
'''
class Player:
    """
    Класс для представления игрока
    """
    def __init__(self, sid):
        self.sid = sid                    # Идентификатор сокета игрока
        self.current_riddle = None        # Текущая загадка, над которой работает игрок
        self.score = 0                    # Счет игрока (количество правильных ответов)
        self.riddle_index = 0             # Индекс текущей загадки в списке

    def set_current_riddle(self, riddle):
        """
        Устанавливает текущую загадку для игрока
        """
        self.current_riddle = riddle

    def increment_score(self):
        """
        Увеличивает счет игрока
        """
        self.score += 1

    def reset_game(self):
        """
        Сбрасывает параметры игры для игрока
        """
        self.current_riddle = None  # Сбрасываем текущую загадку
        self.score = 0              # Сбрасываем счет
        self.riddle_index = 0       # Сбрасываем индекс загадки