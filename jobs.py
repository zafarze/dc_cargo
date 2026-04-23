# -*- coding: utf-8 -*-
# DC Cargo — jobs.py
import asyncio
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import logger, XLSX_FILENAME, XLSX_PATH
from admin_utils import notify_admins
from handlers import get_text, process_excel_to_db
from db_utils import (
    get_dushanbe_arrivals_to_notify,
    set_dushanbe_notification_sent,
)


# === 1. Уведомление о прибытии в Душанбе ===

async def notify_dushanbe_arrival_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ищет заказы в Душанбе, о которых не уведомляли, и шлёт пуш."""
    logger.info("Job: checking Dushanbe arrivals in DC Cargo DB...")

    try:
        orders = await get_dushanbe_arrivals_to_notify()
        if not orders:
            logger.info("Job: no new Dushanbe arrivals.")
            return

        logger.info(f"Job: found {len(orders)} Dushanbe arrivals to notify.")
        tasks = [
            _send_arrival(context, o['user_id'], o['track_code'], o['language_code'])
            for o in orders
        ]
        await asyncio.gather(*tasks)

    except Exception as e:
        logger.error(f"CRITICAL Notify Job Error: {e}", exc_info=True)
        try:
            await notify_admins(context.bot, f"❌ Ошибка notify job DC Cargo:\n{e}")
        except Exception as e2:
            logger.error(f"Failed to notify admins about job error: {e2}")


async def _send_arrival(context, user_id, track_code, lang):
    try:
        lang = lang or 'ru'
        message = get_text('dushanbe_arrival_notification', lang).format(code=track_code)
        await context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
        await set_dushanbe_notification_sent(track_code)
        logger.info(f"Notified {user_id} about arrival of {track_code}")
    except Exception as e:
        err = str(e).lower()
        if "bot was blocked" in err or "user is deactivated" in err or "chat not found" in err:
            # Клиент недоступен — помечаем всё равно, чтобы не спамить каждые 5 мин
            await set_dushanbe_notification_sent(track_code)
            logger.warning(f"Notify {user_id} skipped ({track_code}): {e}")
        else:
            logger.warning(f"Notify failed for {user_id} ({track_code}): {e}")


# === 2. Миграция Excel → БД ===

async def reload_codes_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Каждые 5 мин тянет трек-коды из DC_Cargo.xlsx в БД."""
    logger.info(f"Job: starting Excel -> DB migration from {XLSX_FILENAME}...")

    file_path = str(XLSX_PATH)

    try:
        stats = await process_excel_to_db(file_path)
        logger.info(f"Job: migration finished. Stats: {stats}")

        if 'error' in stats:
            await notify_admins(
                context.bot,
                f"⚠️ Ошибка фоновой миграции DC Cargo Excel:\n<code>{stats['error']}</code>",
                parse_mode=ParseMode.HTML,
            )
        elif stats.get('failed', 0) > 0:
            await notify_admins(
                context.bot,
                f"⚠️ Миграция DC Cargo завершилась с ошибками:\n"
                f"Не удалось обработать {stats['failed']} из {stats['total']} строк.",
            )

    except FileNotFoundError:
        logger.error(f"Migration job: файл {file_path} не найден.")
        await notify_admins(
            context.bot,
            f"❌ DC Cargo: Файл {XLSX_FILENAME} не найден ({file_path}).",
        )
    except Exception as e:
        logger.error(f"CRITICAL Migration Job Error: {e}", exc_info=True)
        try:
            await notify_admins(context.bot, f"❌ DC Cargo migration error:\n{e}")
        except Exception as e2:
            logger.error(f"Failed to notify admins: {e2}")
