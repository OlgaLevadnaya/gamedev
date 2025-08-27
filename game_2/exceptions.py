class GameException(Exception):
    """Базовое исключение для игровых ошибок."""
    pass

class LevelNotCompletedError(GameException):
    """Исключение вызывается когда уровень еще не пройден."""
    pass

class PrizeAlreadyAwardedError(GameException):
    """Исключение вызывается когда приз уже был выдан."""
    pass

class LevelPrizeNotConfiguredError(GameException):
    """Исключение вызывается когда для уровня не настроен приз."""
    pass