# -*- coding: utf-8 -*-
# DC Cargo — config.py
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# --- Пути ---
BASE_DIR = Path(__file__).resolve().parent

env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# --- Токен ---
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    logger.critical("TELEGRAM_TOKEN не найден (проверьте .env)")
    sys.exit(1)
else:
    logger.info("TELEGRAM_TOKEN загружен успешно")

# --- БД ---
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    logger.critical("DATABASE_URL не найден в .env")
    sys.exit(1)
else:
    logger.info("DATABASE_URL загружен успешно")

USERS_TABLE = "dc_users"
ORDERS_TABLE = "dc_orders"

# --- Администраторы DC Cargo ---
ADMIN_USER_IDS = [
    515809298,    # Zafar
    8039418689,
    6778668416, #Alijon
    8522797568, #Saif
    
]
logger.info(f"Загружено {len(ADMIN_USER_IDS)} ID администраторов")

# --- Файлы ---
XLSX_FILENAME = "DC_Cargo.xlsx"
XLSX_PATH = BASE_DIR / XLSX_FILENAME

BACKUP_DIR = "backups"
BACKUP_DIR_PATH = BASE_DIR / BACKUP_DIR
try:
    BACKUP_DIR_PATH.mkdir(exist_ok=True)
except Exception as e:
    logger.warning(f"Не удалось создать директорию бэкапов: {e}")

CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "")  # опционально

# --- Склад в Душанбе (для send_venue) ---
WAREHOUSE_DUSHANBE_LAT = 38.545857
WAREHOUSE_DUSHANBE_LON = 68.752327
WAREHOUSE_DUSHANBE_TITLE = "DC Cargo — склад в Душанбе"
WAREHOUSE_DUSHANBE_ADDRESS = "ул. Собира Абдуллоева, 28 (напротив Бозори Чал-Чам)"

# --- Фото (берём из app/img/) ---
IMG_DIR = BASE_DIR / "img"
PHOTO_CONTACT_PATH = IMG_DIR / "contact.png"
PHOTO_PRICE_PATH = IMG_DIR / "price.png"
# У DC Cargo пока один файл адреса — используем его и для Таджикистана, и для Китая.
PHOTO_ADDRESS_TAJIK_PATH = IMG_DIR / "adress_tj.JPG"
PHOTO_ADDRESS_CHINA_PATH = IMG_DIR / "address.jpg"

for name, path in [
    ("Контакты", PHOTO_CONTACT_PATH),
    ("Тарифы", PHOTO_PRICE_PATH),
    ("Адрес (Таджикистан)", PHOTO_ADDRESS_TAJIK_PATH),
    ("Адрес (Китай)", PHOTO_ADDRESS_CHINA_PATH),
]:
    if path.exists():
        logger.info(f"Фото {name}: {path.name} — найден")
    else:
        logger.warning(f"Фото {name}: {path} — НЕ НАЙДЕН")

# Видео-адрес (необязательно)
VIDEO_ADDRESS_TAJIK_PATH = IMG_DIR / "address_tajik.mov"

# --- Персистенс ---
PERSISTENCE_FILE = str(BASE_DIR / "dc_cargo_persistence.pickle")

# --- Job Queue ---
JOBS = {
    'reload_codes': {
        'enabled': True,
        'interval': 300,
        'first': 10,
    },
    'notify_dushanbe': {
        'enabled': True,
        'interval': 300,
        'first': 15,
    },
}
logger.info("Настройки фоновых задач загружены")

# --- Состояния ConversationHandler (как в CargoBot) ---
(
    START_ROUTES,
    AWAITING_SUBSCRIPTION,
    MAIN_MENU,
    LK_MENU,
    ADMIN_MENU,
    AWAITING_FULL_NAME,
    AWAITING_PHONE,
    AWAITING_ADDRESS,
    AWAITING_LANG_CHOICE,
    AWAITING_TRACK_CODE,
    LK_AWAIT_DELIVERY_ADDRESS,
    LK_AWAIT_PROFILE_ADDRESS,
    LK_AWAIT_PHONE,
    AWAITING_BROADCAST_MESSAGE,
    CONFIRM_BROADCAST,
    ADMIN_AWAIT_SEARCH_CODE,
    ADMIN_AWAIT_ORDER_CODE,
    ADMIN_AWAIT_ORDER_STATUS,
    ADMIN_AWAIT_ORDER_DATE_YIWU,
    ADMIN_AWAIT_ORDER_DATE_DUSH,
) = range(20)

logger.info(f"Загружено 20 состояний ConversationHandler")

logger.info("=" * 50)
logger.info("DC CARGO — конфигурация загружена")
logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"Токен: {'OK' if BOT_TOKEN else 'MISSING'}")
logger.info(f"БД: {'OK' if DATABASE_URL else 'MISSING'} (таблицы: {USERS_TABLE}, {ORDERS_TABLE})")
logger.info(f"Админы: {len(ADMIN_USER_IDS)}")
logger.info(f"Фоновые задачи: {sum(1 for j in JOBS.values() if j['enabled'])} активны")
logger.info("=" * 50)
