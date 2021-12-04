import re


def registration_response_parser(response):
    labels = {'username': 'Имя пользователя', 'password': 'Пароль', 'password2': 'Повторный пароль', 'email': 'Email'}
    result = '\n'.join(
        f"*{labels.get(k, 'Ошибка')}*: {','.join(value.lower() for value in v)}" for k, v in response.items()
    )
    return result


def example_text_parser(user_word, tenses, example):
    example_words = example.split()

    result = ''
    for word in example_words:
        if (word.lower() == user_word) or \
                (word.lower() in tenses) or \
                (re.sub(r"[\s.,%!?']", '', word.lower()) in tenses):
            result += f'<b><u>{word}</u></b> '
            continue
        result += word + ' '
    return result.strip()