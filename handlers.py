# -*- coding: utf-8 -*-
# DC Cargo — handlers.py
import os
import asyncio
import re
import uuid
from datetime import datetime

import pandas as pd

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ParseMode, ChatAction
from telegram.error import Forbidden

from config import (
    logger,
    ADMIN_USER_IDS,
    CHANNEL_USERNAME,
    XLSX_FILENAME,
    XLSX_PATH,
    PHOTO_CONTACT_PATH,
    PHOTO_PRICE_PATH,
    PHOTO_ADDRESS_CHINA_PATH,
    START_ROUTES, AWAITING_SUBSCRIPTION, MAIN_MENU, LK_MENU, ADMIN_MENU,
    AWAITING_FULL_NAME, AWAITING_PHONE, AWAITING_ADDRESS, AWAITING_LANG_CHOICE,
    AWAITING_TRACK_CODE,
    LK_AWAIT_DELIVERY_ADDRESS, LK_AWAIT_PROFILE_ADDRESS, LK_AWAIT_PHONE,
    AWAITING_BROADCAST_MESSAGE, CONFIRM_BROADCAST, ADMIN_AWAIT_SEARCH_CODE,
    ADMIN_AWAIT_ORDER_CODE, ADMIN_AWAIT_ORDER_STATUS,
    ADMIN_AWAIT_ORDER_DATE_YIWU, ADMIN_AWAIT_ORDER_DATE_DUSH,
)

from db_utils import (
    get_user,
    register_user,
    update_user_lang,
    update_user_address,
    update_user_phone,
    get_all_users_count,
    get_all_user_ids,
    link_order_to_user,
    get_user_orders,
    request_delivery_multiple,
    get_delivery_requests,
    confirm_delivery,
    get_delivered_orders_paginated,
    get_delivered_orders_count,
    mark_order_delivered_by_code,
    admin_upsert_order,
    upsert_order_from_excel,
    get_order_by_track_code,
    get_archived_user_orders,
    mark_order_archived_by_code,
)

from texts import TEXTS, CONTACT_PHONE_TEL, CONTACT_PHONE_DISPLAY, OPERATOR_LINK
from admin_utils import notify_admins


# =================================================================
# --- Вспомогательные функции ---
# =================================================================

def get_text(key, lang='ru', default_lang='ru', fallback=None):
    default_value = fallback if fallback is not None else f"<{key}>"
    return TEXTS.get(lang, {}).get(key) or TEXTS.get(default_lang, {}).get(key, default_value)


def get_main_keyboard(lang, is_admin_user=False):
    buttons = get_text('main_buttons', lang)
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def get_lk_keyboard(lang, is_admin_flag):
    key = 'lk_admin_menu_buttons' if is_admin_flag else 'lk_menu_buttons'
    buttons = get_text(key, lang)
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def get_cancel_keyboard(lang):
    return ReplyKeyboardMarkup([[get_text('cancel_button', lang)]], resize_keyboard=True)


def is_admin(user_id):
    return user_id in ADMIN_USER_IDS


async def check_subscription(user_id, context):
    if not CHANNEL_USERNAME:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception as e:
        logger.error(f"Ошибка проверки подписки {user_id} в {CHANNEL_USERNAME}: {e}")
        if "chat not found" in str(e).lower() or "bot is not a member" in str(e).lower():
            return True
        return False


async def send_photo_safe(context, chat_id, photo_path, caption="", reply_markup=None, text_fallback=""):
    try:
        if not os.path.exists(photo_path):
            logger.warning(f"Фото не найдено: {photo_path}")
            await context.bot.send_message(chat_id, text_fallback or caption,
                                           reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            return

        await context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_PHOTO)
        with open(photo_path, 'rb') as f:
            await context.bot.send_photo(
                chat_id=chat_id, photo=f, caption=caption,
                reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Не удалось отправить фото {photo_path} (user {chat_id}): {e}")
        try:
            await context.bot.send_message(chat_id, text_fallback or caption,
                                           reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        except Exception as e2:
            logger.error(f"Резервное сообщение тоже не отправилось: {e2}")


async def clear_user_data(context):
    for key in ['full_name', 'phone_number', 'address', 'broadcast_message',
                'delivery_track_code', 'delivery_track_codes', 'available_delivery_orders']:
        context.user_data.pop(key, None)


def create_admin_regex(key_index_tuple):
    key, i, j = key_index_tuple
    try:
        text_ru = TEXTS['ru'][key][i][j]
        text_tg = TEXTS['tg'][key][i][j]
        text_en = TEXTS['en'][key][i][j]
    except (KeyError, IndexError):
        return "^$"
    return f"^({re.escape(text_ru)}|{re.escape(text_tg)}|{re.escape(text_en)})$"


REGEX_DELIVERY_REQUESTS = create_admin_regex(('lk_admin_menu_buttons', 0, 0))
REGEX_DELIVERED_LIST = create_admin_regex(('lk_admin_menu_buttons', 0, 1))
REGEX_STATS = create_admin_regex(('lk_admin_menu_buttons', 1, 0))
REGEX_BROADCAST = create_admin_regex(('lk_admin_menu_buttons', 1, 1))
REGEX_DOWNLOAD_EXCEL = create_admin_regex(('lk_admin_menu_buttons', 2, 0))
REGEX_ADMIN_PROFILE = create_admin_regex(('lk_admin_menu_buttons', 2, 1))


# =================================================================
# --- /start ---
# =================================================================

async def start(update, context):
    user = update.effective_user
    user_id = user.id
    name = user.first_name

    logger.info(f"User {user_id} ({user.username or 'NoUsername'}) started the bot.")
    await clear_user_data(context)

    db_user = await get_user(user_id)

    if db_user:
        lang = db_user['language_code'] or 'ru'
        context.user_data['lang'] = lang
        await update.message.reply_text(
            get_text('welcome_back', lang).format(name=name),
            reply_markup=get_main_keyboard(lang, is_admin(user_id))
        )
        return MAIN_MENU

    context.user_data['name_for_welcome'] = name
    lang_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru"),
        InlineKeyboardButton("Тоҷикӣ 🇹🇯", callback_data="lang_tg"),
        InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
    ]])
    await update.message.reply_text(
        TEXTS['ru']['welcome'].format(name=name),
        reply_markup=lang_keyboard
    )
    return AWAITING_LANG_CHOICE


async def select_language(update, context):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang
    logger.info(f"User {update.effective_user.id} selected language: {lang}")

    try:
        await query.edit_message_text(get_text('language_selected', lang))
    except Exception as e:
        logger.warning(f"edit_message_text failed: {e}")

    return await start_subscription_check(update, context)


# =================================================================
# --- Регистрация ---
# =================================================================

async def start_subscription_check(update, context):
    lang = context.user_data.get('lang', 'ru')
    user = update.effective_user

    if await check_subscription(user.id, context):
        return await start_registration(update, context)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text('subscribe_button_channel', lang),
                              url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton(get_text('subscribe_button_check', lang),
                              callback_data="check_subscription")],
    ])

    query = update.callback_query
    target = query.message if query else update.message
    await target.reply_text(get_text('subscribe_prompt', lang),
                            reply_markup=keyboard, disable_web_page_preview=True)
    return AWAITING_SUBSCRIPTION


