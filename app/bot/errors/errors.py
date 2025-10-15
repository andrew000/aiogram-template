from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError


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


class ChatNotFoundError(TelegramBadRequest):
    message = "Bad Request: chat not found"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: CHAT_RESTRICTED
class ChatRestrictedError(TelegramBadRequest):
    message = "Bad Request: CHAT_RESTRICTED"


# aiogram.exceptions.TelegramForbiddenError: Telegram server says - Forbidden: bot was kicked from
# the supergroup chat
class BotWasKickedFromSuperGroupError(TelegramForbiddenError):
    message = "Forbidden: bot was kicked from the supergroup chat"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: REACTION_INVALID
class ReactionInvalidError(TelegramBadRequest):
    message = "Bad Request: REACTION_INVALID"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: not enough rights to
# send text messages to the chat
class NotEnoughRightsToSendTextError(TelegramBadRequest):
    message = "Bad Request: not enough rights to send text messages to the chat"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: MESSAGE_ID_INVALID
class MessageIdInvalidError(TelegramBadRequest):
    message = "Bad Request: MESSAGE_ID_INVALID"


# aiogram.exceptions.TelegramForbiddenError: Telegram server says - Forbidden: bot was blocked by
# the user
class BotWasBlockedByUserError(TelegramForbiddenError):
    message = "Forbidden: bot was blocked by the user"


# aiogram.exceptions.TelegramForbiddenError: Telegram server says - Forbidden: bot was kicked
# from the group chat
class BotWasKickedFromGroupError(TelegramForbiddenError):
    message = "Forbidden: bot was kicked from the group chat"


# aiogram.exceptions.TelegramForbiddenError: Telegram server says - Forbidden: bot was kicked
# from the channel chat
class BotWasKickedFromChannelError(TelegramForbiddenError):
    message = "Forbidden: bot was kicked from the channel chat"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: channel direct
# messages topic must be specified
class ChannelDirectMessagesTopicMustBeSpecifiedError(TelegramBadRequest):
    message = "Bad Request: channel direct messages topic must be specified"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: can't remove chat owner
class CantRemoveChatOwnerError(TelegramBadRequest):
    message = "Bad Request: can't remove chat owner"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: CHAT_ADMIN_REQUIRED
class ChatAdminRequiredError(TelegramBadRequest):
    message = "Bad Request: CHAT_ADMIN_REQUIRED"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: message to react not
# found
class MessageToReactNotFoundError(TelegramBadRequest):
    message = "Bad Request: message to react not found"


# aiogram.exceptions.TelegramNetworkError: HTTP Client says - Request timeout error
class RequestTimeoutError(TelegramAPIError):
    message = "HTTP Client says - Request timeout error"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: CHAT_WRITE_FORBIDDEN
class ChatWriteForbiddenError(TelegramBadRequest):
    message = "Bad Request: CHAT_WRITE_FORBIDDEN"


# aiogram.exceptions.TelegramForbiddenError: Telegram server says - Forbidden: the group chat was
# deleted
class ChatDeletedError(TelegramForbiddenError):
    message = "Forbidden: the group chat was deleted"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: chat actions can't be
# sent to channel direct messages chats
class ChatActionsForbiddenInChannelDirectMessagesError(TelegramBadRequest):
    message = "Bad Request: chat actions can't be sent to channel direct messages chats"


# aiogram.exceptions.TelegramForbiddenError: Telegram server says - Forbidden: bot is not a member
# of the group chat
class BotNotMemberOfGroupError(TelegramForbiddenError):
    message = "Forbidden: bot is not a member of the group chat"


# aiogram.exceptions.TelegramForbiddenError: Telegram server says - Forbidden: bot is not a member
# of the supergroup chat
class BotNotMemberOfSuperGroupError(TelegramForbiddenError):
    message = "Forbidden: bot is not a member of the supergroup chat"


# aiogram.exceptions.TelegramForbiddenError: Telegram server says - Forbidden: bot is not a member
# of the channel chat
class BotNotMemberOfChannelError(TelegramForbiddenError):
    message = "Forbidden: bot is not a member of the channel chat"


# aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: CHANNEL_PRIVATE
class ChannelPrivateError(TelegramBadRequest):
    message = "Bad Request: CHANNEL_PRIVATE"


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

        case ChatNotFoundError.message as message:
            return ChatNotFoundError(method=exception.method, message=message)

        case ChatRestrictedError.message as message:
            return ChatRestrictedError(method=exception.method, message=message)

        case BotWasBlockedByUserError.message as message:
            return BotWasBlockedByUserError(method=exception.method, message=message)

        case BotWasKickedFromSuperGroupError.message as message:
            return BotWasKickedFromSuperGroupError(method=exception.method, message=message)

        case ReactionInvalidError.message as message:
            return ReactionInvalidError(method=exception.method, message=message)

        case NotEnoughRightsToSendTextError.message as message:
            return NotEnoughRightsToSendTextError(method=exception.method, message=message)

        case MessageIdInvalidError.message as message:
            return MessageIdInvalidError(method=exception.method, message=message)

        case BotWasKickedFromGroupError.message as message:
            return BotWasKickedFromGroupError(method=exception.method, message=message)

        case BotWasKickedFromChannelError.message as message:
            return BotWasKickedFromChannelError(method=exception.method, message=message)

        case ChannelDirectMessagesTopicMustBeSpecifiedError.message as message:
            return ChannelDirectMessagesTopicMustBeSpecifiedError(
                method=exception.method, message=message
            )

        case CantRemoveChatOwnerError.message as message:
            return CantRemoveChatOwnerError(method=exception.method, message=message)

        case ChatAdminRequiredError.message as message:
            return ChatAdminRequiredError(method=exception.method, message=message)

        case MessageToReactNotFoundError.message as message:
            return MessageToReactNotFoundError(method=exception.method, message=message)

        case RequestTimeoutError.message as message:
            return RequestTimeoutError(method=exception.method, message=message)

        case ChatWriteForbiddenError.message as message:
            return ChatWriteForbiddenError(method=exception.method, message=message)

        case ChatDeletedError.message as message:
            return ChatDeletedError(method=exception.method, message=message)

        case ChatActionsForbiddenInChannelDirectMessagesError.message as message:
            return ChatActionsForbiddenInChannelDirectMessagesError(
                method=exception.method, message=message
            )

        case BotNotMemberOfGroupError.message as message:
            return BotNotMemberOfGroupError(method=exception.method, message=message)

        case BotNotMemberOfSuperGroupError.message as message:
            return BotNotMemberOfSuperGroupError(method=exception.method, message=message)

        case BotNotMemberOfChannelError.message as message:
            return BotNotMemberOfChannelError(method=exception.method, message=message)

        case ChannelPrivateError.message as message:
            return ChannelPrivateError(method=exception.method, message=message)

        case _:
            return exception
