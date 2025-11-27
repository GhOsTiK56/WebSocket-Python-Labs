class Riddle:
    """
    Класс для представления загадки
    """
    def __init__(self, number, text, answer):
        self.number = number
        self.text = text
        self.answer = answer

    def check_answer(self, user_answer):
        """
        Проверяет, совпадает ли ответ пользователя с правильным ответом
        """
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


class Player:
    """
    Класс для представления игрока
    """
    def __init__(self, sid):
        self.sid = sid
        self.current_riddle = None
        self.score = 0
        self.riddle_index = 0  # Индекс текущей загадки в списке

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
        self.current_riddle = None
        self.score = 0
        self.riddle_index = 0