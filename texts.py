# -*- coding: utf-8 -*-
# DC Cargo — texts.py (RU / TG / EN)
from config import XLSX_FILENAME

CONTACT_PHONE_DISPLAY = "+992 11 155 53 95"
CONTACT_PHONE_TEL = "+992111555395"
OPERATOR_LINK = "t.me/SALVATORZODA"
INSTAGRAM_LINK = "https://instagram.com/dc_cargo1"
INSTAGRAM_HANDLE = "dc_cargo1"
TELEGRAM_CHANNEL_LINK = "https://t.me/dc_cargo1"

_CHINA_ADDRESS_RU = (
    "🏭 <b>Адрес в Китае:</b>\n\n"
    "收货人: Dc_cargo\n"
    "手机号: <code>15267402525</code>\n"
    "地址: <code>浙江省义乌市后宅街道洪华小区88栋5单元仓库2号门</code>\n\n"
    "☝️ Укажите ваше ФИО и номер телефона (латиницей)."
)
_CHINA_ADDRESS_TG = (
    "🏭 <b>Суроға дар Хитой:</b>\n\n"
    "收货人: Dc_cargo\n"
    "手机号: <code>15267402525</code>\n"
    "地址: <code>浙江省义乌市后宅街道洪华小区88栋5单元仓库2号门</code>\n\n"
    "☝️ Ном ва рақами телефон (бо ҳарфҳои лотинӣ)-ро нишон диҳед."
)
_CHINA_ADDRESS_EN = (
    "🏭 <b>Address in China:</b>\n\n"
    "收货人: Dc_cargo\n"
    "手机号: <code>15267402525</code>\n"
    "地址: <code>浙江省义乌市后宅街道洪华小区88栋5单元仓库2号门</code>\n\n"
    "☝️ Provide your full name and phone number (in Latin)."
)

_TJ_CONTACT_RU = (
    "📍 <b>Наш адрес в Душанбе:</b>\n"
    "г. Душанбе, улица Собира Абдуллоева, 28\n"
    "<i>Ориентир: напротив Бозори Чал-Чам — Кухна</i>\n\n"
    f"📞 Телефон: <code>{CONTACT_PHONE_DISPLAY}</code>\n"
    f"💬 Оператор: {OPERATOR_LINK}\n\n"
    "Свяжитесь с оператором, чтобы уточнить время и место выдачи."
)
_TJ_CONTACT_TG = (
    "📍 <b>Суроғаи мо дар Душанбе:</b>\n"
    "ш. Душанбе, кӯчаи Собир Абдуллоев, 28\n"
    "<i>Ориентир: рӯ ба рӯи Бозори Чал-Чам — Кӯҳна</i>\n\n"
    f"📞 Телефон: <code>{CONTACT_PHONE_DISPLAY}</code>\n"
    f"💬 Оператор: {OPERATOR_LINK}\n\n"
    "Барои донистани вақт ва маҳали супурдани бор бо оператор тамос гиред."
)
_TJ_CONTACT_EN = (
    "📍 <b>Our address in Dushanbe:</b>\n"
    "Dushanbe, Sobir Abdulloev street, 28\n"
    "<i>Landmark: opposite Chal-Cham Kuhna bazaar</i>\n\n"
    f"📞 Phone: <code>{CONTACT_PHONE_DISPLAY}</code>\n"
    f"💬 Operator: {OPERATOR_LINK}\n\n"
    "Contact the operator to arrange pick-up time and place."
)


