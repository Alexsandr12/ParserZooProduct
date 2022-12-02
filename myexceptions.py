class MyRequestError(Exception):
    """Закончились попытки получения корректного ответа от сайта."""
    pass


class NotValidCategory(Exception):
    """Переданы не валидные Id катерогий"""
    pass
