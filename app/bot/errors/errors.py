from aiogram.exceptions import TelegramAPIError, TelegramBadRequest


class UserIsAnAdministratorError(TelegramBadRequest):
    message = "Bad Request: user is an administrator of the chat"


class CantRestrictSelfError(TelegramBadRequest):
    message = "Bad Request: can't restrict self"


class NotEnoughRightsError(TelegramBadRequest):
    message = "Bad Request: not enough rights"


class NotEnoughRightsToRestrictError(TelegramBadRequest):
    message = "Bad Request: not enough rights to restrict/unrestrict chat member"


class TopicClosedError(TelegramBadRequest):
    message = "Bad Request: TOPIC_CLOSED"


def resolve_exception(exception: TelegramAPIError) -> TelegramAPIError:
    match exception.message:
        case UserIsAnAdministratorError.message as message:
            return UserIsAnAdministratorError(method=exception.method, message=message)

        case CantRestrictSelfError.message as message:
            return CantRestrictSelfError(method=exception.method, message=message)

        case NotEnoughRightsError.message as message:
            return NotEnoughRightsError(method=exception.method, message=message)

        case NotEnoughRightsToRestrictError.message as message:
            return NotEnoughRightsToRestrictError(method=exception.method, message=message)

        case TopicClosedError.message as message:
            return TopicClosedError(method=exception.method, message=message)

        case _:
            return exception