async def process_subscription_check(update, context):
    query = update.callback_query
    user = update.effective_user
    lang = context.user_data.get('lang', 'ru')

    await query.answer(get_text('checking_button', lang), show_alert=False)

    if await check_subscription(user.id, context):
        await query.edit_message_text(get_text('subscription_success', lang))
        await query.message.reply_text(get_text('registration_start', lang))
        return await start_registration(update, context)
    else:
        await query.answer(get_text('subscribe_fail', lang), show_alert=True)
        return AWAITING_SUBSCRIPTION


async def start_registration(update, context):
    lang = context.user_data.get('lang', 'ru')
    target = update.message or update.callback_query.message
    await target.reply_text(get_text('registration_prompt_name', lang),
                            reply_markup=ReplyKeyboardRemove())
    return AWAITING_FULL_NAME


async def register_name(update, context):
    lang = context.user_data.get('lang', 'ru')
    full_name = update.message.text.strip()

    if len(full_name.split()) < 2:
        await update.message.reply_text(get_text('registration_invalid_name', lang))
        return AWAITING_FULL_NAME

    context.user_data['full_name'] = full_name
    phone_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(get_text('send_contact_button', lang), request_contact=True)]],
        resize_keyboard=True
    )
    await update.message.reply_text(
        get_text('registration_prompt_phone', lang).format(full_name=full_name),
        reply_markup=phone_keyboard, parse_mode=ParseMode.HTML
    )
    return AWAITING_PHONE


async def register_phone(update, context):
    lang = context.user_data.get('lang', 'ru')
    phone = update.message.contact.phone_number if update.message.contact else update.message.text.strip()

    if not re.match(r'^\+?\d{9,15}$', phone):
        await update.message.reply_text(get_text('registration_invalid_phone', lang),
                                        parse_mode=ParseMode.HTML)
        return AWAITING_PHONE

    if not phone.startswith('+'):
        phone = '+' + phone

    context.user_data['phone_number'] = phone
    await update.message.reply_text(
        get_text('registration_prompt_address', lang),
        reply_markup=ReplyKeyboardRemove()
    )
    return AWAITING_ADDRESS


async def register_address(update, context):
    lang = context.user_data.get('lang', 'ru')
    address = update.message.text.strip()
    user = update.effective_user
    user_id = user.id

    full_name = context.user_data.get('full_name')
    phone_number = context.user_data.get('phone_number')

    if not all([full_name, phone_number]):
        await update.message.reply_text(get_text('registration_error', lang))
        return await start(update, context)

    try:
        username = user.username or f"id{user_id}"
        success = await register_user(
            user_id=user_id, full_name=full_name,
            phone_number=phone_number, address=address,
            username=username, language_code=lang
        )
        if not success:
            raise Exception("register_user returned False")

        logger.info(f"User {user_id} successfully registered in DB.")
        await update.message.reply_text(
            get_text('registration_complete', lang).format(full_name=full_name),
            reply_markup=get_main_keyboard(lang, is_admin(user_id))
        )

        admin_msg = get_text('admin_notify_new_user', 'ru').format(
            full_name=full_name, phone=phone_number, address=address,
            user_id=user_id, username=f"@{username}" if user.username else "N/A"
        )
        await notify_admins(context.bot, admin_msg, parse_mode=ParseMode.HTML)
        await clear_user_data(context)
        return MAIN_MENU

    except Exception as e:
        logger.error(f"Ошибка регистрации {user_id}: {e}", exc_info=True)
        await update.message.reply_text(get_text('registration_error', lang),
                                        reply_markup=ReplyKeyboardRemove())
        return await start(update, context)


# =================================================================
# --- Главное меню ---
# =================================================================

async def track_order_start(update, context):
    lang = context.user_data.get('lang', 'ru')
    await update.message.reply_text(
        get_text('track_code_prompt', lang),
        reply_markup=get_cancel_keyboard(lang)
    )
    return AWAITING_TRACK_CODE


async def build_status_text_safe(order, lang):
    track_code = order['track_code']

    if order.get('status_delivered'):
        date_str = order.get('date_delivered') or "N/A"
        return get_text('track_code_found_other', lang).format(
            code=track_code, status=f"{order['status_delivered']} ({date_str})"
        )
    if order.get('status_dushanbe'):
        date_str = order.get('date_dushanbe') or "N/A"
        return get_text('track_code_found_dushanbe', lang).format(code=track_code, date=date_str)
    if order.get('status_yiwu'):
        date_str = order.get('date_yiwu') or "N/A"
        return get_text('track_code_found_yiwu', lang).format(code=track_code, date=date_str)

    return get_text('track_code_found_other', lang).format(code=track_code, status="В обработке")


async def link_order_callback(update, context):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')

    if not query.data.startswith('link_'):
        await query.edit_message_text(get_text('error', lang))
        return MAIN_MENU

    track_code = query.data.split('_', 1)[1].upper()
    linked = await link_order_to_user(track_code, user_id)

    if linked and linked > 0:
        await query.edit_message_text(get_text('order_link_success', lang), parse_mode=ParseMode.HTML)
        order = await get_order_by_track_code(track_code)
        if order:
            await context.bot.send_message(user_id, await build_status_text_safe(order, lang),
                                           parse_mode=ParseMode.HTML)
    else:
        await query.edit_message_text(get_text('order_link_fail', lang), parse_mode=ParseMode.HTML)

    await context.bot.send_message(
        chat_id=user_id, text=get_text('select_action', lang),
        reply_markup=get_main_keyboard(lang, is_admin(user_id))
    )
    return MAIN_MENU


async def process_track_code(update, context):
    lang = context.user_data.get('lang', 'ru')
    user_id = update.effective_user.id
    track_code = update.message.text.strip().upper()

    order = await get_order_by_track_code(track_code)
    response_text = ""
    keyboard = None

    if order:
        response_text = await build_status_text_safe(order, lang)
        owner_id = order.get('user_id')

        if not owner_id:
            try:
                linked = await link_order_to_user(track_code, user_id)
                if linked and linked > 0:
                    response_text += f"\n\n{get_text('order_link_success', lang)}"
                else:
                    keyboard = InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔗 Привязать этот заказ ко мне",
                                             callback_data=f"link_{track_code}")
                    ]])
            except Exception as e:
                logger.error(f"Link order {track_code} to {user_id}: {e}")
        elif owner_id != user_id:
            logger.warning(f"User {user_id} checked order {track_code} which belongs to {owner_id}")
    else:
        response_text = get_text('track_code_not_found', lang)

    await update.message.reply_text(response_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await update.message.reply_text(
        get_text('select_action', lang),
        reply_markup=get_main_keyboard(lang, is_admin(user_id))
    )
    return MAIN_MENU


async def show_contacts(update, context):
    lang = context.user_data.get('lang', 'ru')
    base = get_text('contacts', lang)
    phone_text = f"<b>📞 Телефон:</b> <a href='tel:{CONTACT_PHONE_TEL}'>{CONTACT_PHONE_DISPLAY}</a>"
    contacts_text = f"{base}\n\n{phone_text}"
    fallback = get_text('photo_contact_error', lang).format(contacts=contacts_text)

    await send_photo_safe(
        context, chat_id=update.effective_chat.id,
        photo_path=PHOTO_CONTACT_PATH, caption=contacts_text,
        text_fallback=fallback
    )
    return MAIN_MENU


async def show_prices(update, context):
    lang = context.user_data.get('lang', 'ru')
    prices = get_text('prices_text', lang)
    await send_photo_safe(
        context, chat_id=update.effective_chat.id,
        photo_path=PHOTO_PRICE_PATH, caption=prices,
        text_fallback=get_text('photo_price_error', lang).format(price_list=prices)
    )
    return MAIN_MENU


async def show_forbidden(update, context):
    lang = context.user_data.get('lang', 'ru')
    await update.message.reply_text(get_text('forbidden_text', lang),
                                    parse_mode=ParseMode.HTML,
                                    disable_web_page_preview=True)
    return MAIN_MENU


async def show_address_menu(update, context):
    lang = context.user_data.get('lang', 'ru')
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text('button_china', lang), callback_data="address_china")],
        [InlineKeyboardButton(get_text('button_tajikistan', lang), callback_data="address_tajikistan")],
    ])
    await update.message.reply_text(get_text('address_text', lang), reply_markup=keyboard)
    return MAIN_MENU


