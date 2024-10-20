from django.conf import settings

from bot import bot, logger


def start_message(message):
    """Обработчик команды /start"""

    bot.send_chat_action(message.chat.id, "typing")
    response = 'Здравствуйте! Чем я могу вам помочь?'
    bot.send_message(message.chat.id, response)
    logger.info(f"User {message.chat.id}: sent /start command")
