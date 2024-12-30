import logging


def loger_init():
    # Логер инит
    logger = logging.getLogger(__name__)

    # Уровень логирования
    logger.setLevel(logging.INFO)

    # Создание обработчика для записи логов в файл
    file_handler = logging.FileHandler("bot_logs.log")
    file_handler.setLevel(logging.INFO)

    # Формат для логов
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Добавление обработчика в логгер
    logger.addHandler(file_handler)

    # Вывод логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