async def show_address_callback(update, context):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('lang', 'ru')
    address_type = query.data.split('_')[1]

    if address_type == "china":
        caption = get_text('address_caption_china', lang)
        await send_photo_safe(
            context, query.message.chat_id,
            PHOTO_ADDRESS_CHINA_PATH, caption,
            text_fallback=get_text('photo_address_error', lang).format(address=caption)
        )
    else:
        caption = get_text('address_caption_tajikistan', lang)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💬 {OPERATOR_LINK}", url=f"https://{OPERATOR_LINK}")]
        ])
        await query.message.reply_text(caption, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    return MAIN_MENU


async def change_language_start(update, context):
    lang_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Русский 🇷🇺", callback_data="set_lang_ru"),
        InlineKeyboardButton("Тоҷикӣ 🇹🇯", callback_data="set_lang_tg"),
        InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en"),
    ]])
    await update.message.reply_text(
        "Выберите язык / Забонро интихоб кунед / Select language:",
        reply_markup=lang_keyboard
    )
    return MAIN_MENU


async def change_language_callback(update, context):
    query = update.callback_query
    await query.answer()

    lang = query.data.split('_')[2]
    user_id = update.effective_user.id

    try:
        success = await update_user_lang(user_id, lang)
        if not success:
            raise Exception("update_user_lang False")
        context.user_data['lang'] = lang
        await query.edit_message_text(get_text('language_selected', lang))
        await query.message.reply_text(
            get_text('select_action', lang),
            reply_markup=get_main_keyboard(lang, is_admin(user_id))
        )
    except Exception as e:
        logger.error(f"change_language error for {user_id}: {e}")
        await query.message.reply_text(
            "Произошла ошибка / Хатогӣ рух дод",
            reply_markup=get_main_keyboard(context.user_data.get('lang', 'ru'), is_admin(user_id))
        )
    return MAIN_MENU


async def show_help(update, context):
    lang = context.user_data.get('lang', 'ru')
    await update.message.reply_text(get_text('help_message', lang), parse_mode=ParseMode.HTML)
    return MAIN_MENU


# =================================================================
# --- Личный кабинет ---
# =================================================================

async def lk_menu_start(update, context):
    user = update.effective_user
    lang = context.user_data.get('lang', 'ru')

    db_user = await get_user(user.id)
    if not db_user:
        await update.message.reply_text(get_text('registration_required', lang))
        return await start(update, context)

    await update.message.reply_text(
        get_text('lk_welcome', lang).format(name=user.first_name),
        reply_markup=get_lk_keyboard(lang, is_admin(user.id))
    )
    return LK_MENU


async def lk_back_to_main(update, context):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    await update.message.reply_text(
        get_text('select_action', lang),
        reply_markup=get_main_keyboard(lang, is_admin(user_id))
    )
    return MAIN_MENU


async def lk_show_profile(update, context):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')

    db_user = await get_user(user_id)
    if not db_user:
        await update.message.reply_text(get_text('registration_required', lang))
        return await start(update, context)

    profile_text = get_text('profile_info', lang).format(
        full_name=db_user.get('full_name') or 'N/A',
        phone_number=db_user.get('phone_number') or 'N/A',
        address=db_user.get('address') or get_text('profile_address_not_set', lang)
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text('profile_button_edit_phone', lang), callback_data="lk_edit_phone")],
        [InlineKeyboardButton(get_text('profile_button_edit_address', lang), callback_data="lk_edit_address")],
    ])
    await update.message.reply_text(profile_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return LK_MENU


async def lk_show_orders(update, context):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    target = update.message or update.callback_query.message

    orders = await get_user_orders(user_id)

    if not orders:
        await target.reply_text(get_text('lk_no_orders', lang))
        return LK_MENU

    response = get_text('lk_orders_title', lang) + "\n\n"
    messages = []

    for order in orders:
        if order.get('status_delivered') == 'Доставлен':
            status_text = get_text('status_delivered', lang)
            date_text = order.get('date_delivered') or "N/A"
        elif order.get('status_delivered') == 'Запрошена':
            status_text = get_text('status_deliveryrequested', lang)
            date_text = order.get('date_dushanbe') or "N/A"
        elif order.get('status_dushanbe'):
            status_text = get_text('status_dushanbe', lang)
            date_text = order.get('date_dushanbe') or "N/A"
        elif order.get('status_yiwu'):
            status_text = get_text('status_yiwu', lang)
            date_text = order.get('date_yiwu') or "N/A"
        else:
            status_text = "В обработке"
            date_text = "N/A"

        order_str = get_text('lk_order_item', lang).format(
            code=order['track_code'], status=status_text, date=date_text
        )
        if len(response) + len(order_str) > 4000:
            messages.append(response)
            response = ""
        response += order_str

    if response:
        messages.append(response)

    for i, msg in enumerate(messages):
        reply_markup = None
        if i == len(messages) - 1:
            btn = "✅ Я получил товар (в архив)"
            if lang == 'tg': btn = "✅ Тасдиқи қабул (ба архив)"
            elif lang == 'en': btn = "✅ I received the item (archive)"
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(btn, callback_data="archive_select")]])
        await target.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        await asyncio.sleep(0.15)

    return LK_MENU


async def lk_show_archive(update, context):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    target = update.message or update.callback_query.message

    orders = await get_archived_user_orders(user_id)

    if not orders:
        empty = "🗄 Ваш архив пуст."
        if lang == 'tg': empty = "🗄 Архиви шумо холӣ аст."
        elif lang == 'en': empty = "🗄 Your archive is empty."
        await target.reply_text(empty)
        return LK_MENU

    title = "<b>🗄 Ваш архив заказов:</b>"
    if lang == 'tg': title = "<b>🗄 Архиви фармоишҳои шумо:</b>"
    elif lang == 'en': title = "<b>🗄 Your Archived Orders:</b>"

    response = title + "\n\n"
    messages = []

    for order in orders:
        status_text = get_text('status_delivered', lang)
        date_text = order.get('date_delivered') or "N/A"
        order_str = get_text('lk_order_item', lang).format(
            code=order['track_code'], status=status_text, date=date_text
        )
        if len(response) + len(order_str) > 4000:
            messages.append(response)
            response = ""
        response += order_str

    if response:
        messages.append(response)

    for msg in messages:
        await target.reply_text(msg, parse_mode=ParseMode.HTML)
        await asyncio.sleep(0.15)

    return LK_MENU


async def archive_select_callback(update, context):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')

    orders = await get_user_orders(user_id)
    if not orders:
        await query.message.edit_text(get_text('lk_no_orders', lang))
        return LK_MENU

    prompt = "Выберите заказ, который вы получили:"
    if lang == 'tg': prompt = "Фармоишеро, ки қабул кардед, интихоб кунед:"
    elif lang == 'en': prompt = "Select the order you received:"

    keyboard = [[InlineKeyboardButton(f"📦 {o['track_code']}",
                                      callback_data=f"archive_order_{o['track_code']}")]
                for o in orders]
    keyboard.append([InlineKeyboardButton(get_text('cancel_button', lang),
                                          callback_data="delivery_cancel")])

    await query.message.edit_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard),
                                  parse_mode=ParseMode.HTML)
    return LK_MENU


