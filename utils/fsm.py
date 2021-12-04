from aiogram.dispatcher.filters.state import State, StatesGroup


class LoginState(StatesGroup):

    waiting_for_username = State()
    waiting_for_password = State()


class RegistrationState(StatesGroup):

    waiting_for_username = State()
    waiting_for_email = State()
    waiting_for_password = State()
    waiting_for_password2 = State()


class LearnState(StatesGroup):

    waiting_for_words_type = State()
    waiting_for_word = State()
