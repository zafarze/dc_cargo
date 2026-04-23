# -*- coding: utf-8 -*-
import asyncio
from telegram.error import Forbidden, BadRequest
from config import logger, ADMIN_USER_IDS


async def notify_admins(bot, message: str, parse_mode=None):
    """Асинхронно отправляет сообщение всем админам."""
    tasks = [send_admin_message(bot, admin_id, message, parse_mode)
             for admin_id in ADMIN_USER_IDS]
    await asyncio.gather(*tasks)


async def send_admin_message(bot, admin_id: int, message: str, parse_mode=None):
    """Отправляет одно сообщение админу с обработкой ошибок."""
    try:
        await bot.send_message(chat_id=admin_id, text=message, parse_mode=parse_mode)
        logger.info(f"Successfully notified admin {admin_id}")
    except Forbidden:
        logger.warning(f"Cannot send message to admin {admin_id}: Bot was blocked")
    except BadRequest as e:
        if "chat not found" in str(e).lower():
            logger.error(f"Chat not found for admin {admin_id}")
        else:
            logger.error(f"Failed to send to admin {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending to admin {admin_id}: {e}")
