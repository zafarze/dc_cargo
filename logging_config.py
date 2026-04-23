# -*- coding: utf-8 -*-
import logging
import sys
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Настраивает систему логирования для всего приложения."""

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(BASE_DIR, 'logs')

    if not os.path.exists(LOG_DIR):
        try:
            os.makedirs(LOG_DIR)
        except OSError as e:
            print(f"Warning: Could not create log directory {LOG_DIR}. {e}", file=sys.stderr)

    log_file = os.path.join(LOG_DIR, 'bot.log')
    error_log_file = os.path.join(LOG_DIR, 'error.log')

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s:%(lineno)d) - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except PermissionError:
        print(f"Warning: No permission to write to {log_file}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Could not create file handler for {log_file}. {e}", file=sys.stderr)

    try:
        error_handler = logging.FileHandler(error_log_file, mode='a', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    except PermissionError:
        print(f"Warning: No permission to write to {error_log_file}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Could not create error handler for {error_log_file}. {e}", file=sys.stderr)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram.ext").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    initial_logger = logging.getLogger(__name__)
    initial_logger.info("--- (re)Logging setup complete ---")
