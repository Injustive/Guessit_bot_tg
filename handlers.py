from aiogram import types
import asyncio

from selenium.common.exceptions import TimeoutException

from loader import dp
from utils.fsm import LoginState, RegistrationState, LearnState
from utils.keyboards import get_kb, cancel_kb, get_word_stat_kb
from aiogram.dispatcher import FSMContext
from utils.queries_to_server import login_user, register_user, user_logout, get_next_word, send_stat, get_word_stat
from utils.text_parsers import registration_response_parser, example_text_parser
from utils.handlers_utils import delete_message
from utils.audio import get_voice
from utils.screen import make_screen
from errors import NoUserTokenError, NoWordsError, BadStatusError
from loader import bot
from utils.emojis import *

SITE_URL = 'https://guessit-space.herokuapp.com/'


@dp.message_handler(commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(f'Привет {EMOJI_HELLO}! Я бот для изучения английского языка, '
                         f'выбери действие ниже, чтобы начать изучение {EMOJI_DOWN_ARROW*3}\n'
                         f'Сайт бота - [Guessit]({SITE_URL}) {EMOJI_LEFT_ARROW}',
                         reply_markup=await get_kb(message.from_user.id),
                         parse_mode='Markdown')


@dp.message_handler(commands=['Отмена'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(text="login", state='*')
async def login(call: types.CallbackQuery):

    state = dp.current_state(user=call.from_user.id)
    await state.reset_state()
    await call.answer()
    await call.message.answer(f'Введите имя пользователя:', reply_markup=cancel_kb)
    await LoginState.next()


@dp.message_handler(state=LoginState.waiting_for_username)
async def username_chosen(message: types.Message, state: FSMContext):

    await state.update_data(chosen_username=message.text)
    await message.answer('Введите пароль:')
    await LoginState.next()


@dp.message_handler(state=LoginState.waiting_for_password)
async def password_chosen(message: types.Message, state: FSMContext):

    await state.update_data(chosen_password=message.text)
    user_data = await state.get_data()
    response = await login_user(
        message.from_user.id,
        user_data.get('chosen_username'),
        user_data.get('chosen_password')
    )
    if response == 200:
        await message.answer(f"Поздравляю, вы успешно вошли, {user_data.get('chosen_username')} {EMOJI_HELLO}",
                             reply_markup=await get_kb(message.from_user.id))
    else:
        await message.answer("Похоже, данного пользователя не существует, "
                             "проверьте правильность написания данных и попробуйте снова",
                             reply_markup=await get_kb(message.from_user.id))
    await state.finish()


@dp.callback_query_handler(text="register", state='*')
async def registration(call: types.CallbackQuery):

    state = dp.current_state(user=call.from_user.id)
    await state.reset_state()
    await call.answer()
    await call.message.answer(f'Введите имя пользователя:', reply_markup=cancel_kb)
    await RegistrationState.next()


@dp.message_handler(state=RegistrationState.waiting_for_username)
async def username_chosen(message: types.Message, state: FSMContext):

    await state.update_data(username=message.text)
    await message.answer('Введите email:', reply_markup=cancel_kb)
    await RegistrationState.next()


@dp.message_handler(state=RegistrationState.waiting_for_email)
async def email_chosen(message: types.Message, state: FSMContext):

    await state.update_data(email=message.text)
    await message.answer('Введите пароль:', reply_markup=cancel_kb)
    await RegistrationState.next()


@dp.message_handler(state=RegistrationState.waiting_for_password)
async def password_chosen(message: types.Message, state: FSMContext):

    await state.update_data(password=message.text)
    await message.answer('Введите пароль повторно:', reply_markup=cancel_kb)
    await RegistrationState.next()


@dp.message_handler(state=RegistrationState.waiting_for_password2)
async def password2_chosen(message: types.Message, state: FSMContext):

    await state.update_data(password2=message.text)
    user_data = await state.get_data()
    response = await register_user(**user_data)
    if not response == 200:
        await message.answer(registration_response_parser(response),
                             reply_markup=await get_kb(message.from_user.id),
                             parse_mode='Markdown')
    else:
        await message.answer(f'Вы успешно зарегистрировались {EMOJI_FIRE}, теперь войдите',
                             reply_markup=await get_kb(message.from_user.id))
    await state.finish()


@dp.callback_query_handler(text="logout", state='*')
async def logout(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)
    await state.reset_state()
    await call.answer()
    await user_logout(call.from_user.id)
    await call.message.answer('Вы успешно вышли!', reply_markup=await get_kb(call.from_user.id))


@dp.callback_query_handler(text="learn", state='*')
async def learn(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)
    await state.reset_state()
    await call.answer()
    await call.message.answer('Выберите тип слов для изучения: \n/all_words - все слова \n/own_words - свои слова')
    await LearnState.waiting_for_words_type.set()


@dp.message_handler(state=LearnState.waiting_for_words_type)
async def learn_words(message: types.Message, state: FSMContext):

    data = await state.get_data()
    if not data.get('words_type'):
        await state.update_data(words_type=message.text)

    try:
        result = await get_next_word(message.from_user.id, (await state.get_data()).get('words_type') == '/own_words')
    except NoUserTokenError:
        await message.answer('Похоже, что вы не вошли. Сначала войдите',
                             reply_markup=await get_kb(message.from_user.id))
        return
    except NoWordsError:
        await message.answer(f"У вас еще нет своих слов! Войдите на наш сайт [Guessit]({SITE_URL}) и добавьте их",
                             reply_markup=await get_kb(message.from_user.id), parse_mode='Markdown')
        return

    if data.get('first_call', True):
        await message.answer(f'Начинаем {EMOJI_FIRE}! Введите перевод слова:')
    await asyncio.sleep(1)

    status = result[0]
    response = result[1]
    if not status == 200:
        await message.answer(f'Что-то пошло не так {EMOJI_CROSS_MARK}, попробуйте позже...')
        return

    word = response.get('word')
    tenses = response.get('tenses')
    word_translation = word.get('translation')
    word_id = word.get('id')

    await message.answer(
        f'*{word_translation}*',
        reply_markup=get_word_stat_kb(word_id),
        parse_mode='Markdown'
    )
    await state.update_data(first_call=False)
    await state.update_data(correct=True)
    await state.update_data(word=word, tenses=tenses)
    await LearnState.waiting_for_word.set()


@dp.message_handler(state=LearnState.waiting_for_word)
async def check_word(message: types.Message, state: FSMContext):

    user_data = await state.get_data()
    word = user_data.get('word')
    tenses = user_data.get('tenses')
    if not word.get('word') == message.text.lower():
        await state.update_data(correct=False)
        await delete_message(message, 0)
        msg = await message.answer(word.get('word'))
        await delete_message(msg, 1.5)
    else:
        is_correct = (await state.get_data())['correct']
        word_id = word.get('id')
        word_word = word.get('word')
        word_rusex = word.get('rusex')
        word_engex = word.get('engex')
        await send_stat(message.from_user.id, word_id, is_correct)

        word_engex_parsed = example_text_parser(word_word, tenses, word_engex)

        await bot.send_voice(message.from_user.id, get_voice(word_word))
        await message.answer(f"{word_engex_parsed}\n{word_rusex}")
        await bot.send_voice(message.from_user.id, get_voice(word_engex))
        await learn_words(message, state)


@dp.callback_query_handler(text="stat", state='*')
async def stat(call: types.CallbackQuery):

    state = dp.current_state(user=call.from_user.id)
    await state.reset_state()
    await call.answer()
    await call.message.answer('Подождите, это может занять некоторое время...')
    try:
        png = await make_screen(call.from_user.id, 'stat/', (247, 80, 1020, 1360), True)
    except (BadStatusError, TimeoutException):
        await call.message.answer('Что-то пошло не так, попробуйте еще раз...')

    await bot.send_photo(call.from_user.id, png.getvalue())


@dp.callback_query_handler(lambda call: call.data.startswith('stat_'), state='*')
async def stat(call: types.CallbackQuery):
    await call.answer()
    word_id = call.data.replace('stat_', '')
    status = await get_word_stat(call.from_user.id, word_id)
    if not status == 200:
        await call.message.answer(f'Еще нет статистики для этого слова {EMOJI_CROSS_MARK}! '
                                  f'Впишите ответ, чтобы начать учет статистики')
        return
    await call.message.answer('Подождите, это может занять некоторое время...')

    try:
        png = await make_screen(call.from_user.id, f'words/word_stat/{word_id}/', (200, 80, 1083, 575), False)
    except (BadStatusError, TimeoutException):
        await call.message.answer(f'Что-то пошло не так {EMOJI_CROSS_MARK}, попробуйте еще раз...')
    await bot.send_photo(call.from_user.id, png.getvalue())