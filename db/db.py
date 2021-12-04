import asyncpg
from utils.db_queries import *
from loggers_control.loggers import db_logger
import socket
from functools import wraps
import os

POSTGRES_NAME = os.getenv('POSTGRES_NAME')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PSW = os.getenv('POSTGRES_PSW')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')

DSN = f'postgresql://{POSTGRES_USER}:{POSTGRES_PSW}@{POSTGRES_HOST}/{POSTGRES_NAME}'


def connect_db(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                conn = await asyncpg.connect(DSN)
                await conn.execute(CREATE_TABLE_QUERY)
                return await func(conn, *args, **kwargs)
            except socket.gaierror as err:  # Ошибки связанные с адресами, для getaddrinfo() и getnameinfo()
                pass
                db_logger.error(f"Пользователю не удалось подключиться к БД. Причина - {err}")
        return wrapper


@connect_db
async def write_token(conn, user_id, access, refresh):
    await conn.execute(INSERT_OR_UPDATE_TOKEN_QUERY, user_id, access, refresh)


@connect_db
async def get_token(conn, user_id):
    tokens = await conn.fetch(GET_TOKENS_QUERY, user_id)
    if tokens:
        return {'access': tokens[0]['access'], 'refresh': tokens[0]['refresh']}


@connect_db
async def clear_token(conn, user_id):
    await conn.execute(CLEAR_TOKENS_QUERY, user_id)


@connect_db
async def write_access_token(conn, access, refresh):
    await conn.execute(WRITE_ACCESS_TOKEN_QUERY, access, refresh)