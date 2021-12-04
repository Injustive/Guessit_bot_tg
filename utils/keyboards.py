from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from utils.queries_to_server import check_auth


async def get_kb(user_id):
    main_keyboard = InlineKeyboardMarkup()
    auth_status = await check_auth(user_id)
    if auth_status == 200:
        learn_btn = InlineKeyboardButton(text='Изучение', callback_data='learn')
        stat_btn = InlineKeyboardButton(text='Статистика', callback_data='stat')
        logout_btn = InlineKeyboardButton(text='Выйти с аккаунта', callback_data='logout')
        main_keyboard.add(learn_btn, stat_btn, logout_btn)
    else:
        login_btn = InlineKeyboardButton(text='Вход', callback_data='login')
        register_btn = InlineKeyboardButton(text='Регистрация', callback_data='register')
        main_keyboard.add(login_btn, register_btn)
    return main_keyboard


def get_word_stat_kb(word_id):
    word_stat_kb = InlineKeyboardMarkup()
    word_stat_btn = InlineKeyboardButton(text='Статистика слова', callback_data=f'stat_{word_id}')
    word_stat_kb.add(word_stat_btn)
    return word_stat_kb


cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton("/Отмена"))

words_type_kb = InlineKeyboardMarkup()
all_words_btn = InlineKeyboardButton(text='Все слова', callback_data='all_words_learn')
own_words_btn = InlineKeyboardButton(text='Свои слова', callback_data='own_words_learn')
words_type_kb.add(all_words_btn, own_words_btn)