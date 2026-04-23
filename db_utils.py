# -*- coding: utf-8 -*-
# DC Cargo — db_utils.py
# Общая БД с CargoBot, но таблицы с префиксом dc_ (dc_users, dc_orders).
import psycopg2
import psycopg2.pool
import psycopg2.extras
import asyncio
from urllib.parse import urlparse
from config import DATABASE_URL, USERS_TABLE, ORDERS_TABLE, logger


# --- Пул соединений ---
pool = None


def parse_database_url(url):
    try:
        result = urlparse(url)
        return {
            'dbname': result.path[1:],
            'user': result.username,
            'password': result.password,
            'host': result.hostname,
            'port': result.port,
        }
    except Exception as e:
        logger.error(f"Ошибка парсинга DATABASE_URL: {e}")
        return None


def init_db_pool():
    """Инициализирует пул соединений и создаёт таблицы DC Cargo."""
    global pool
    if pool:
        logger.info("Пул соединений уже инициализирован.")
        return

    if not DATABASE_URL:
        logger.critical("DATABASE_URL не найден. Пул не может быть создан.")
        return

    db_params = parse_database_url(DATABASE_URL)
    if not db_params:
        logger.critical("Не удалось разобрать DATABASE_URL.")
        return

    try:
        logger.info("Инициализация пула соединений PostgreSQL...")
        pool = psycopg2.pool.SimpleConnectionPool(1, 20, **db_params)

        if not pool:
            logger.error("Не удалось создать пул соединений Postgres.")
            return

        logger.info("Пул соединений Postgres успешно создан.")
        conn = get_db()
        if conn:
            try:
                create_tables(conn)
            finally:
                release_db(conn)
        else:
            logger.error("Не удалось получить соединение из пула для создания таблиц.")

    except psycopg2.DatabaseError as e:
        logger.critical(f"Не удалось подключиться к PostgreSQL: {e}")
    except Exception as e:
        logger.critical(f"Неизвестная ошибка при инициализации пула: {e}")


def close_db_pool():
    global pool
    if pool:
        try:
            pool.closeall()
            pool = None
            logger.info("Пул соединений PostgreSQL закрыт.")
        except Exception as e:
            logger.error(f"Ошибка при закрытии пула: {e}")


def get_db():
    global pool
    if pool is None:
        logger.error("Пул не инициализирован. Пробуем инициализировать.")
        init_db_pool()
        if pool is None:
            logger.critical("Аварийная инициализация пула не удалась.")
            return None
    try:
        conn = pool.getconn()
        conn.autocommit = False
        return conn
    except Exception as e:
        logger.error(f"Ошибка при получении соединения: {e}")
        return None


def release_db(conn):
    global pool
    if not conn:
        return
    try:
        if pool:
            pool.putconn(conn)
        else:
            conn.close()
    except Exception as e:
        logger.error(f"Ошибка при возврате соединения: {e}")


# --- Универсальный запрос ---