async def archive_specific_order_callback(update, context):
    query = update.callback_query
    await query.answer()

    track_code = query.data.split('_', 2)[2]
    lang = context.user_data.get('lang', 'ru')

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    await mark_order_archived_by_code(track_code)

    success = f"✅ Заказ <b>{track_code}</b> перенесён в архив!"
    if lang == 'tg': success = f"✅ Фармоиши <b>{track_code}</b> ба архив интиқол ёфт!"
    elif lang == 'en': success = f"✅ Order <b>{track_code}</b> archived!"

    await query.message.reply_text(success, parse_mode=ParseMode.HTML)
    return await lk_show_orders(update, context)


async def lk_delivery_start(update, context):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')

    all_orders = await get_user_orders(user_id)
    target_statuses = ['в душанбе', 'душанбе', 'dushanbe']

    available = []
    for o in all_orders:
        s = o.get('status_dushanbe')
        in_dushanbe = s and s.strip().lower() in target_statuses
        requested = o.get('status_delivered') is not None
        if in_dushanbe and not requested:
            available.append(o)

    if not available:
        await update.message.reply_text(get_text('lk_delivery_no_orders', lang))
        return LK_MENU

    context.user_data['available_delivery_orders'] = available
    keyboard = []

    if len(available) > 1:
        keyboard.append([InlineKeyboardButton(
            get_text('lk_delivery_button_all', lang).format(count=len(available)),
            callback_data="delivery_select_ALL"
        )])

    for o in available:
        keyboard.append([InlineKeyboardButton(f"📦 {o['track_code']}",
                                              callback_data=f"delivery_select_{o['track_code']}")])

    keyboard.append([InlineKeyboardButton(get_text('cancel_button', lang),
                                          callback_data="delivery_cancel")])

    text = get_text('lk_delivery_select_order', lang)
    if len(available) > 1:
        codes_str = "\n".join([f"• <code>{o['track_code']}</code>" for o in available])
        text = get_text('lk_delivery_select_all_orders', lang).format(codes=codes_str)

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard),
                                    parse_mode=ParseMode.HTML)
    return LK_MENU


async def lk_select_delivery_order(update, context):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    code_str = query.data.split('_', 2)[2]

    if code_str == "ALL":
        available = context.user_data.get('available_delivery_orders', [])
        if not available:
            await query.message.edit_text(get_text('lk_delivery_no_orders', lang))
            return LK_MENU
        codes = [o['track_code'] for o in available]
        context.user_data['delivery_track_codes'] = codes
        prompt = get_text('order_delivery_prompt_all', lang)
    else:
        order = await get_order_by_track_code(code_str)
        if not order or order.get('status_delivered') is not None:
            await query.message.edit_text(get_text('error', lang))
            return LK_MENU
        context.user_data['delivery_track_codes'] = [code_str]
        prompt = get_text('order_delivery_prompt', lang).format(track_code=code_str)

    db_user = await get_user(user_id)
    saved_address = db_user.get('address') if db_user else None

    keyboard = []
    if saved_address:
        keyboard.append([InlineKeyboardButton(
            get_text('order_delivery_button_use_saved', lang).format(address=saved_address[:50]),
            callback_data="delivery_use_saved"
        )])
    keyboard.append([InlineKeyboardButton(get_text('order_delivery_button_new', lang),
                                          callback_data="delivery_use_new")])
    keyboard.append([InlineKeyboardButton(get_text('cancel_button', lang),
                                          callback_data="delivery_cancel")])

    await query.message.edit_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard),
                                  parse_mode=ParseMode.HTML)
    return LK_MENU


async def lk_delivery_use_saved(update, context):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')

    db_user = await get_user(user_id)
    saved_address = db_user.get('address') if db_user else None
    if not saved_address:
        await query.message.edit_text(get_text('lk_edit_address_prompt', lang).format(address="—"),
                                      parse_mode=ParseMode.HTML)
        return LK_AWAIT_DELIVERY_ADDRESS

    return await lk_save_delivery_request(update, context, saved_address)


async def lk_delivery_use_new(update, context):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')
    await query.message.edit_text(get_text('order_delivery_prompt_new', lang))
    return LK_AWAIT_DELIVERY_ADDRESS


async def lk_delivery_address_save(update, context):
    return await lk_save_delivery_request(update, context, update.message.text)


async def lk_save_delivery_request(update, context, address):
    user_id = (update.message or update.callback_query.message).chat_id
    if update.message:
        user_id = update.message.from_user.id
    else:
        user_id = update.callback_query.from_user.id
    lang = context.user_data.get('lang', 'ru')

    codes = context.user_data.get('delivery_track_codes')
    if not codes:
        target = update.message or update.callback_query.message
        await target.reply_text(get_text('error', lang))
        return LK_MENU

    success = await request_delivery_multiple(codes, address)
    codes_str = ", ".join([f"<code>{c}</code>" for c in codes])

    if success:
        logger.info(f"Delivery request for {codes_str} (user {user_id})")
        msg = get_text('order_delivery_request_sent', lang)
        if update.message:
            await update.message.reply_text(msg, reply_markup=get_lk_keyboard(lang, is_admin(user_id)))
        else:
            await update.callback_query.message.edit_text(msg)

        db_user = await get_user(user_id)
        username = f"@{db_user.get('username')}" if db_user and db_user.get('username') else "N/A"
        admin_msg = get_text('admin_notify_delivery_request', 'ru').format(
            full_name=db_user.get('full_name') if db_user else 'N/A',
            username=username,
            phone_number=db_user.get('phone_number') if db_user else 'N/A',
            track_codes=codes_str,
            address=address
        )
        await notify_admins(context.bot, admin_msg, parse_mode=ParseMode.HTML)
    else:
        err = get_text('error', lang)
        if update.message:
            await update.message.reply_text(err)
        else:
            await update.callback_query.message.edit_text(err)

    for k in ('delivery_track_code', 'available_delivery_orders', 'delivery_track_codes'):
        context.user_data.pop(k, None)
    return LK_MENU


async def lk_delivery_cancel(update, context):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')
    for k in ('delivery_track_code', 'available_delivery_orders', 'delivery_track_codes'):
        context.user_data.pop(k, None)

    await query.message.edit_text(get_text('admin_broadcast_cancelled', lang))
    await query.message.reply_text(
        get_text('lk_welcome_back', lang),
        reply_markup=get_lk_keyboard(lang, is_admin(update.effective_user.id))
    )
    return LK_MENU


async def lk_edit_address_start(update, context):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    db_user = await get_user(user_id)
    current = db_user.get('address') if db_user else None
    current = current or get_text('profile_address_not_set', lang)

    await query.message.reply_text(
        get_text('lk_edit_address_prompt', lang).format(address=current),
        reply_markup=get_cancel_keyboard(lang), parse_mode=ParseMode.HTML
    )
    return LK_AWAIT_PROFILE_ADDRESS


