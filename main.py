import logging

from telethon import TelegramClient, events

from src.handlers.commands import help_cmd_handler, msg_handler, start_cmd_handler, list_handler, track_handler, untrack_handler, unknown_command_handler
from src.handlers.chat_id import chat_id_cmd_handler
from src.settings import settings

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

from enum import Enum


class BotCommand(Enum):
    """Перечисление команд, поддерживаемых Telegram-ботом.

    Содержит список фиксированных команд, которые бот распознаёт и обрабатывает.
    Каждая команда представлена строковым значением, начинающимся c символа '/'.

    :ivar START: Команда для регистрации пользователя.
    :ivar HELP: Команда для отображения справки.
    :ivar TRACK: Команда для начала отслеживания ссылки.
    :ivar UNTRACK: Команда для прекращения отслеживания ссылки.
    :ivar LIST: Команда для вывода списка отслеживаемых ссылок.
    :ivar CHAT_ID: Команда для получения ID чата.
    """

    START = "/start"
    HELP = "/help"
    TRACK = "/track"
    UNTRACK = "/untrack"
    LIST = "/list"
    CHAT_ID = "/chat_id"

def main() -> None:

    """Инициализирует и запускает Telegram-бота c использованием Telethon.

    Создаёт и настраивает TelegramClient c использованием настроек бота.
    Регистрирует обработчики событий для известных команд (определённых в BotCommand).
    Регистрирует обработчик для неизвестных команд и общий обработчик для сообщений.
    Запускает цикл получения сооб щений от пользователей до отключения клиента.

    :return: None
    """
    logger.info("Run the event loop to start receiving messages")

    client = TelegramClient("bot_session", settings.api_id, settings.api_hash).start(
        bot_token= settings.token,
    )

    command_handlers = {
        BotCommand.CHAT_ID.value: chat_id_cmd_handler,
        BotCommand.START.value: start_cmd_handler,
        BotCommand.HELP.value: help_cmd_handler,
        BotCommand.TRACK.value: track_handler,
        BotCommand.UNTRACK.value: untrack_handler,
        BotCommand.LIST.value: list_handler,
    }

    for command, handler in command_handlers.items():
        client.add_event_handler(handler, events.NewMessage(pattern=rf"^{command}"))

    excluded_commands = "|".join(cmd.name.lower() for cmd in BotCommand)
    client.add_event_handler(
        unknown_command_handler,
        events.NewMessage(pattern=rf"/(?!{excluded_commands})\w+"),
    )

    client.add_event_handler(msg_handler, events.NewMessage(pattern=r"^[^/]"))

    with client:
        try:
            client.run_until_disconnected()
        except KeyboardInterrupt:
            pass

        except Exception as exc:
            logger.exception(
                "Main loop raised error.",
                extra={"exc": exc},
            )


if __name__ == "__main__":

    main()