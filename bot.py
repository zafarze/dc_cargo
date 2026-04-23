# -*- coding: utf-8 -*-
# DC Cargo — bot.py
import asyncio
import sys
import warnings

# Подавляем шумное предупреждение PTB про per_message=False (штатное для смешанных handlers)
warnings.filterwarnings("ignore", message=".*per_message=False.*")

from logging_config import setup_logging
setup_logging()

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    PicklePersistence,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
from config import ADMIN_USER_IDS, BOT_TOKEN, ORDERS_TABLE, PERSISTENCE_FILE, JOBS, logger
from db_utils import execute_query, get_all_users_count, get_db, init_db_pool, close_db_pool, release_db
from handlers import (
    get_main_conv_handler,
    document_handler,
    admin_mark_delivered,
    image_handler,
    error_handler,
)
from jobs import reload_codes_job, notify_dushanbe_arrival_job


def check_db_connection() -> bool:
    conn = None
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
        logger.info("PostgreSQL connection OK.")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}", exc_info=True)
        return False
    finally:
        if conn is not None:
            release_db(conn)


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "✅ Бот работает!\n"
        "✅ Получил ваше сообщение.\n"
        "✅ Готов к работе!"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        users_count = await get_all_users_count()
        res = await asyncio.to_thread(
            execute_query,
            f"SELECT COUNT(*) AS count FROM {ORDERS_TABLE}",
            fetchone=True,
        )
        orders_count = res['count'] if res else 0

        await update.message.reply_text(
            "📊 Статус бота:\n"
            "✅ Бот активен\n"
            f"👥 Пользователей в БД: {users_count}\n"
            f"📦 Заказов в БД: {orders_count}\n"
            "🔄 Фоновые задачи: активны\n"
            "🗄️ База данных: PostgreSQL"
        )
    except Exception as e:
        logger.error(f"/status failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Ошибка при проверке статуса: {e}")


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        "🐛 Отладочная информация:\n"
        f"ID пользователя: {user.id}\n"
        f"Имя: {user.first_name}\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"Язык: {user.language_code or 'N/A'}\n"
        f"Админ: {'✅' if user.id in ADMIN_USER_IDS else '❌'}"
    )


async def post_init(app: Application) -> None:
    logger.info("DC Cargo bot initialized.")
    init_db_pool()

    if not await asyncio.to_thread(check_db_connection):
        logger.critical("DB health-check failed after init_db_pool() — бот всё равно запускается, но работа с БД невозможна.")

    jq = app.job_queue
    if jq is None:
        logger.warning("JobQueue is None — фоновые задачи не будут запускаться.")
        return

    if JOBS.get('reload_codes', {}).get('enabled'):
        cfg = JOBS['reload_codes']
        jq.run_repeating(
            reload_codes_job,
            interval=cfg['interval'],
            first=cfg['first'],
            name='reload_codes',
        )
        logger.info(f"Job 'reload_codes' запланирован: каждые {cfg['interval']}с, первый через {cfg['first']}с.")

    if JOBS.get('notify_dushanbe', {}).get('enabled'):
        cfg = JOBS['notify_dushanbe']
        jq.run_repeating(
            notify_dushanbe_arrival_job,
            interval=cfg['interval'],
            first=cfg['first'],
            name='notify_dushanbe',
        )
        logger.info(f"Job 'notify_dushanbe' запланирован: каждые {cfg['interval']}с, первый через {cfg['first']}с.")


async def post_shutdown(app: Application) -> None:
    logger.info("DC Cargo bot shutting down...")
    close_db_pool()


def main():
    try:
        persistence = PicklePersistence(filepath=PERSISTENCE_FILE)

        application = (
            ApplicationBuilder()
            .token(BOT_TOKEN)
            .persistence(persistence)
            .connect_timeout(60.0)
            .read_timeout(120.0)
            .write_timeout(120.0)
            .post_init(post_init)
            .post_shutdown(post_shutdown)
            .build()
        )

        # Главный ConversationHandler (start, меню, LK, админ, addorder, broadcast)
        application.add_handler(get_main_conv_handler())

        # Команды вне диалога
        application.add_handler(CommandHandler("delivered", admin_mark_delivered), group=1)
        application.add_handler(CommandHandler("test", test_command), group=1)
        application.add_handler(CommandHandler("status", status_command), group=1)
        application.add_handler(CommandHandler("debug", debug_command), group=1)

        # Загрузка Excel админом (документ)
        application.add_handler(MessageHandler(filters.Document.ALL, document_handler))

        # Фото — вежливый ответ (вне conv)
        application.add_handler(MessageHandler(filters.PHOTO, image_handler))

        application.add_error_handler(error_handler)

        logger.info("DC Cargo bot запускается (polling)...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.critical(f"Critical startup error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