def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    conn = None
    try:
        conn = get_db()
        if conn is None:
            logger.error("Нет соединения с БД для execute_query")
            return None

        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            result = None
            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()

            if commit:
                conn.commit()
                if result is not None:
                    return result
                return cursor.rowcount

            if result is not None:
                return result
            return cursor.rowcount

    except psycopg2.DatabaseError as e:
        logger.error(f"DB ERROR ({e.pgcode}): {e}")
        logger.error(f"   Query: {query}")
        logger.error(f"   Params: {params}")
        if conn:
            conn.rollback()
        return None
    except Exception as e:
        logger.error(f"UNKNOWN DB ERROR: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            release_db(conn)


# --- Создание таблиц ---

def create_tables(conn):
    """Создаёт dc_users и dc_orders, если их нет."""
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {USERS_TABLE} (
                    user_id BIGINT PRIMARY KEY,
                    full_name VARCHAR(255),
                    username VARCHAR(255),
                    phone_number VARCHAR(50),
                    address TEXT,
                    language_code VARCHAR(10) DEFAULT 'ru',
                    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_subscribed BOOLEAN DEFAULT FALSE,
                    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info(f"Таблица '{USERS_TABLE}' проверена/создана.")

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {ORDERS_TABLE} (
                    id SERIAL PRIMARY KEY,
                    track_code VARCHAR(100) UNIQUE NOT NULL,
                    user_id BIGINT,
                    status_yiwu VARCHAR(100),
                    date_yiwu DATE,
                    status_dushanbe VARCHAR(100),
                    date_dushanbe DATE,
                    status_delivered VARCHAR(100),
                    date_delivered DATE,
                    notify_dushanbe BOOLEAN DEFAULT FALSE,
                    notify_delivered BOOLEAN DEFAULT FALSE,
                    is_archived BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES {USERS_TABLE}(user_id) ON DELETE SET NULL
                );
            """)
            logger.info(f"Таблица '{ORDERS_TABLE}' проверена/создана.")

            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{ORDERS_TABLE}_user_id ON {ORDERS_TABLE} (user_id);")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{ORDERS_TABLE}_status_dushanbe ON {ORDERS_TABLE} (status_dushanbe);")

            conn.commit()
        logger.info(f"Таблицы DC Cargo готовы.")

    except psycopg2.DatabaseError as e:
        logger.error(f"DB ERROR при создании таблиц: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")


# === Пользователи ===

async def get_user(user_id):
    q = f"SELECT * FROM {USERS_TABLE} WHERE user_id = %s"
    return await asyncio.to_thread(execute_query, q, (user_id,), fetchone=True)


async def create_user(user_id, lang, username=None, full_name=None):
    q = f"""
        INSERT INTO {USERS_TABLE} (user_id, language_code, username, full_name, last_activity)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE SET
            language_code = EXCLUDED.language_code,
            username = EXCLUDED.username,
            full_name = COALESCE({USERS_TABLE}.full_name, EXCLUDED.full_name),
            last_activity = CURRENT_TIMESTAMP
    """
    return await asyncio.to_thread(execute_query, q, (user_id, lang, username, full_name), commit=True)


async def update_user_activity(user_id):
    q = f"UPDATE {USERS_TABLE} SET last_activity = CURRENT_TIMESTAMP WHERE user_id = %s"
    return await asyncio.to_thread(execute_query, q, (user_id,), commit=True)


async def update_user_profile(user_id, full_name, phone_number, address):
    q = f"""
        UPDATE {USERS_TABLE}
        SET full_name = %s, phone_number = %s, address = %s
        WHERE user_id = %s
    """
    return await asyncio.to_thread(execute_query, q, (full_name, phone_number, address, user_id), commit=True)


async def update_user_phone(user_id, phone_number):
    q = f"UPDATE {USERS_TABLE} SET phone_number = %s WHERE user_id = %s"
    return await asyncio.to_thread(execute_query, q, (phone_number, user_id), commit=True)


async def update_user_address(user_id, address):
    q = f"UPDATE {USERS_TABLE} SET address = %s WHERE user_id = %s"
    return await asyncio.to_thread(execute_query, q, (address, user_id), commit=True)


async def update_user_lang(user_id, lang):
    q = f"UPDATE {USERS_TABLE} SET language_code = %s WHERE user_id = %s"
    return await asyncio.to_thread(execute_query, q, (lang, user_id), commit=True)


async def get_all_users_count(active_only=False):
    if active_only:
        q = f"SELECT COUNT(*) AS count FROM {USERS_TABLE} WHERE last_activity >= CURRENT_TIMESTAMP - INTERVAL '30 days'"
    else:
        q = f"SELECT COUNT(*) AS count FROM {USERS_TABLE}"
    res = await asyncio.to_thread(execute_query, q, fetchone=True)
    return res['count'] if res else 0


async def get_all_user_ids(active_only=False):
    if active_only:
        q = f"SELECT user_id FROM {USERS_TABLE} WHERE last_activity >= CURRENT_TIMESTAMP - INTERVAL '30 days'"
    else:
        q = f"SELECT user_id FROM {USERS_TABLE}"
    res = await asyncio.to_thread(execute_query, q, fetchall=True)
    return [r['user_id'] for r in res] if res else []


async def get_user_subscription_status(user_id):
    q = f"SELECT is_subscribed FROM {USERS_TABLE} WHERE user_id = %s"
    res = await asyncio.to_thread(execute_query, q, (user_id,), fetchone=True)
    return res['is_subscribed'] if res else False


async def set_user_subscription_status(user_id, status):
    q = f"UPDATE {USERS_TABLE} SET is_subscribed = %s WHERE user_id = %s"
    return await asyncio.to_thread(execute_query, q, (status, user_id), commit=True)


async def register_user(user_id, full_name, username, phone_number, address, language_code='ru'):
    q = f"""
        INSERT INTO {USERS_TABLE} (
            user_id, full_name, username, phone_number, address, language_code,
            registration_date, last_activity
        ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            username = EXCLUDED.username,
            phone_number = EXCLUDED.phone_number,
            address = EXCLUDED.address,
            language_code = EXCLUDED.language_code,
            last_activity = CURRENT_TIMESTAMP
        RETURNING user_id;
    """
    res = await asyncio.to_thread(
        execute_query, q,
        (user_id, full_name, username, phone_number, address, language_code),
        fetchone=True, commit=True
    )
    return bool(res)


# === Заказы ===

async def get_order_by_track_code(track_code):
    q = f"SELECT * FROM {ORDERS_TABLE} WHERE track_code = %s"
    return await asyncio.to_thread(execute_query, q, (track_code,), fetchone=True)


async def get_order(track_code):
    return await get_order_by_track_code(track_code)


async def get_orders_by_user_id(user_id):
    q = f"SELECT * FROM {ORDERS_TABLE} WHERE user_id = %s ORDER BY date_yiwu DESC, id DESC"
    return await asyncio.to_thread(execute_query, q, (user_id,), fetchall=True)


async def get_user_orders(user_id):
    q = f"""
        SELECT track_code, status_yiwu, date_yiwu, status_dushanbe, date_dushanbe,
               status_delivered, date_delivered
        FROM {ORDERS_TABLE}
        WHERE user_id = %s
          AND (is_archived = FALSE OR is_archived IS NULL)
          AND (date_delivered IS NULL OR date_delivered >= CURRENT_DATE - INTERVAL '3 months')
        ORDER BY date_yiwu DESC, id DESC
    """
    return await asyncio.to_thread(execute_query, q, (user_id,), fetchall=True)


async def get_archived_user_orders(user_id):
    q = f"""
        SELECT track_code, status_yiwu, date_yiwu, status_dushanbe, date_dushanbe,
               status_delivered, date_delivered
        FROM {ORDERS_TABLE}
        WHERE user_id = %s
          AND (is_archived = TRUE
               OR (date_delivered IS NOT NULL AND date_delivered < CURRENT_DATE - INTERVAL '3 months'))
        ORDER BY date_delivered DESC, date_yiwu DESC, id DESC
    """
    return await asyncio.to_thread(execute_query, q, (user_id,), fetchall=True)


async def archive_delivered_orders(user_id):
    q = f"""
        UPDATE {ORDERS_TABLE}
        SET is_archived = TRUE
        WHERE user_id = %s
          AND status_delivered = 'Доставлен'
          AND (is_archived = FALSE OR is_archived IS NULL)
    """
    return await asyncio.to_thread(execute_query, q, (user_id,), commit=True)


async def mark_order_archived_by_code(track_code):
    q = f"""
        UPDATE {ORDERS_TABLE}
        SET status_delivered = 'Доставлен',
            date_delivered = COALESCE(date_delivered, CURRENT_DATE),
            is_archived = TRUE
        WHERE track_code = %s
    """
    return await asyncio.to_thread(execute_query, q, (track_code,), commit=True)


async def link_order_to_user(track_code, user_id):
    q = f"UPDATE {ORDERS_TABLE} SET user_id = %s WHERE track_code = %s AND user_id IS NULL"
    return await asyncio.to_thread(execute_query, q, (user_id, track_code), commit=True)


async def mark_order_as_delivered(track_code):
    q = f"""
        UPDATE {ORDERS_TABLE}
        SET status_delivered = 'Доставлен', date_delivered = CURRENT_DATE
        WHERE track_code = %s
    """
    return await asyncio.to_thread(execute_query, q, (track_code,), commit=True)


async def request_delivery_for_order(track_code):
    q = f"""
        UPDATE {ORDERS_TABLE}
        SET status_delivered = 'Запрошена'
        WHERE track_code = %s AND (status_delivered IS NULL OR status_delivered = 'В Душанбе')
    """
    return await asyncio.to_thread(execute_query, q, (track_code,), commit=True)


async def get_dushanbe_arrivals_to_notify():
    q = f"""
        SELECT o.track_code, o.user_id, u.language_code
        FROM {ORDERS_TABLE} o
        JOIN {USERS_TABLE} u ON o.user_id = u.user_id
        WHERE o.status_dushanbe IN ('В Душанбе', 'Dushanbe', 'Душанбе')
          AND o.notify_dushanbe = FALSE
          AND o.user_id IS NOT NULL
    """
    return await asyncio.to_thread(execute_query, q, fetchall=True)


async def set_dushanbe_notification_sent(track_code):
    q = f"UPDATE {ORDERS_TABLE} SET notify_dushanbe = TRUE WHERE track_code = %s"
    return await asyncio.to_thread(execute_query, q, (track_code,), commit=True)


async def upsert_order_from_excel(track_code, status_yiwu, date_yiwu,
                                  status_dushanbe, date_dushanbe,
                                  status_delivered, date_delivered):
    """Upsert из Excel. Не перезаписывает 'Запрошена' и 'Доставлен'."""
    def clean_value(v):
        if isinstance(v, str) and v.lower() in ('nan', 'none', '', 'null'):
            return None
        return v

    def clean_date(d):
        if str(d).lower() in ('nan', 'none', 'nat', '', 'null'):
            return None
        return d

    params = (
        track_code,
        clean_value(status_yiwu), clean_date(date_yiwu),
        clean_value(status_dushanbe), clean_date(date_dushanbe),
        clean_value(status_delivered), clean_date(date_delivered),
        track_code,
    )

    q = f"""
        INSERT INTO {ORDERS_TABLE} (
            track_code, status_yiwu, date_yiwu, status_dushanbe, date_dushanbe,
            status_delivered, date_delivered
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (track_code) DO UPDATE SET
            status_yiwu = EXCLUDED.status_yiwu,
            date_yiwu = EXCLUDED.date_yiwu,
            status_dushanbe = EXCLUDED.status_dushanbe,
            date_dushanbe = EXCLUDED.date_dushanbe,
            status_delivered = CASE
                WHEN {ORDERS_TABLE}.status_delivered = 'Запрошена' THEN 'Запрошена'
                WHEN {ORDERS_TABLE}.status_delivered = 'Доставлен' THEN 'Доставлен'
                ELSE EXCLUDED.status_delivered
            END,
            date_delivered = CASE
                WHEN {ORDERS_TABLE}.status_delivered = 'Запрошена' THEN {ORDERS_TABLE}.date_delivered
                WHEN {ORDERS_TABLE}.status_delivered = 'Доставлен' THEN {ORDERS_TABLE}.date_delivered
                ELSE EXCLUDED.date_delivered
            END
        RETURNING track_code,
                  (SELECT user_id IS NULL FROM {ORDERS_TABLE} WHERE track_code = %s) AS was_unlinked
    """

    logger.debug(f"DB upsert: {track_code}")
    return await asyncio.to_thread(execute_query, q, params, fetchone=True, commit=True)


async def request_delivery(track_code, address=None):
    await request_delivery_for_order(track_code)
    return True


async def request_delivery_multiple(track_codes, address):
    success = 0
    for code in track_codes:
        if await request_delivery_for_order(code):
            success += 1
    return success == len(track_codes)


async def get_delivery_requests():
    q = f"""
        SELECT o.track_code, u.user_id, u.full_name, u.phone_number, u.address
        FROM {ORDERS_TABLE} o
        JOIN {USERS_TABLE} u ON o.user_id = u.user_id
        WHERE o.status_delivered = 'Запрошена'
        ORDER BY o.date_dushanbe DESC;
    """
    return await asyncio.to_thread(execute_query, q, fetchall=True)


async def confirm_delivery(track_codes):
    q = f"""
        UPDATE {ORDERS_TABLE}
        SET status_delivered = 'Доставлен',
            date_delivered = CURRENT_DATE,
            notify_delivered = FALSE
        WHERE track_code = ANY(%s)
        RETURNING track_code;
    """
    res = await asyncio.to_thread(execute_query, q, (track_codes,), fetchall=True, commit=True)
    return [r['track_code'] for r in res] if res else []


async def get_delivered_orders_paginated(page=1, per_page=10):
    offset = (page - 1) * per_page
    q = f"""
        SELECT o.track_code, o.date_delivered, u.full_name, u.phone_number
        FROM {ORDERS_TABLE} o
        JOIN {USERS_TABLE} u ON o.user_id = u.user_id
        WHERE o.status_delivered = 'Доставлен'
        ORDER BY o.date_delivered DESC
        LIMIT %s OFFSET %s;
    """
    return await asyncio.to_thread(execute_query, q, (per_page, offset), fetchall=True)


async def get_delivered_orders_count():
    q = f"SELECT COUNT(*) AS cnt FROM {ORDERS_TABLE} WHERE status_delivered = 'Доставлен';"
    res = await asyncio.to_thread(execute_query, q, fetchone=True)
    return res['cnt'] if res else 0


async def get_delivered_orders():
    q = f"""
        SELECT o.track_code, o.date_delivered, u.full_name
        FROM {ORDERS_TABLE} o
        JOIN {USERS_TABLE} u ON o.user_id = u.user_id
        WHERE o.status_delivered = 'Доставлен'
        ORDER BY o.date_delivered DESC;
    """
    return await asyncio.to_thread(execute_query, q, fetchall=True)


async def admin_upsert_order(track_code, status, date_yiwu, date_dushanbe, owner_id=None):
    from datetime import datetime
    status_yiwu = status if status in ('Yiwu', 'В Иу', 'Иу') else None
    status_dushanbe = status if status in ('Dushanbe', 'В Душанбе', 'Душанбе') else None

    status_delivered = None
    date_delivered = None
    if status in ('Delivered', 'Доставлен'):
        status_delivered = 'Доставлен'
        date_delivered = datetime.now().date()

    q = f"""
        INSERT INTO {ORDERS_TABLE} (
            track_code, user_id,
            status_yiwu, date_yiwu,
            status_dushanbe, date_dushanbe,
            status_delivered, date_delivered
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (track_code) DO UPDATE SET
            user_id = EXCLUDED.user_id,
            status_yiwu = EXCLUDED.status_yiwu,
            date_yiwu = EXCLUDED.date_yiwu,
            status_dushanbe = EXCLUDED.status_dushanbe,
            date_dushanbe = EXCLUDED.date_dushanbe,
            status_delivered = EXCLUDED.status_delivered,
            date_delivered = EXCLUDED.date_delivered
        RETURNING track_code;
    """
    params = (track_code, owner_id, status_yiwu, date_yiwu,
              status_dushanbe, date_dushanbe, status_delivered, date_delivered)
    res = await asyncio.to_thread(execute_query, q, params, fetchone=True, commit=True)
    return bool(res)


async def mark_order_delivered_by_code(track_code):
    return await mark_order_as_delivered(track_code)
