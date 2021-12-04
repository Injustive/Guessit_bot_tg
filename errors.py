class NoUserTokenError(Exception):
    pass


class AccessTokenExpiredError(Exception):
    pass


class NoWordsError(Exception):
    pass


class BadStatusError(Exception):
    pass