async def lk_edit_address_save(update, context):
    lang = context.user_data.get('lang', 'ru')
    user_id = update.effective_user.id
    new_address = update.message.text

    if new_address == get_text('cancel_button', lang):
        await update.message.reply_text(get_text('lk_welcome_back', lang),
                                        reply_markup=get_lk_keyboard(lang, is_admin(user_id)))
        return LK_MENU

    try:
        success = await update_user_address(user_id, new_address)
        if not success:
            raise Exception("update_user_address False")
        await update.message.reply_text(get_text('lk_edit_address_success', lang),
                                        reply_markup=get_lk_keyboard(lang, is_admin(user_id)))
    except Exception as e:
        logger.error(f"update address for {user_id}: {e}")
        await update.message.reply_text(get_text('lk_edit_error', lang))
    return LK_MENU


async def lk_edit_phone_start(update, context):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    db_user = await get_user(user_id)
    current = db_user.get('phone_number') if db_user else 'N/A'

    await query.message.reply_text(
        get_text('lk_edit_phone_prompt', lang).format(phone=current),
        reply_markup=get_cancel_keyboard(lang), parse_mode=ParseMode.HTML
    )
    return LK_AWAIT_PHONE


async def lk_edit_phone_save(update, context):
    lang = context.user_data.get('lang', 'ru')
    user_id = update.effective_user.id
    new_phone = update.message.text

    if new_phone == get_text('cancel_button', lang):
        await update.message.reply_text(get_text('lk_welcome_back', lang),
                                        reply_markup=get_lk_keyboard(lang, is_admin(user_id)))
        return LK_MENU

    if not re.match(r'^\+?\d{9,15}$', new_phone):
        await update.message.reply_text(get_text('registration_invalid_phone', lang),
                                        parse_mode=ParseMode.HTML)
        return LK_AWAIT_PHONE

    if not new_phone.startswith('+'):
        new_phone = '+' + new_phone

    try:
        success = await update_user_phone(user_id, new_phone)
        if not success:
            raise Exception("update_user_phone False")
        await update.message.reply_text(get_text('lk_edit_phone_success', lang),
                                        reply_markup=get_lk_keyboard(lang, is_admin(user_id)))
    except Exception as e:
        logger.error(f"update phone for {user_id}: {e}")
        await update.message.reply_text(get_text('lk_edit_error', lang))
    return LK_MENU


# =================================================================
# --- Админ-панель ---
# =================================================================

async def admin_show_stats(update, context):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    if not is_admin(user_id):
        return await lk_menu_start(update, context)
    count = await get_all_users_count()
    await update.message.reply_text(get_text('stats_message', lang).format(count=count))
    return LK_MENU


async def admin_download_excel(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return await lk_menu_start(update, context)

    await context.bot.send_chat_action(user_id, ChatAction.UPLOAD_DOCUMENT)

    try:
        path = str(XLSX_PATH)
        if not os.path.exists(path):
            await update.message.reply_text(f"Файл {XLSX_FILENAME} не найден.")
            return LK_MENU
        with open(path, 'rb') as doc:
            await context.bot.send_document(chat_id=user_id, document=doc, filename=XLSX_FILENAME)
    except Exception as e:
        logger.error(f"admin_download_excel: {e}")
        await update.message.reply_text(f"Не удалось отправить файл: {e}")
    return LK_MENU


async def admin_show_delivery_requests(update, context):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    if not is_admin(user_id):
        return await lk_menu_start(update, context)

    requests = await get_delivery_requests()
    if not requests:
        await update.message.reply_text(get_text('admin_delivery_requests_empty', lang))
        return LK_MENU

    await update.message.reply_text(get_text('admin_delivery_requests_title', lang),
                                    parse_mode=ParseMode.HTML)

    grouped = {}
    for req in requests:
        uid = req['user_id']
        if uid not in grouped:
            grouped[uid] = {
                'full_name': req['full_name'], 'phone_number': req['phone_number'],
                'address': req['address'], 'track_codes': []
            }
        grouped[uid]['track_codes'].append(req['track_code'])

    for uid, data in grouped.items():
        codes_str = ", ".join([f"<code>{c}</code>" for c in data['track_codes']])
        msg = get_text('admin_delivery_requests_item', 'ru').format(
            full_name=data['full_name'], user_id=uid,
            phone_number=data['phone_number'], address=data['address'],
            track_codes=codes_str
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(
            get_text('admin_delivery_button_confirm', 'ru').format(user_id=uid),
            callback_data=f"admin_confirm_{uid}"
        )]])
        await update.message.reply_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    return LK_MENU


async def admin_confirm_delivery_callback(update, context):
    query = update.callback_query
    await query.answer()

    admin_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')

    try:
        client_user_id = int(query.data.split('_')[2])
        requests = await get_delivery_requests()
        codes = [r['track_code'] for r in requests if r['user_id'] == client_user_id]

        if not codes:
            await query.message.reply_text(
                f"Не найдено заказов (ID: {client_user_id}). Возможно, уже подтверждено."
            )
            return LK_MENU

        confirmed = await confirm_delivery(codes)
        if not confirmed:
            await query.message.reply_text(
                f"Не найдено заказов (ID: {client_user_id}). Возможно, уже подтверждено."
            )
            return LK_MENU

        codes_str = ", ".join(confirmed)
        client = await get_user(client_user_id)
        client_name = client['full_name'] if client else f"ID {client_user_id}"
        client_lang = client['language_code'] if client else 'ru'

        await query.message.reply_text(
            get_text('admin_delivery_confirm_success', lang).format(
                full_name=client_name, track_codes=codes_str
            )
        )
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        try:
            title = get_text('user_notify_delivered_title', client_lang)
            body = get_text('user_notify_delivered_body', client_lang).format(
                track_codes="\n".join([f"• <code>{c}</code>" for c in confirmed])
            )
            await context.bot.send_message(
                client_user_id, f"<b>{title}</b>\n\n{body}", parse_mode=ParseMode.HTML
            )
        except Forbidden:
            logger.warning(f"Cannot notify client {client_user_id}: blocked.")
        except Exception as e:
            logger.error(f"Notify client {client_user_id}: {e}")

    except Exception as e:
        logger.error(f"admin_confirm_delivery: {e}", exc_info=True)
        await query.message.reply_text(get_text('admin_delivery_confirm_fail', lang))
    return LK_MENU


async def admin_show_delivered_list(update, context):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    if not is_admin(user_id):
        return await lk_menu_start(update, context)

    page = context.user_data.get('delivered_page', 1)
    limit = 50
    offset = (page - 1) * limit

    orders = await get_delivered_orders_paginated(page, limit)
    total = await get_delivered_orders_count()

    if not orders:
        await update.message.reply_text(get_text('admin_delivered_list_empty', lang))
        return LK_MENU

    response = f"{get_text('admin_delivered_list_title', lang)}\nСтраница {page} (всего: {total})\n\n"
    for o in orders:
        try:
            d = o['date_delivered']
            date_str = d.strftime('%Y-%m-%d') if isinstance(d, datetime) else str(d or 'N/A')
        except Exception:
            date_str = str(o.get('date_delivered') or 'N/A')
        response += get_text('admin_delivered_item', 'ru').format(
            code=o['track_code'], full_name=o.get('full_name') or 'N/A', date=date_str
        )

    kb = []
    if page > 1:
        kb.append(InlineKeyboardButton("⬅️ Предыдущая", callback_data=f"delivered_page_{page - 1}"))
    if offset + limit < total:
        kb.append(InlineKeyboardButton("Следующая ➡️", callback_data=f"delivered_page_{page + 1}"))

    markup = InlineKeyboardMarkup([kb]) if kb else None
    await update.message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=markup)
    return LK_MENU


