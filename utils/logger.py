import logging
import os


def logger_init():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(os.path.dirname(project_dir), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)

    log_file_path = os.path.join(logs_dir, "bot_logs.log")

    # Логер инит
    logger = logging.getLogger(__name__)

    # Уровень логирования
    logger.setLevel(logging.INFO)

    # Проверка, чтобы не добавлять обработчики повторно
    if not logger.handlers:
        # Создание обработчика для записи логов в файл
        file_handler = logging.FileHandler(log_file_path)
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
