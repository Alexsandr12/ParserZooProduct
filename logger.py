import logging
from datetime import datetime
from config import LOGS_DIR


class MyLogger:
    """Класс для создания логгеров"""
    MY_FORMAT = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    def create_logger(self, name: str) -> logging.Logger:
        """Создает логгер

        Args:
            name: Имя логгера
        Returns:
            logging.Logger: созданный логгер
        """
        name_file = f"{name}{str(datetime.now().date()).replace(':', '.')}.log"

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        handler_file = logging.FileHandler(LOGS_DIR / name_file, encoding="utf-8")
        handler_stream = logging.StreamHandler()
        handler_file.setFormatter(self.MY_FORMAT)
        handler_stream.setFormatter(self.MY_FORMAT)
        logger.addHandler(handler_file)
        logger.addHandler(handler_stream)

        return logger


logger = MyLogger()
log = logger.create_logger("logger")