async def delivered_page_callback(update, context):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split('_')[2])
    context.user_data['delivered_page'] = page

    class _FakeMsg:
        def __init__(self, msg):
            self.message = msg
            self.effective_user = update.effective_user
            self.effective_chat = msg.chat

        async def reply_text(self, *a, **kw):
            return await query.message.reply_text(*a, **kw)

    # Просто переотправляем список. admin_show_delivered_list ожидает update.message.
    # Эмулируем это, вызывая с update.callback_query.message.
    fake = type("F", (), {
        "message": query.message,
        "effective_user": update.effective_user,
        "effective_chat": query.message.chat,
    })()
    return await admin_show_delivered_list(fake, context)


async def admin_broadcast_start(update, context):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    if not is_admin(user_id):
        return await lk_menu_start(update, context)
    await update.message.reply_text(get_text('admin_broadcast_prompt', lang),
                                    reply_markup=get_cancel_keyboard(lang))
    return AWAITING_BROADCAST_MESSAGE


async def admin_broadcast_confirm(update, context):
    context.user_data['broadcast_message'] = update.message
    await update.message.reply_text("Предпросмотр:")
    await context.bot.copy_message(
        chat_id=update.effective_chat.id,
        from_chat_id=update.effective_chat.id,
        message_id=update.message.message_id
    )
    keyboard = ReplyKeyboardMarkup([["Да, отправить"], ["Нет, отменить"]], resize_keyboard=True)
    await update.message.reply_text("Отправляем?", reply_markup=keyboard)
    return CONFIRM_BROADCAST


async def admin_broadcast_send(update, context):
    lang = context.user_data.get('lang', 'ru')
    admin_id = update.effective_user.id
    msg = context.user_data.get('broadcast_message')

    if not msg:
        await update.message.reply_text("Ошибка: сообщение не найдено.")
        return await lk_menu_start(update, context)

    await update.message.reply_text("Начинаю рассылку...",
                                    reply_markup=get_lk_keyboard(lang, is_admin(admin_id)))

    user_ids = await get_all_user_ids()
    success = failed = 0
    for uid in user_ids:
        if uid == admin_id:
            continue
        try:
            await context.bot.copy_message(chat_id=uid, from_chat_id=msg.chat_id,
                                           message_id=msg.message_id)
            success += 1
        except Forbidden:
            failed += 1
        except Exception as e:
            failed += 1
            logger.error(f"Broadcast to {uid}: {e}")
        await asyncio.sleep(0.05)

    await update.message.reply_text(get_text('admin_broadcast_report', lang).format(
        success=success, failed=failed
    ))
    context.user_data.pop('broadcast_message', None)
    return LK_MENU


async def admin_broadcast_cancel(update, context):
    lang = context.user_data.get('lang', 'ru')
    context.user_data.pop('broadcast_message', None)
    await update.message.reply_text(get_text('admin_broadcast_cancelled', lang),
                                    reply_markup=get_lk_keyboard(lang,
                                                                 is_admin(update.effective_user.id)))
    return LK_MENU