TEXTS = {
    "ru": {
        "welcome": "Привет {name}, рад что Вы с нами. Пожалуйста, выберите язык.",
        "welcome_back": "С возвращением, {name}!",
        "language_selected": "Язык установлен: Русский",
        "invalid_input": "Пожалуйста, используйте кнопки меню или введите трек-код.",
        "select_action": "Выберите действие:",
        "track_code_prompt": "Введите ваш трек-код:",

        "track_code_found_yiwu": (
            "Ассалому алейкум!\n"
            "✅ Ваш груз с трек-кодом <b>{code}</b> принят на складе DC Cargo в г. Иу.\n"
            "🗓️ <b>Дата приёма:</b> {date}\n"
            "⏳ Срок доставки: 12-20 дней. Постараемся доставить Ваш груз раньше срока.\n\n"
            "✨ DC Cargo! Надёжное, быстрое карго по доступной цене."
        ),
        "track_code_found_dushanbe": (
            "Ассалому алейкум!\n"
            "🚚 Ваш груз с трек-кодом <b>{code}</b> прибыл на склад DC Cargo в г. Душанбе!\n"
            "🗓️ <b>Дата прибытия:</b> {date}\n\n"
            f"📞 Пожалуйста, свяжитесь с нами для получения: <code>{CONTACT_PHONE_DISPLAY}</code>.\n\n"
            "✨ DC Cargo! Надёжное, быстрое карго по доступной цене."
        ),
        "track_code_not_found": "❌ Ваш груз пока не поступил на склад DC Cargo в г. Иу.",
        "track_code_found_other": (
            "ℹ️ Статус вашего заказа <b>{code}</b>:\n"
            "<b>{status}</b>"
        ),

        "track_codes_not_loaded": "⚠️ Проблема с загрузкой трек-кодов. Обратитесь к администратору.",
        "file_received": "Файл получен. Обрабатываю...",
        "file_wrong_name": f"⚠️ Пожалуйста, отправьте файл с точным именем: {XLSX_FILENAME}",
        "file_upload_forbidden": "⛔ У вас нет прав на загрузку файла.",
        "file_upload_success": f"✅ Файл {XLSX_FILENAME} успешно обновлён!\nЗагружено трек-кодов: {{count}}.",
        "file_download_error": "❌ Не удалось скачать или обработать файл.",
        "job_reload_success": "Автоматическое обновление трек-кодов из {filename} прошло успешно. Загружено: {count}.",
        "job_reload_fail": "⚠️ Ошибка при автоматическом обновлении трек-кодов из {filename}. Проверьте логи.",
        "admin_notify_initial_load_fail": f"⚠️ КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить трек-коды из {XLSX_FILENAME}!",
        "admin_notify_photo_not_found": "⚠️ Ошибка: Не найден файл фото '{photo_path}'.",
        "dushanbe_arrival_notification": (
            "🚚 Уважаемый клиент!\n"
            "Ваш груз с трек-кодом '{code}' прибыл на склад DC Cargo в г. Душанбе!\n"
            f"📞 Пожалуйста, свяжитесь с нами: {CONTACT_PHONE_DISPLAY}."
        ),
        "contacts": (
            "<b>DC Cargo</b>\n"
            "Режим работы: с 9:00 до 18:00\n"
            "Перерыв: с 12:00 до 13:00\n\n"
            f"💬 Оператор: {OPERATOR_LINK}\n"
            f"📸 Instagram: <a href=\"{INSTAGRAM_LINK}\">@{INSTAGRAM_HANDLE}</a>\n"
            f"📢 Telegram-канал: {TELEGRAM_CHANNEL_LINK}"
        ),
        "prices_text": (
            "<b>Наши тарифы</b>\n\n"
            "🇨🇳 Иу — Душанбе 🇹🇯\n"
            "Срок доставки: 12-20 дней\n\n"
            "🚚 От 1 до 30 кг: <b>2.5$</b>\n"
            "🚚 От 30 до 50 кг: <b>2.3$</b>\n"
            "🚚 От 50 кг и выше: <b>2.0$</b>\n"
            "📦 За 1 куб: <b>250$</b>\n\n"
            "⚠️ Крупногабаритные грузы рассчитываются по кубам.\n\n"
            "💼 <b>От 200 кг — цена договорная.</b>\n"
            "Возможна скидка или индивидуальные условия.\n"
            f"✍️ Напишите нам в Direct: <a href=\"{INSTAGRAM_LINK}\">@{INSTAGRAM_HANDLE}</a> "
            f"или оператору: {OPERATOR_LINK}"
        ),
        "forbidden_text": (
            "<b>Запрещённые товары:</b>\n"
            "1. Лекарства (порошок, таблетки, жидкие препараты)\n"
            "2. Все виды жидкостей (парфюм, ароматизаторы и т.д.)\n"
            "3. Все виды холодного оружия (ножи, электрошокеры, дубинки и т.д.)\n"
            "4. Электронные сигареты, кальяны и т.д. — не принимаются."
        ),
        "address_text": "Выберите адрес:",
        "button_china": "🏭 Адрес в Китае",
        "button_tajikistan": "🇹🇯 Получение в Душанбе",
        "address_caption_china": _CHINA_ADDRESS_RU,
        "address_caption_tajikistan": _TJ_CONTACT_RU,
        "image_received": "Изображение получено. Пока я не обрабатываю изображения, но могу помочь с другим! 😊",
        "error": "Произошла ошибка. Попробуйте снова или начните с /start.",
        "photo_address_error": "Не удалось отправить фото. Вот адрес:\n{address}",
        "photo_contact_error": "Не удалось отправить фото. Вот контакты:\n{contacts}",
        "photo_price_error": "Не удалось отправить фото. Вот тарифы:\n{price_list}",
        "stats_forbidden": "⛔ Эта команда доступна только администраторам.",
        "stats_message": "📊 Статистика бота:\nВсего уникальных пользователей: {count}",
        "admin_broadcast_prompt": "Введите сообщение для рассылки. Для отмены /cancel.",
        "admin_broadcast_confirm_prompt": "Отправить это сообщение? (Да, отправить / Нет, отменить)\n\n{message}",
        "admin_broadcast_cancelled": "Рассылка отменена.",
        "admin_broadcast_report": "✅ Рассылка завершена.\nОтправлено: {success}\nНе удалось: {failed}",
        "help_message": (
            "👋 Здравствуйте! Я бот DC Cargo.\n\n"
            "🔍 <b>Отследить трек-код</b> — статус груза.\n"
            "👤 <b>Личный кабинет</b> — ваши заказы и профиль.\n"
            "📞 <b>Контакты</b>, 📊 <b>Тарифы</b>, ❌ <b>Запрещённые</b>, 📍 <b>Адрес</b>, 🌐 <b>Язык</b>.\n\n"
            "Для сброса диалога: /start."
        ),

        "subscribe_prompt": "Чтобы продолжить, подпишитесь на канал:",
        "subscribe_button_channel": "DC Cargo",
        "subscribe_button_check": "Я подписался ✅",
        "checking_button": "Проверка...",
        "subscribe_fail": "Вы не подписаны. Подпишитесь и нажмите 'Проверить'.",
        "subscription_success": "Спасибо за подписку! ✅",

        "registration_start": "Давайте начнём регистрацию.",
        "registration_prompt_name": "Пожалуйста, отправьте ваше ФИО (например: Иванов Иван Иванович):",
        "registration_invalid_name": "❌ Неверный формат. Введите хотя бы два слова (Имя и Фамилию).",
        "registration_prompt_phone": "Отлично, {full_name}.\nТеперь поделитесь номером телефона (кнопка ниже) или введите вручную в формате <code>+992XXXXXXXXX</code>:",
        "registration_invalid_phone": "❌ Неверный формат. Номер должен быть в формате <code>+992XXXXXXXXX</code>.",
        "registration_prompt_address": "Спасибо.\nВведите адрес доставки (например: г. Душанбе, ул. Рудаки 15, кв 5).",
        "registration_complete": "🎉 Регистрация завершена! Добро пожаловать, {full_name}!",
        "registration_error": "⚠️ Ошибка регистрации. Попробуйте /start.",
        "registration_required": "Вы не зарегистрированы. Начните с /start.",
        "send_contact_button": "📱 Поделиться номером",
        "cancel_button": "Отмена",
        "admin_notify_new_user": (
            "👤 <b>Новый пользователь!</b>\n\n"
            "<b>ФИО:</b> {full_name}\n"
            "<b>Телефон:</b> {phone}\n"
            "<b>Адрес:</b> {address}\n"
            "<b>ID:</b> <code>{user_id}</code>\n"
            "<b>Username:</b> {username}"
        ),

        "lk_welcome": "Вы в Личном кабинете, {name}. Выберите действие:",
        "lk_welcome_back": "Вы в Личном кабинете. Выберите действие:",
        "lk_menu_buttons": [
            ["📋 Мои заказы", "🏠 Мой профиль"],
            ["🚚 Заказать доставку", "🗄 Архив заказов"],
            ["⬅️ Назад"]
        ],
        "lk_admin_menu_buttons": [
            ["🚚 Оформление на доставку", "📦 Полученные товары"],
            ["📊 Статистика", "📣 Рассылка"],
            ["💾 Скачать Excel", "🏠 Мой профиль"],
            ["⬅️ Назад"]
        ],

        "profile_info": (
            "<b>Ваш профиль:</b>\n\n"
            "<b>ФИО:</b> {full_name}\n"
            "<b>Телефон:</b> {phone_number}\n"
            "<b>Адрес:</b> {address}"
        ),
        "profile_address_not_set": "Не указан",
        "profile_button_edit_phone": "✏️ Изменить телефон",
        "profile_button_edit_address": "✏️ Изменить адрес",

        "lk_edit_address_prompt": "Ваш текущий адрес: <i>{address}</i>\n\nВведите новый адрес:",
        "lk_edit_address_success": "✅ Адрес обновлён!",
        "lk_edit_phone_prompt": "Ваш текущий телефон: <i>{phone}</i>\n\nВведите новый телефон (<code>+992XXXXXXXXX</code>):",
        "lk_edit_phone_success": "✅ Телефон обновлён!",
        "lk_edit_error": "⚠️ Ошибка. Попробуйте позже.",

        "lk_orders_title": "<b>Ваши привязанные заказы</b>",
        "lk_no_orders": "У вас пока нет привязанных заказов.\n\nПосле проверки трек-кода через '🔍 Отследить трек-код' он появится здесь.",
        "lk_order_item": "📦 <b>{code}</b> — {status} (от {date})\n",

        "status_yiwu": "В Иу",
        "status_dushanbe": "В Душанбе",
        "status_deliveryrequested": "Ожидает доставки",
        "status_delivered": "Доставлен",

        "lk_delivery_select_order": "🚚 <b>Заказ доставки</b>\n\nВыберите заказ, прибывший в Душанбе:",
        "lk_delivery_select_all_orders": (
            "🚚 <b>Заказ доставки</b>\n\n"
            "Готовые к доставке заказы:\n"
            "{codes}\n\n"
            "Заказать доставку для <b>всех</b>?"
        ),
        "lk_delivery_button_all": "✅ Да, заказать доставку (всего: {count} шт.)",
        "order_delivery_prompt_all": "Выбраны <b>все</b> заказы.\nКуда доставить?",
        "lk_delivery_no_orders": "У вас нет заказов, готовых к доставке (со статусом 'Душанбе').",
        "order_delivery_prompt": "Выбран заказ <b>{track_code}</b>.\nКуда доставить?",
        "order_delivery_button_use_saved": "📍 Использовать мой адрес: {address}",
        "order_delivery_button_new": "✏️ Ввести новый адрес",
        "order_delivery_prompt_new": "Введите адрес доставки:",
        "order_delivery_request_sent": "✅ Заявка принята. Ваш товар будет доставлен в течение 48 часов. Ожидайте звонка курьера.",
        "admin_notify_delivery_request": (
            "✅ <b>Новая заявка на доставку!</b>\n\n"
            "Клиент: {full_name} ({username})\n"
            "Телефон: {phone_number}\n"
            "Трек-код(ы): {track_codes}\n"
            "Адрес: {address}"
        ),

        "order_link_success": "✅ Заказ привязан к вашему профилю!",
        "order_link_fail": "⚠️ Не удалось привязать заказ. Возможно, он уже привязан.",

        "admin_delivery_requests_title": "<b>🚚 Новые заявки на доставку:</b>",
        "admin_delivery_requests_empty": "Новых заявок нет.",
        "admin_delivery_requests_item": (
            "\n<b>Клиент:</b> {full_name} (<code>{user_id}</code>)\n"
            "<b>Телефон:</b> <code>{phone_number}</code>\n"
            "<b>Адрес:</b> {address}\n"
            "<b>Заказы:</b> {track_codes}\n"
        ),
        "admin_delivery_button_confirm": "✅ Выдано (Клиент: {user_id})",
        "admin_delivery_confirm_success": "✅ Заявка {full_name} ({track_codes}) отмечена как 'Доставлено'.",
        "admin_delivery_confirm_fail": "❌ Не удалось обработать заявку.",

        "admin_delivered_list_title": "<b>📦 Недавно выданные товары:</b>",
        "admin_delivered_list_empty": "Недавно выданных товаров нет.",
        "admin_delivered_item": "✅ <b>{code}</b> — {full_name} (от {date})\n",

        "user_notify_delivered_title": "🎉 Заказ получен!",
        "user_notify_delivered_body": (
            "Ваши заказы отмечены как <b>полученные</b>:\n"
            "{track_codes}\n\n"
            "Спасибо, что выбрали DC Cargo!"
        ),

        "main_buttons": [
            ["🔍 Отследить трек-код", "👤 Личный кабинет"],
            ["📞 Контакты", "📊 Тарифы"],
            ["❌ Запрещённые грузы", "📍 Адрес склада"],
            ["🌐 Сменить язык"]
        ],
    },

    "en": {
        "welcome": "Hi {name}, glad to have you with us. Please select a language.",
        "welcome_back": "Welcome back, {name}!",
        "language_selected": "Language set: English",
        "invalid_input": "Please use the menu buttons or enter a track code.",
        "select_action": "Select an action:",
        "track_code_prompt": "Enter your track code:",

        "track_code_found_yiwu": (
            "Assalomu alaykum!\n"
            "✅ Your cargo with track code <b>{code}</b> has been received at DC Cargo warehouse in Yiwu.\n"
            "🗓️ <b>Acceptance date:</b> {date}\n"
            "⏳ Delivery time: 12-20 days. We will try to deliver ahead of schedule.\n\n"
            "✨ DC Cargo! Reliable, fast cargo at an affordable price."
        ),
        "track_code_found_dushanbe": (
            "Assalomu alaykum!\n"
            "🚚 Your cargo <b>{code}</b> has arrived at DC Cargo warehouse in Dushanbe!\n"
            "🗓️ <b>Arrival date:</b> {date}\n\n"
            f"📞 Please contact us: <code>{CONTACT_PHONE_DISPLAY}</code>.\n\n"
            "✨ DC Cargo! Reliable, fast cargo at an affordable price."
        ),
        "track_code_not_found": "❌ Your cargo has not arrived at DC Cargo warehouse in Yiwu yet.",
        "track_code_found_other": (
            "ℹ️ Status of order <b>{code}</b>:\n"
            "<b>{status}</b>"
        ),

        "track_codes_not_loaded": "⚠️ Problem loading track codes. Contact admin.",
        "file_received": "File received. Processing...",
        "file_wrong_name": f"⚠️ Please send a file named exactly: {XLSX_FILENAME}",
        "file_upload_forbidden": "⛔ You do not have permission to upload files.",
        "file_upload_success": f"✅ File {XLSX_FILENAME} updated!\nLoaded track codes: {{count}}.",
        "file_download_error": "❌ Failed to download or process the file.",
        "job_reload_success": "Automatic reload from {filename} successful. Loaded: {count}.",
        "job_reload_fail": "⚠️ Error during automatic reload from {filename}. Check logs.",
        "admin_notify_initial_load_fail": f"⚠️ CRITICAL: Failed to load from {XLSX_FILENAME} on startup!",
        "admin_notify_photo_not_found": "⚠️ Photo file '{photo_path}' not found.",
        "dushanbe_arrival_notification": (
            "🚚 Dear Customer!\n"
            "Your cargo '{code}' has arrived at DC Cargo warehouse in Dushanbe!\n"
            f"📞 Please contact us: {CONTACT_PHONE_DISPLAY}."
        ),
        "contacts": (
            "<b>DC Cargo</b>\n"
            "Working hours: 9:00 to 18:00\n"
            "Break: 12:00 to 13:00\n\n"
            f"💬 Operator: {OPERATOR_LINK}\n"
            f"📸 Instagram: <a href=\"{INSTAGRAM_LINK}\">@{INSTAGRAM_HANDLE}</a>\n"
            f"📢 Telegram channel: {TELEGRAM_CHANNEL_LINK}"
        ),
        "prices_text": (
            "<b>Our Rates</b>\n\n"
            "🇨🇳 Yiwu — Dushanbe 🇹🇯\n"
            "Delivery time: 12-20 days\n\n"
            "🚚 1 to 30 kg: <b>2.5$</b>\n"
            "🚚 30 to 50 kg: <b>2.3$</b>\n"
            "🚚 50 kg and above: <b>2.0$</b>\n"
            "📦 Per cubic meter: <b>250$</b>\n\n"
            "⚠️ Oversized cargo is calculated as cube.\n\n"
            "💼 <b>From 200 kg — price is negotiable.</b>\n"
            "Discounts and individual terms are possible.\n"
            f"✍️ DM us on Instagram: <a href=\"{INSTAGRAM_LINK}\">@{INSTAGRAM_HANDLE}</a> "
            f"or contact the operator: {OPERATOR_LINK}"
        ),
        "forbidden_text": (
            "<b>Prohibited Items:</b>\n"
            "1. Medicines (powder, tablets, liquids)\n"
            "2. All liquids (perfume, fresheners, etc.)\n"
            "3. All cold weapons (knives, stun guns, batons)\n"
            "4. E-cigarettes, hookahs — not accepted."
        ),
        "address_text": "Select address:",
        "button_china": "🏭 Address in China",
        "button_tajikistan": "🇹🇯 Pick-up in Dushanbe",
        "address_caption_china": _CHINA_ADDRESS_EN,
        "address_caption_tajikistan": _TJ_CONTACT_EN,
        "image_received": "Image received. I don't process images yet. 😊",
        "error": "An error occurred. Try again or /start.",
        "photo_address_error": "Could not send photo. Address:\n{address}",
        "photo_contact_error": "Could not send photo. Contacts:\n{contacts}",
        "photo_price_error": "Could not send photo. Rates:\n{price_list}",
        "stats_forbidden": "⛔ Admin only.",
        "stats_message": "📊 Bot stats:\nTotal unique users: {count}",
        "admin_broadcast_prompt": "Enter broadcast message. /cancel to abort.",
        "admin_broadcast_confirm_prompt": "Send this message? (Yes / No)\n\n{message}",
        "admin_broadcast_cancelled": "Broadcast cancelled.",
        "admin_broadcast_report": "✅ Broadcast done.\nSent: {success}\nFailed: {failed}",
        "help_message": (
            "👋 Hello! I am DC Cargo Bot.\n\n"
            "🔍 <b>Track</b>, 👤 <b>Personal Cabinet</b>, 📞 <b>Contacts</b>, "
            "📊 <b>Rates</b>, ❌ <b>Forbidden</b>, 📍 <b>Address</b>, 🌐 <b>Language</b>.\n\n"
            "Use /start to reset."
        ),

        "subscribe_prompt": "To continue, please subscribe to our channel:",
        "subscribe_button_channel": "DC Cargo",
        "subscribe_button_check": "I subscribed ✅",
        "checking_button": "Checking...",
        "subscribe_fail": "Not subscribed. Please subscribe and press 'Check'.",
        "subscription_success": "Thanks for subscribing! ✅",

        "registration_start": "Let's start registration.",
        "registration_prompt_name": "Please send your Full Name (e.g., John Smith):",
        "registration_invalid_name": "❌ Invalid name. At least two words (first and last).",
        "registration_prompt_phone": "Great, {full_name}.\nShare your phone (button below) or enter manually in <code>+992XXXXXXXXX</code> format:",
        "registration_invalid_phone": "❌ Invalid phone. Must be <code>+992XXXXXXXXX</code>.",
        "registration_prompt_address": "Thank you.\nEnter your delivery address (e.g., Dushanbe, Rudaki 15, apt 5).",
        "registration_complete": "🎉 Registration complete! Welcome, {full_name}!",
        "registration_error": "⚠️ Registration error. Try /start.",
        "registration_required": "You are not registered. Start with /start.",
        "send_contact_button": "📱 Share Phone Number",
        "cancel_button": "Cancel",
        "admin_notify_new_user": (
            "👤 <b>New user!</b>\n\n"
            "Full Name: {full_name}\n"
            "Phone: {phone}\n"
            "Address: {address}\n"
            "ID: <code>{user_id}</code>\n"
            "Username: {username}"
        ),

        "lk_welcome": "Personal Cabinet, {name}. Choose an action:",
        "lk_welcome_back": "Personal Cabinet. Choose an action:",
        "lk_menu_buttons": [
            ["📋 My Orders", "🏠 My Profile"],
            ["🚚 Request Delivery", "🗄 Orders Archive"],
            ["⬅️ Back"]
        ],
        "lk_admin_menu_buttons": [
            ["🚚 Delivery Requests", "📦 Received Goods"],
            ["📊 Statistics", "📣 Broadcast"],
            ["💾 Download Excel", "🏠 My Profile"],
            ["⬅️ Back"]
        ],

        "profile_info": (
            "<b>Your Profile:</b>\n\n"
            "<b>Full Name:</b> {full_name}\n"
            "<b>Phone:</b> {phone_number}\n"
            "<b>Address:</b> {address}"
        ),
        "profile_address_not_set": "Not set",
        "profile_button_edit_phone": "✏️ Edit Phone",
        "profile_button_edit_address": "✏️ Edit Address",

        "lk_edit_address_prompt": "Current address: <i>{address}</i>\n\nEnter new address:",
        "lk_edit_address_success": "✅ Address updated!",
        "lk_edit_phone_prompt": "Current phone: <i>{phone}</i>\n\nEnter new phone (<code>+992XXXXXXXXX</code>):",
        "lk_edit_phone_success": "✅ Phone updated!",
        "lk_edit_error": "⚠️ Error. Try again later.",

        "lk_orders_title": "<b>Your Linked Orders</b>",
        "lk_no_orders": "You have no linked orders yet.\n\nOnce you check a track code via '🔍 Track', it will appear here.",
        "lk_order_item": "📦 <b>{code}</b> — {status} (from {date})\n",

        "status_yiwu": "In Yiwu",
        "status_dushanbe": "In Dushanbe",
        "status_deliveryrequested": "Pending Delivery",
        "status_delivered": "Delivered",

        "lk_delivery_select_order": "🚚 <b>Request Delivery</b>\n\nSelect an order arrived in Dushanbe:",
        "lk_delivery_select_all_orders": (
            "🚚 <b>Request Delivery</b>\n\n"
            "Orders ready for delivery:\n"
            "{codes}\n\n"
            "Request delivery for <b>all</b>?"
        ),
        "lk_delivery_button_all": "✅ Yes, request delivery ({count} total)",
        "order_delivery_prompt_all": "<b>All</b> orders selected.\nDeliver where?",
        "lk_delivery_no_orders": "No orders ready for delivery (with 'Dushanbe' status).",
        "order_delivery_prompt": "Order <b>{track_code}</b> selected.\nDeliver where?",
        "order_delivery_button_use_saved": "📍 Use my address: {address}",
        "order_delivery_button_new": "✏️ Enter new address",
        "order_delivery_prompt_new": "Enter delivery address:",
        "order_delivery_request_sent": "✅ Request accepted. Your item will be delivered within 48 hours. Expect a courier call.",
        "admin_notify_delivery_request": (
            "✅ <b>New delivery request!</b>\n\n"
            "Customer: {full_name} ({username})\n"
            "Phone: {phone_number}\n"
            "Track code(s): {track_codes}\n"
            "Address: {address}"
        ),

        "order_link_success": "✅ Order linked to your profile!",
        "order_link_fail": "⚠️ Failed to link. Maybe already linked.",

        "admin_delivery_requests_title": "<b>🚚 New Delivery Requests:</b>",
        "admin_delivery_requests_empty": "No new delivery requests.",
        "admin_delivery_requests_item": (
            "\n<b>Client:</b> {full_name} (<code>{user_id}</code>)\n"
            "<b>Phone:</b> <code>{phone_number}</code>\n"
            "<b>Address:</b> {address}\n"
            "<b>Orders:</b> {track_codes}\n"
        ),
        "admin_delivery_button_confirm": "✅ Delivered (Client: {user_id})",
        "admin_delivery_confirm_success": "✅ Request {full_name} ({track_codes}) marked as 'Delivered'.",
        "admin_delivery_confirm_fail": "❌ Failed to process request.",

        "admin_delivered_list_title": "<b>📦 Recently Delivered:</b>",
        "admin_delivered_list_empty": "No recently delivered.",
        "admin_delivered_item": "✅ <b>{code}</b> — {full_name} (on {date})\n",

        "user_notify_delivered_title": "🎉 Order Received!",
        "user_notify_delivered_body": (
            "Your orders marked as <b>received</b>:\n"
            "{track_codes}\n\n"
            "Thanks for choosing DC Cargo!"
        ),

        "main_buttons": [
            ["🔍 Track Code", "👤 Personal Cabinet"],
            ["📞 Contacts", "📊 Rates"],
            ["❌ Forbidden Goods", "📍 Warehouse Address"],
            ["🌐 Change Language"]
        ],
    },

    "tg": {
        "welcome": "Салом {name}, хуш омадед. Лутфан забонро интихоб кунед.",
        "welcome_back": "Хуш омадед, {name}!",
        "language_selected": "Забон интихоб шуд: Тоҷикӣ",
        "invalid_input": "Лутфан тугмаҳои менюро истифода баред ё трек-кодро ворид кунед.",
        "select_action": "Амалро интихоб кунед:",
        "track_code_prompt": "Трек-кодро ворид кунед:",

        "track_code_found_yiwu": (
            "Ассалому алайкум!\n"
            "✅ Бори шумо бо трек-коди <b>{code}</b> дар анбори DC Cargo дар ш. Иву қабул шуд.\n"
            "🗓️ <b>Санаи қабул:</b> {date}\n"
            "⏳ Мӯҳлат: 12-20 рӯз.\n\n"
            "✨ DC Cargo! Каргои боэтимод ва зуд."
        ),
        "track_code_found_dushanbe": (
            "Ассалому алайкум!\n"
            "🚚 Бори шумо бо трек-коди <b>{code}</b> ба анбори DC Cargo дар ш. Душанбе расид!\n"
            "🗓️ <b>Санаи расидан:</b> {date}\n\n"
            f"📞 Барои гирифтан тамос гиред: <code>{CONTACT_PHONE_DISPLAY}</code>.\n\n"
            "✨ DC Cargo!"
        ),
        "track_code_not_found": "❌ Бори шумо то ҳол дар анбори DC Cargo дар ш. Иву наомадааст.",
        "track_code_found_other": (
            "ℹ️ Ҳолати фармоиши <b>{code}</b>:\n"
            "<b>{status}</b>"
        ),

        "track_codes_not_loaded": "⚠️ Мушкилот бо трек-кодҳо. Ба админ муроҷиат кунед.",
        "file_received": "Файл қабул шуд. Коркард...",
        "file_wrong_name": f"⚠️ Файлро бо номи аниқ ирсол кунед: {XLSX_FILENAME}",
        "file_upload_forbidden": "⛔ Шумо ҳуқуқ надоред.",
        "file_upload_success": f"✅ {XLSX_FILENAME} нав шуд! Кодҳо: {{count}}.",
        "file_download_error": "❌ Файлро коркард кардан нашуд.",
        "job_reload_success": "Навсозии {filename} муваффақ. Кодҳо: {count}.",
        "job_reload_fail": "⚠️ Хатогии навсозии {filename}.",
        "admin_notify_initial_load_fail": f"⚠️ КРИТИКИ: {XLSX_FILENAME} бор нашуд!",
        "admin_notify_photo_not_found": "⚠️ Файли акси '{photo_path}' ёфт нашуд.",
        "dushanbe_arrival_notification": (
            "🚚 Мизоҷи муҳтарам!\n"
            "Бори шумо бо трек-коди '{code}' ба анбори DC Cargo дар Душанбе расид!\n"
            f"📞 Тамос гиред: {CONTACT_PHONE_DISPLAY}."
        ),
        "contacts": (
            "<b>DC Cargo</b>\n"
            "Реҷаи корӣ: 9:00 - 18:00\n"
            "Танаффус: 12:00 - 13:00\n\n"
            f"💬 Оператор: {OPERATOR_LINK}\n"
            f"📸 Instagram: <a href=\"{INSTAGRAM_LINK}\">@{INSTAGRAM_HANDLE}</a>\n"
            f"📢 Канали Telegram: {TELEGRAM_CHANNEL_LINK}"
        ),
        "prices_text": (
            "<b>Нархномаи мо</b>\n\n"
            "🇨🇳 Иу — Душанбе 🇹🇯\n"
            "Мӯҳлат: 12-20 рӯз\n\n"
            "🚚 Аз 1 то 30 кг: <b>2.5$</b>\n"
            "🚚 Аз 30 то 50 кг: <b>2.3$</b>\n"
            "🚚 Аз 50 кг боло: <b>2.0$</b>\n"
            "📦 1 куб: <b>250$</b>\n\n"
            "⚠️ Борҳои калонҳаҷм чун куб ҳисоб мешаванд.\n\n"
            "💼 <b>Аз 200 кг боло — нарх шартномавӣ.</b>\n"
            "Тахфиф ё шартҳои инфиродӣ имконпазиранд.\n"
            f"✍️ Ба Direct нависед: <a href=\"{INSTAGRAM_LINK}\">@{INSTAGRAM_HANDLE}</a> "
            f"ё ба оператор: {OPERATOR_LINK}"
        ),
        "forbidden_text": (
            "<b>Молҳои манъшуда:</b>\n"
            "1. Доруворӣ\n"
            "2. Моеъҳо (атриёт ва ғ.)\n"
            "3. Аслиҳаи сард\n"
            "4. Сигаретаҳои электронӣ, кальянҳо."
        ),
        "address_text": "Суроғаро интихоб кунед:",
        "button_china": "🏭 Суроға дар Хитой",
        "button_tajikistan": "🇹🇯 Гирифтан дар Душанбе",
        "address_caption_china": _CHINA_ADDRESS_TG,
        "address_caption_tajikistan": _TJ_CONTACT_TG,
        "image_received": "Тасвир қабул шуд. 😊",
        "error": "Хатогӣ. Лутфан /start.",
        "photo_address_error": "Суроға:\n{address}",
        "photo_contact_error": "Тамосҳо:\n{contacts}",
        "photo_price_error": "Тарофаҳо:\n{price_list}",
        "stats_forbidden": "⛔ Танҳо админ.",
        "stats_message": "📊 Омор:\nИстифодабарандагон: {count}",
        "admin_broadcast_prompt": "Паёмро ворид кунед. /cancel бекор.",
        "admin_broadcast_confirm_prompt": "Фиристам? (Ҳа / Не)\n\n{message}",
        "admin_broadcast_cancelled": "Ирсол бекор шуд.",
        "admin_broadcast_report": "✅ Ирсол анҷом. Фиристода: {success}. Хато: {failed}",
        "help_message": (
            "👋 Ман боти DC Cargo.\n\n"
            "Аз тугмаҳо истифода баред. /start барои аз нав."
        ),

        "subscribe_prompt": "Барои идома ба канал обуна шавед:",
        "subscribe_button_channel": "DC Cargo",
        "subscribe_button_check": "Обуна шудам ✅",
        "checking_button": "Санҷиш...",
        "subscribe_fail": "Обуна нашудаед. Санҷед.",
        "subscription_success": "Ташаккур! ✅",

        "registration_start": "Бақайдгириро оғоз мекунем.",
        "registration_prompt_name": "Ном ва Насаби худро ворид кунед (Масалан: Каримов Карим):",
        "registration_invalid_name": "❌ Формат нодуруст. Ҳадди аққал 2 калима.",
        "registration_prompt_phone": "Хуб, {full_name}.\nРақами телефонро равон кунед ё ба таври дастӣ <code>+992XXXXXXXXX</code>:",
        "registration_invalid_phone": "❌ Формат нодуруст. <code>+992XXXXXXXXX</code>.",
        "registration_prompt_address": "Ташаккур.\nСуроғаи дастрасиро ворид кунед (Масалан: ш. Душанбе, кӯч. Рӯдакӣ 15).",
        "registration_complete": "🎉 Бақайдгирӣ анҷом ёфт! Хуш омадед, {full_name}!",
        "registration_error": "⚠️ Хатогӣ. /start.",
        "registration_required": "Ба қайд нагирифта. /start.",
        "send_contact_button": "📱 Равон кардани рақам",
        "cancel_button": "Бекор кардан",
        "admin_notify_new_user": (
            "👤 <b>Истифодабарандаи нав!</b>\n\n"
            "ННН: {full_name}\n"
            "Тел: {phone}\n"
            "Суроға: {address}\n"
            "ID: <code>{user_id}</code>\n"
            "Username: {username}"
        ),

        "lk_welcome": "Кабинети шахсӣ, {name}. Амалро интихоб кунед:",
        "lk_welcome_back": "Кабинети шахсӣ. Амалро интихоб кунед:",
        "lk_menu_buttons": [
            ["📋 Фармоишҳои ман", "🏠 Профили ман"],
            ["🚚 Дархости интиқол", "🗄 Архиви фармоишҳо"],
            ["⬅️ Ба қафо"]
        ],
        "lk_admin_menu_buttons": [
            ["🚚 Дархостҳои нав", "📦 Молҳои гирифташуда"],
            ["📊 Омор", "📣 Паёмнамо"],
            ["💾 Боргирии Excel", "🏠 Профили ман"],
            ["⬅️ Ба менюи асосӣ"]
        ],

        "profile_info": (
            "<b>Профили шумо:</b>\n\n"
            "<b>ННН:</b> {full_name}\n"
            "<b>Тел:</b> {phone_number}\n"
            "<b>Суроға:</b> {address}"
        ),
        "profile_address_not_set": "Нишон дода нашудааст",
        "profile_button_edit_phone": "✏️ Ивази телефон",
        "profile_button_edit_address": "✏️ Ивази суроға",

        "lk_edit_address_prompt": "Суроғаи ҷорӣ: <i>{address}</i>\n\nСуроғаи навро ворид кунед:",
        "lk_edit_address_success": "✅ Суроға нав шуд!",
        "lk_edit_phone_prompt": "Телефони ҷорӣ: <i>{phone}</i>\n\nНаворо ворид кунед (<code>+992XXXXXXXXX</code>):",
        "lk_edit_phone_success": "✅ Телефон нав шуд!",
        "lk_edit_error": "⚠️ Хатогӣ.",

        "lk_orders_title": "<b>Фармоишҳои шумо</b>",
        "lk_no_orders": "Шумо фармоиш надоред.\n\nПас аз санҷиши трек-код он ин ҷо пайдо мешавад.",
        "lk_order_item": "📦 <b>{code}</b> — {status} (аз {date})\n",

        "status_yiwu": "Дар Иу",
        "status_dushanbe": "Дар Душанбе",
        "status_deliveryrequested": "Интизори расонидан",
        "status_delivered": "Расонида шуд",

        "lk_delivery_select_order": "🚚 <b>Дархости интиқол</b>\n\nФармоишро интихоб кунед:",
        "lk_delivery_select_all_orders": (
            "🚚 <b>Дархости интиқол</b>\n\n"
            "Фармоишҳои омода:\n"
            "{codes}\n\n"
            "Барои <b>ҳама</b> дархост кунем?"
        ),
        "lk_delivery_button_all": "✅ Ҳа, дархост ({count} дона)",
        "order_delivery_prompt_all": "<b>Ҳама</b> интихоб шуд.\nБа куҷо?",
        "lk_delivery_no_orders": "Фармоиши омодаи интиқол надоред.",
        "order_delivery_prompt": "Фармоиши <b>{track_code}</b>.\nБа куҷо?",
        "order_delivery_button_use_saved": "📍 Суроғаи ман: {address}",
        "order_delivery_button_new": "✏️ Суроғаи нав",
        "order_delivery_prompt_new": "Суроғаи интиқолро ворид кунед:",
        "order_delivery_request_sent": "✅ Дархост қабул шуд. Дар 48 соат расонида мешавад.",
        "admin_notify_delivery_request": (
            "✅ <b>Дархости нав!</b>\n\n"
            "Мизоҷ: {full_name} ({username})\n"
            "Тел: {phone_number}\n"
            "Трек-код: {track_codes}\n"
            "Суроға: {address}"
        ),

        "order_link_success": "✅ Фармоиш пайваст шуд!",
        "order_link_fail": "⚠️ Пайваст нашуд.",

        "admin_delivery_requests_title": "<b>🚚 Дархостҳои нав:</b>",
        "admin_delivery_requests_empty": "Дархост нест.",
        "admin_delivery_requests_item": (
            "\n<b>Мизоҷ:</b> {full_name} (<code>{user_id}</code>)\n"
            "<b>Тел:</b> <code>{phone_number}</code>\n"
            "<b>Суроға:</b> {address}\n"
            "<b>Фармоишҳо:</b> {track_codes}\n"
        ),
        "admin_delivery_button_confirm": "✅ Супорид (Мизоҷ: {user_id})",
        "admin_delivery_confirm_success": "✅ {full_name} ({track_codes}) — 'Расонидашуд'.",
        "admin_delivery_confirm_fail": "❌ Хатогӣ.",

        "admin_delivered_list_title": "<b>📦 Супоридашудаҳо:</b>",
        "admin_delivered_list_empty": "Холӣ.",
        "admin_delivered_item": "✅ <b>{code}</b> — {full_name} (санаи {date})\n",

        "user_notify_delivered_title": "🎉 Фармоиш гирифта шуд!",
        "user_notify_delivered_body": (
            "Фармоишҳо <b>гирифташуда</b> қайд шуданд:\n"
            "{track_codes}\n\n"
            "Ташаккур, ки DC Cargo-ро интихоб кардед!"
        ),

        "main_buttons": [
            ["🔍 Пайгирии трек-код", "👤 Утоқи шахсӣ"],
            ["📞 Тамосҳо", "📊 Тарофаҳо"],
            ["❌ Молҳои манъшуда", "📍 Суроғаи анбор"],
            ["🌐 Ивази забон"]
        ],
    },
}
