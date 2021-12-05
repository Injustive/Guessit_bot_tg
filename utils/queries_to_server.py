import aiohttp
import json
from db.db import write_token, get_token, clear_token, write_access_token
from errors import NoUserTokenError, NoWordsError, BadStatusError

AUTH_JWT_URL = 'https://guessit-space.herokuapp.com/auth/jwt/'
API_URL = 'https://guessit-space.herokuapp.com/api/'

async def login_user(user_id, username, password):
    data = {'username': username, 'password': password}
    async with aiohttp.ClientSession() as session:
        async with session.post(AUTH_JWT_URL + 'create/', data=data) as response:
            if response.status == 200:
                result = json.loads(await response.text())
                await write_token(user_id, result['access'], result['refresh'])
            return response.status


async def check_auth(user_id):
    tokens = await get_token(user_id)
    if not tokens:
        return
    data = {'token': tokens['refresh']}
    async with aiohttp.ClientSession() as session:
        async with session.post(AUTH_JWT_URL + 'verify/', data=data) as response:
            return response.status


async def register_user(**kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL + 'create_user/', data=kwargs) as response:
            if not response.status == 200:
                result = json.loads(await response.text())
                return result
            return response.status


async def user_logout(user_id):
    await clear_token(user_id)


async def refresh_token(refresh):
    data = {'refresh': refresh}
    async with aiohttp.ClientSession() as session:
        async with session.post(AUTH_JWT_URL + 'refresh/', data=data) as response:
            if response.status == 200:
                result = json.loads(await response.text())
                access = result['access']
                await write_access_token(access, refresh)
                return access
            raise NoUserTokenError


async def get_next_word(user_id, is_own_words=False):
    access = await get_valid_access(user_id)

    endpoint = 'get_next_word/' if not is_own_words else 'get_next_word/?words=own_words'
    headers = {'Authorization': f'Bearer {access}'}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(API_URL + endpoint) as response:
            result = json.loads(await response.text())
            if response.status == 404 and result.get('code') == 'No words':
                raise NoWordsError
            return response.status, result


async def get_valid_access(user_id):
    tokens = await get_token(user_id)

    if not tokens:
        raise NoUserTokenError

    access = tokens['access']
    refresh = tokens['refresh']

    headers = {'Authorization': f'Bearer {access}'}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(API_URL + 'test/') as response:
            if not response.status == 200:
                access = await refresh_token(refresh)
            return access


async def send_stat(user_id, word_id, is_correct):
    access = await get_valid_access(user_id)
    data = {'word_id': word_id, 'is_correct': is_correct}
    headers = {'Authorization': f'Bearer {access}'}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(API_URL + 'get_next_word/', data=data) as response:
            if not response.status == 200:
                raise BadStatusError


async def get_word_stat(user_id, word_id):
    access = await get_valid_access(user_id)
    headers = {'Authorization': f'Bearer {access}'}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(API_URL + f'word_stat/{word_id}/') as response:
            return response.status