async def admin_mark_delivered(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    try:
        track_code = context.args[0].upper()
    except (IndexError, AttributeError):
        await update.message.reply_text("Использование: /delivered <code>")
        return

    order = await get_order_by_track_code(track_code)
    if not order:
        await update.message.reply_text(f"❌ Заказ {track_code} не найден.")
        return

    success = await mark_order_delivered_by_code(track_code)
    if success:
        await update.message.reply_text(f"✅ Заказ {track_code} отмечен как 'Доставлен'.")
        client_id = order.get('user_id')
        if client_id:
            try:
                client = await get_user(client_id)
                client_lang = client['language_code'] if client else 'ru'
                title = get_text('user_notify_delivered_title', client_lang)
                body = get_text('user_notify_delivered_body', client_lang).format(
                    track_codes=f"• <code>{track_code}</code>"
                )
                await context.bot.send_message(client_id, f"<b>{title}</b>\n\n{body}",
                                               parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.warning(f"notify client on /delivered: {e}")
    else:
        await update.message.reply_text(f"❌ Не удалось обновить {track_code}.")


# =================================================================
# --- Общие: картинки / invalid / error ---
# =================================================================

async def image_handler(update, context):
    lang = context.user_data.get('lang', 'ru')
    await update.message.reply_text(get_text('image_received', lang))


async def invalid_input(update, context):
    lang = context.user_data.get('lang', 'ru')
    user_id = update.effective_user.id
    await update.message.reply_text(get_text('invalid_input', lang),
                                    reply_markup=get_main_keyboard(lang, is_admin(user_id)))
    return MAIN_MENU


async def error_handler(update, context):
    logger.error(f"Update caused error: {context.error}", exc_info=context.error)
    if update and update.effective_message:
        try:
            lang = context.user_data.get('lang', 'ru') if context.user_data else 'ru'
            await update.effective_message.reply_text(get_text('error', lang))
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")


# =================================================================
# --- Admin add/update order (ConversationHandler) ---
# =================================================================

async def admin_add_order_start(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return ConversationHandler.END

    context.user_data.pop('admin_order_data', None)
    await update.message.reply_text(
        "Режим <b>Добавить/Обновить Заказ</b>.\n\n"
        "<b>Шаг 1/4:</b> Введите <b>Трек-код</b> (или /cancel):",
        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove()
    )
    return ADMIN_AWAIT_ORDER_CODE


async def admin_add_order_get_code(update, context):
    track_code = update.message.text.strip().upper()
    if not track_code:
        await update.message.reply_text("Трек-код не может быть пустым.")
        return ADMIN_AWAIT_ORDER_CODE

    context.user_data['admin_order_data'] = {'track_code': track_code}
    existing = await get_order_by_track_code(track_code)

    if existing:
        cur = existing.get('status_delivered') or existing.get('status_dushanbe') or existing.get('status_yiwu') or 'N/A'
        await update.message.reply_text(
            f"Заказ <code>{track_code}</code> <b>НАЙДЕН</b> (обновление).\n"
            f"Текущий статус: {cur}\n"
            f"Владелец: {existing.get('user_id') or 'N/A'}\n\n"
            "<b>Шаг 2/4:</b> Введите <b>НОВЫЙ статус</b> (Yiwu, Dushanbe, Delivered):",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            f"Заказ <code>{track_code}</code> <b>НЕ НАЙДЕН</b> (создание).\n\n"
            "<b>Шаг 2/4:</b> Введите <b>статус</b> (Yiwu, Dushanbe):",
            parse_mode=ParseMode.HTML
        )
    return ADMIN_AWAIT_ORDER_STATUS


async def admin_add_order_get_status(update, context):
    context.user_data['admin_order_data']['status'] = update.message.text.strip().capitalize()
    await update.message.reply_text(
        "<b>Шаг 3/4:</b> <b>Дата Иу</b> (ГГГГ-ММ-ДД, 0 или /skip — пусто):",
        parse_mode=ParseMode.HTML
    )
    return ADMIN_AWAIT_ORDER_DATE_YIWU


async def admin_add_order_get_date_yiwu(update, context):
    d = update.message.text.strip()
    context.user_data['admin_order_data']['date_yiwu'] = None if d in ('0', '/skip') else d
    await update.message.reply_text(
        "<b>Шаг 4/4:</b> <b>Дата Душанбе</b> (ГГГГ-ММ-ДД, 0 или /skip — пусто):",
        parse_mode=ParseMode.HTML
    )
    return ADMIN_AWAIT_ORDER_DATE_DUSH


async def admin_add_order_get_date_dush_and_save(update, context):
    lang = context.user_data.get('lang', 'ru')
    d = update.message.text.strip()
    data = context.user_data.pop('admin_order_data')
    data['date_dushanbe'] = None if d in ('0', '/skip') else d

    existing = await get_order_by_track_code(data['track_code'])
    data['owner_id'] = existing.get('user_id') if existing else None

    try:
        success = await admin_upsert_order(**data)
        if success:
            await update.message.reply_text(
                f"✅ Заказ <code>{data['track_code']}</code> сохранён.\n"
                f"Статус: {data['status']}\n"
                f"Владелец: {data['owner_id'] or 'Будет привязан при поиске'}",
                parse_mode=ParseMode.HTML,
                reply_markup=get_lk_keyboard(lang, True)
            )
        else:
            raise Exception("admin_upsert_order False")
    except Exception as e:
        logger.error(f"admin_add_order save: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Не удалось сохранить <code>{data['track_code']}</code>.",
            parse_mode=ParseMode.HTML, reply_markup=get_lk_keyboard(lang, True)
        )
    return LK_MENU


async def admin_add_order_cancel(update, context):
    context.user_data.pop('admin_order_data', None)
    lang = context.user_data.get('lang', 'ru')
    await update.message.reply_text(
        "Действие отменено.",
        reply_markup=get_lk_keyboard(lang, is_admin(update.effective_user.id))
    )
    return LK_MENU


# =================================================================
# --- Excel import ---
# =================================================================

def _read_excel_sync(file_path):
    try:
        return pd.read_excel(file_path, header=0, dtype=str)
    except Exception:
        return pd.read_csv(file_path, header=0, dtype=str, sep=None, engine='python')


def parse_date_safe(date_str):
    if not date_str or str(date_str).lower() in ['nan', 'nat', 'none', '', '0', 'null']:
        return None
    try:
        clean = str(date_str).strip().split(" ")[0]
        dt = pd.to_datetime(clean, dayfirst=True, errors='coerce')
        return dt.date() if pd.notna(dt) else None
    except Exception:
        return None


async def process_excel_to_db(file_path):
    """Строгий парсер: [Трек, Дата Иу, Статус Иу, Дата Душанбе, Статус Душанбе]"""
    stats = {'total': 0, 'updated': 0, 'failed': 0, 'linked': 0}
    try:
        logger.info(f"--- НАЧАЛО ИМПОРТА: {file_path} ---")
        try:
            df = await asyncio.to_thread(_read_excel_sync, file_path)
        except Exception as e:
            return {'error': f'Ошибка чтения файла: {e}'}

        df = df.dropna(how='all')
        if len(df.columns) < 2:
            return {'error': 'Слишком мало колонок в файле.'}

        logger.info(f"Колонки: {list(df.columns)}")
        excel_data = []

        for _, row in df.iterrows():
            raw = row.iloc[0]
            if pd.isna(raw) or str(raw).strip() == '':
                continue
            track_code = str(raw).strip().upper()
            if len(track_code) < 3:
                continue

            date_yiwu = parse_date_safe(row.iloc[1]) if len(df.columns) > 1 else None
            status_yiwu = "Иу"
            if len(df.columns) > 2 and pd.notna(row.iloc[2]):
                v = str(row.iloc[2]).strip()
                if v:
                    status_yiwu = v

            date_dushanbe = parse_date_safe(row.iloc[3]) if len(df.columns) > 3 else None
            status_dushanbe = None
            status_delivered = None
            date_delivered = None

            if len(df.columns) > 4 and pd.notna(row.iloc[4]):
                val = str(row.iloc[4]).strip()
                low = val.lower()
                if val:
                    if any(x in low for x in ['доставлен', 'выдан', 'delivered']):
                        status_delivered = "Доставлен"
                        date_delivered = date_dushanbe
                        status_dushanbe = "Душанбе"
                    elif any(x in low for x in ['душанбе', 'прибыл', 'dushanbe']):
                        status_dushanbe = "Душанбе"
                    else:
                        status_dushanbe = val

            if date_dushanbe and not status_dushanbe:
                status_dushanbe = "Душанбе"

            excel_data.append({
                'track_code': track_code,
                'status_yiwu': status_yiwu, 'date_yiwu': date_yiwu,
                'status_dushanbe': status_dushanbe, 'date_dushanbe': date_dushanbe,
                'status_delivered': status_delivered, 'date_delivered': date_delivered,
            })

    except Exception as e:
        logger.error(f"Ошибка Excel: {e}", exc_info=True)
        return {'error': str(e)}

    stats['total'] = len(excel_data)
    for row in excel_data:
        try:
            res = await upsert_order_from_excel(**row)
            if res:
                stats['updated'] += 1
                if res.get('was_unlinked'):
                    stats['linked'] += 1
            else:
                stats['failed'] += 1
        except Exception as e:
            stats['failed'] += 1
            logger.error(f"DB upsert {row.get('track_code')}: {e}")

    logger.info(f"--- ИТОГ: {stats} ---")
    return stats


async def document_handler(update, context):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        logger.warning(f"Не-админ {user_id} попытался загрузить файл.")
        return

    doc = update.message.document
    if not doc.file_name or not doc.file_name.lower().endswith(('.xlsx', '.xls', '.csv')):
        await update.message.reply_text(
            "Это не похоже на Excel/CSV. Нужен .xlsx, .xls или .csv."
        )
        return

    temp_filename = f"temp_upload_{uuid.uuid4()}{os.path.splitext(doc.file_name)[1]}"
    await update.message.reply_text("Файл получен. Обрабатываю...")

    try:
        file = await doc.get_file()
        await file.download_to_drive(temp_filename)
        await update.message.reply_text(
            "✅ Файл сохранён. Импорт: Трек | Дата Иу | Статус Иу | Дата Душ | Статус Душ..."
        )
        stats = await process_excel_to_db(temp_filename)
        if 'error' in stats:
            await update.message.reply_text(
                f"❌ <b>Ошибка:</b>\n<code>{stats['error']}</code>",
                parse_mode=ParseMode.HTML
            )
        else:
            report = (
                f"<b>✅ Импорт завершён:</b>\n\n"
                f"<b>Всего:</b> {stats.get('total', 0)}\n"
                f"<b>Обновлено:</b> {stats.get('updated', 0)}\n"
                f"<b>Привязано:</b> {stats.get('linked', 0)}\n"
                f"<b>Ошибок:</b> {stats.get('failed', 0)}"
            )
            await update.message.reply_text(report, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"document_handler: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Критическая ошибка: {e}")
    finally:
        try:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        except Exception:
            pass


# =================================================================
# --- Conversation handlers ---
# =================================================================

def get_main_conv_handler():
    lang_filter = filters.TEXT & (~filters.COMMAND)

    # main_buttons regex
    def btn_regex(i, j):
        return f"^({re.escape(TEXTS['ru']['main_buttons'][i][j])}|" \
               f"{re.escape(TEXTS['tg']['main_buttons'][i][j])}|" \
               f"{re.escape(TEXTS['en']['main_buttons'][i][j])})$"

    def lk_btn_regex(i, j):
        return f"^({re.escape(TEXTS['ru']['lk_menu_buttons'][i][j])}|" \
               f"{re.escape(TEXTS['tg']['lk_menu_buttons'][i][j])}|" \
               f"{re.escape(TEXTS['en']['lk_menu_buttons'][i][j])})$"

    entry_points = [
        CommandHandler("start", start),
        CommandHandler("help", show_help),
        CallbackQueryHandler(select_language, pattern='^lang_'),
        CallbackQueryHandler(process_subscription_check, pattern='^check_subscription$'),
        CallbackQueryHandler(show_address_callback, pattern='^address_'),
        CallbackQueryHandler(change_language_callback, pattern='^set_lang_'),
        CallbackQueryHandler(lk_edit_address_start, pattern='^lk_edit_address$'),
        CallbackQueryHandler(lk_edit_phone_start, pattern='^lk_edit_phone$'),
        CallbackQueryHandler(lk_select_delivery_order, pattern='^delivery_select_'),
        CallbackQueryHandler(lk_delivery_use_saved, pattern='^delivery_use_saved$'),
        CallbackQueryHandler(lk_delivery_use_new, pattern='^delivery_use_new$'),
        CallbackQueryHandler(lk_delivery_cancel, pattern='^delivery_cancel$'),
        CallbackQueryHandler(admin_confirm_delivery_callback, pattern='^admin_confirm_'),
        CallbackQueryHandler(delivered_page_callback, pattern='^delivered_page_'),
        CallbackQueryHandler(link_order_callback, pattern='^link_'),
        CallbackQueryHandler(archive_select_callback, pattern='^archive_select$'),
        CallbackQueryHandler(archive_specific_order_callback, pattern='^archive_order_'),
    ]

    states = {
        AWAITING_LANG_CHOICE: [CallbackQueryHandler(select_language, pattern='^lang_')],
        AWAITING_SUBSCRIPTION: [CallbackQueryHandler(process_subscription_check, pattern='^check_subscription$')],

        AWAITING_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
        AWAITING_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), register_phone)],
        AWAITING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_address)],

        MAIN_MENU: [
            MessageHandler(lang_filter & filters.Regex(btn_regex(0, 0)), track_order_start),
            MessageHandler(lang_filter & filters.Regex(btn_regex(0, 1)), lk_menu_start),
            MessageHandler(lang_filter & filters.Regex(btn_regex(1, 0)), show_contacts),
            MessageHandler(lang_filter & filters.Regex(btn_regex(1, 1)), show_prices),
            MessageHandler(lang_filter & filters.Regex(btn_regex(2, 0)), show_forbidden),
            MessageHandler(lang_filter & filters.Regex(btn_regex(2, 1)), show_address_menu),
            MessageHandler(lang_filter & filters.Regex(btn_regex(3, 0)), change_language_start),

            CallbackQueryHandler(show_address_callback, pattern='^address_'),
            CallbackQueryHandler(change_language_callback, pattern='^set_lang_'),
            CallbackQueryHandler(link_order_callback, pattern='^link_'),
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_track_code),
        ],

        AWAITING_TRACK_CODE: [
            MessageHandler(filters.TEXT & filters.Regex(
                f"^({re.escape(TEXTS['ru']['cancel_button'])}|"
                f"{re.escape(TEXTS['tg']['cancel_button'])}|"
                f"{re.escape(TEXTS['en']['cancel_button'])})$"
            ), lk_back_to_main),
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_track_code),
        ],

        LK_MENU: [
            MessageHandler(lang_filter & filters.Regex(lk_btn_regex(2, 0)), lk_back_to_main),
            MessageHandler(lang_filter & filters.Regex(lk_btn_regex(0, 0)), lk_show_orders),
            MessageHandler(lang_filter & filters.Regex(lk_btn_regex(0, 1)), lk_show_profile),
            MessageHandler(lang_filter & filters.Regex(lk_btn_regex(1, 0)), lk_delivery_start),
            MessageHandler(lang_filter & filters.Regex(lk_btn_regex(1, 1)), lk_show_archive),

            MessageHandler(lang_filter & filters.Regex(REGEX_DELIVERY_REQUESTS), admin_show_delivery_requests),
            MessageHandler(lang_filter & filters.Regex(REGEX_DELIVERED_LIST), admin_show_delivered_list),
            MessageHandler(lang_filter & filters.Regex(REGEX_STATS), admin_show_stats),
            MessageHandler(lang_filter & filters.Regex(REGEX_BROADCAST), admin_broadcast_start),
            MessageHandler(lang_filter & filters.Regex(REGEX_DOWNLOAD_EXCEL), admin_download_excel),
            MessageHandler(lang_filter & filters.Regex(REGEX_ADMIN_PROFILE), lk_show_profile),

            CallbackQueryHandler(lk_edit_address_start, pattern='^lk_edit_address$'),
            CallbackQueryHandler(lk_edit_phone_start, pattern='^lk_edit_phone$'),
            CallbackQueryHandler(lk_select_delivery_order, pattern='^delivery_select_'),
            CallbackQueryHandler(lk_delivery_use_saved, pattern='^delivery_use_saved$'),
            CallbackQueryHandler(lk_delivery_use_new, pattern='^delivery_use_new$'),
            CallbackQueryHandler(lk_delivery_cancel, pattern='^delivery_cancel$'),
            CallbackQueryHandler(admin_confirm_delivery_callback, pattern='^admin_confirm_'),
            CallbackQueryHandler(delivered_page_callback, pattern='^delivered_page_'),
            CallbackQueryHandler(archive_select_callback, pattern='^archive_select$'),
            CallbackQueryHandler(archive_specific_order_callback, pattern='^archive_order_'),

            # AWAITING_BROADCAST_MESSAGE (вход)
            MessageHandler(lang_filter & filters.Regex(REGEX_BROADCAST), admin_broadcast_start),

            MessageHandler(filters.TEXT & ~filters.COMMAND, invalid_input),
        ],

        AWAITING_BROADCAST_MESSAGE: [
            CommandHandler("cancel", admin_broadcast_cancel),
            MessageHandler(filters.TEXT & filters.Regex(
                f"^({re.escape(TEXTS['ru']['cancel_button'])}|"
                f"{re.escape(TEXTS['tg']['cancel_button'])}|"
                f"{re.escape(TEXTS['en']['cancel_button'])})$"
            ), admin_broadcast_cancel),
            MessageHandler(filters.ALL & ~filters.COMMAND, admin_broadcast_confirm),
        ],
        CONFIRM_BROADCAST: [
            MessageHandler(filters.Regex("^Да, отправить$"), admin_broadcast_send),
            MessageHandler(filters.Regex("^Нет, отменить$"), admin_broadcast_cancel),
            CommandHandler("cancel", admin_broadcast_cancel),
        ],

        LK_AWAIT_DELIVERY_ADDRESS: [
            MessageHandler(filters.TEXT & filters.Regex(
                f"^({re.escape(TEXTS['ru']['cancel_button'])}|"
                f"{re.escape(TEXTS['tg']['cancel_button'])}|"
                f"{re.escape(TEXTS['en']['cancel_button'])})$"
            ), lk_menu_start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, lk_delivery_address_save),
        ],
        LK_AWAIT_PROFILE_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, lk_edit_address_save)],
        LK_AWAIT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, lk_edit_phone_save)],

        ADMIN_AWAIT_ORDER_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_order_get_code)],
        ADMIN_AWAIT_ORDER_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_order_get_status)],
        ADMIN_AWAIT_ORDER_DATE_YIWU: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_order_get_date_yiwu)],
        ADMIN_AWAIT_ORDER_DATE_DUSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_order_get_date_dush_and_save)],
    }

    return ConversationHandler(
        entry_points=entry_points,
        states=states,
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("help", show_help),
            CommandHandler("cancel", admin_add_order_cancel),
            CommandHandler("addorder", admin_add_order_start),
        ],
        persistent=True,
        name="dc_main_conversation",
        per_message=False,
    )
