from functools import wraps
import os
import sys
import logging
import re
from telebot import apihelper
from requests.exceptions import ConnectionError, ReadTimeout

from handlers import multi_messages, docs
from models.voice_proccesing import (
    download_voice_as_ogg,
    convert_ogg_to_mp3,
)
from models.speech_synthesis import synthesize_text
from keyboards import (
    MAIN_MARKUP,
    MENU_MARKUP,
    GROUP_MAIN_MARKUP,
    GROUP_DOC_MARKUP,
    DOC_MARKUP,
    GROUP_AUDIO_MARKUP,
    AUDIO_MARKUP,
    TAKE_PAY
)

from core import bot, bot_name, send_except, say_my_name, BOT_TOKEN
from handlers import admin_panel
import settings


# Использование Telegram Api Server
apihelper.API_URL = "http://localhost:8081/bot{0}/{1}"
apihelper.FILE_URL = "http://localhost:8081/file/bot{0}/{1}"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

"""Decorators."""


def check_private_chat(func):
    @wraps(func)
    def wrapped(message):
        if message.chat.type == 'private':
            return func(message)
        return

    return wrapped


def restricted(func):
    """Доступ к функции только у разрешенных юзеров, если settings.PER_MODE=True."""
    @wraps(func)
    def wrapped(message):
        user_id = message.chat.id
        if message.chat.type == 'private':
            if settings.PER_MODE and user_id not in settings.ALLOWED_USERS:
                bot.send_message(user_id, f'Этот бот доступен толко по прямому разрешению', reply_markup=TAKE_PAY)
                logger.error(f'Попытка общения с ботом от {user_id}')
                return
        return func(message)

    return wrapped


def send_action(action='typing'):
    """Отправляет 'действие' во время обработки команды."""

    def decorator(func):
        @wraps(func)
        def command_func(message):
            chat_id = message.chat.id
            bot.send_chat_action(chat_id, action)
            return func(message)

        return command_func

    return decorator


"""Handlers."""


@bot.message_handler(commands=['admin'])
@admin_panel.admin_per
def admin_mode(message):
    response = "Меню редактирования бота"
    bot.send_message(message.chat.id, response, reply_markup=MENU_MARKUP)


@bot.message_handler(commands=['start'])
@restricted
def start_message(message):
    """Обработчик команды /start"""

    settings.State.set_state(str(message.chat.id), 'main')

    bot.send_chat_action(message.chat.id, "typing")
    response = 'Здравствуйте! Чем я могу вам помочь?'
    bot.send_message(message.chat.id, response)
    logger.info(f"User {message.chat.id}: sent /start command")


@send_action
@bot.message_handler(func=lambda message: True if bot_name in message.text else False)
@restricted
def text_group_message(message):
    """Обработчик групповых текстовых сообщений."""
    user_id = message.chat.id
    user_message = re.sub(bot_name, '', message.text)
    user_key = str(user_id)

    state, prefix = settings.State.get_state_and_prefix(user_key)

    if 'Очисти историю' in user_message or 'Выйти из режима' in user_message:
        try:
            settings.State.set_state(user_key, 'main')
            settings.CURRENT_MODE.messages_db.pop(user_key)
            bot.send_message(message.chat.id, 'Успешно', reply_markup=GROUP_MAIN_MARKUP)
        except:
            bot.send_message(message.chat.id, 'Уже очищено', reply_markup=GROUP_MAIN_MARKUP)
        return

    msg = bot.send_message(message.chat.id, 'Думаю над ответом 💭')
    bot.send_chat_action(user_id, "typing")

    try:
        response = settings.CURRENT_MODE.get_response(user_id, user_message)
        bot.delete_message(user_id, msg.message_id)
        bot.send_message(user_id, f'{prefix}{response}',
                         reply_markup=settings.GROUP_STATES_BTN[state])
    except Exception as e:
        settings.State.set_state(user_key, 'main')
        logger.error(f"Error occurred: {e}")
        send_except(e, say_my_name())


@send_action
@bot.message_handler(func=lambda message: True)
@restricted
@check_private_chat
def text_message(message):
    """Обработчик личных текстовых сообщений."""

    user_id = message.chat.id
    user_message = message.text
    user_key = str(user_id)

    state, prefix = settings.State.get_state_and_prefix(user_key)

    if user_message in ('Очисти историю', 'Выйти из режима документа', 'Выйти из режима диктофона'):
        try:
            settings.State.set_state(user_key, 'main')
            settings.CURRENT_MODE.messages_db.pop(user_key)
            bot.send_message(message.chat.id, 'Успешно', reply_markup=MAIN_MARKUP)
        except:
            bot.send_message(message.chat.id, 'Уже очищено')
        return

    msg = bot.send_message(message.chat.id, 'Думаю над ответом 💭')
    bot.send_chat_action(user_id, "typing")

    try:
        response = settings.CURRENT_MODE.get_response(
            user_id, user_message
        )
        bot.delete_message(user_id, msg.message_id)
        bot.send_message(user_id, f'{prefix}{response}',
                         reply_markup=settings.STATES_BTN[state],
                         parse_mode="Markdown")

        multi_messages.set_default()
    except Exception as e:
        settings.State.set_state(user_key, 'main')
        logger.error(f"Error occurred: {e}")
        send_except(e, say_my_name())


@bot.message_handler(content_types=["voice"])
@check_private_chat
def voice_message_handler(message):
    user_id = message.chat.id

    msg = bot.send_message(message.chat.id, 'Слушаю вопрос 🎶')

    file_info = bot.get_file(message.voice.file_id)
    converted_file_path = convert_ogg_to_mp3(file_info.file_path)

    try:
        text = settings.CALLBACK_TO_MODES['3.5_tur'].convert_speech_to_text(converted_file_path)
        if 'пиши' not in text and 'текст' not in text:
            bot.edit_message_text(chat_id=user_id, text='Записываю ответ', message_id=msg.message_id)
            bot.send_chat_action(user_id, 'record_audio')

            response = settings.CURRENT_MODE.get_response(user_id, text)

            voice = synthesize_text(response)

            if voice:
                bot.delete_message(user_id, msg.id)
                bot.send_voice(user_id, voice)
            else:
                bot.edit_message_text(chat_id=user_id, text=response, message_id=msg.message_id)

        else:
            bot.edit_message_text(chat_id=user_id, text='Думаю над ответом 💭', message_id=msg.message_id)
            bot.send_chat_action(user_id, 'typing')

            response = settings.CURRENT_MODE.get_response(user_id, text)

            bot.edit_message_text(chat_id=user_id, text=response, message_id=msg.message_id,
                                  parse_mode="Markdown")

    except Exception as e:
        text_message(message)
        logger.error(f"Error occurred: {e}")
        send_except(e, say_my_name())

    finally:
        os.remove(converted_file_path)


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    user_id = message.chat.id
    user_key = str(user_id)

    is_doc = message.chat.type == "group"

    if settings.CURRENT_MODE.__str__() != "Claude":
        bot.send_message(user_id, 'Режим документа пока доступен только в Claude')
        return
    msg = bot.send_message(message.chat.id, 'Начинаю сканировать файл...')

    try:
        text = docs.doc_parser(message)

        if settings.State.get_state_and_prefix(user_key)[1] == "set_prompt":
            with open(settings.PROMPT_DIR, 'w') as f:
                f.write(text)
            settings.CURRENT_MODE.messages_db = {}
            bot.send_message(message.chat.id, '✅ Вы успешно поменяли промпт')
            logger.info(f"Admin changed prompt, messages_db cleared")
            settings.State.set_state(user_key, 'main')
            return
        
        if settings.CURRENT_MODE.get_tokens(user_key) > settings.MAX_TOKENS:
            bot.send_message(user_id, '⚠️ Слишком большой документ! ⚠️')
            settings.CURRENT_MODE.messages_db.pop(user_key)
            return

        settings.CURRENT_MODE.set_fast_prompt(user_id, text)
        settings.State.set_state(user_key, 'doc')

        with open(settings.get_prompt_audio(), 'r') as f:
            start_text = f.read()

        response = settings.CURRENT_MODE.get_response(user_id, start_text)

        keyboard = GROUP_DOC_MARKUP if is_doc else DOC_MARKUP

        bot.delete_message(user_id, msg.message_id)

        bot.send_message(user_id, response, parse_mode='Markdown')
        bot.send_message(message.chat.id,
                         '✅ Сканирование завершено \n'
                         'Режим работы: документ \n'
                         f'(Занято {settings.CURRENT_MODE.get_tokens(user_key)} токенов) \n\n'
                         'Какие у вас будут вопросы по текущему документу? ',
                         reply_markup=keyboard,
                         )
        logger.info(f"Doc mode, messages_db cleared")

        if os.path.exists('document.doc'):
            os.remove('document.doc')
        else:
            logger.info("The file does not exist")

    except Exception as e:
        bot.reply_to(message, e)


"""Режим диктофона"""


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    user_id = message.chat.id
    user_key = str(user_id)

    if settings.CURRENT_MODE.__str__() != "Claude":
        bot.send_message(user_id, 'Режим документа пока доступен только в Claude')
        return
    msg = bot.send_message(message.chat.id, 'Начинаю сканировать аудиофайл...')

    is_doc = message.chat.type == "group"

    settings.State.set_state(user_key, 'audio')

    try:
        file_info = bot.get_file(message.audio.file_id)
        logging.info("Файл скачан")
        file_path = file_info.file_path
    except Exception as e:
        logging.info(f"error: {e}")
        return

    logging.info(f'file_path: {file_path}')
    file_extension = os.path.splitext(file_path)[1]
    logging.info(f'file_extension: {file_extension}')

    if file_extension.lower() in settings.SUPPORTED_FORMATS:
        mp3_filepath = file_path if file_extension.lower() == '.mp3' else convert_ogg_to_mp3(file_path)
        text = settings.CALLBACK_TO_MODES['3.5_tur'].process_audio_file(mp3_filepath, bot, msg)

        if settings.CURRENT_MODE.get_tokens(user_key) > settings.MAX_TOKENS:
            bot.send_message(user_id, '⚠️ Слишком большой аудиофайл! ⚠️')
            settings.CURRENT_MODE.messages_db.pop(user_key)
            return

        with open(settings.get_prompt_audio(), 'r') as f:
            start_text = f.read()
            settings.CURRENT_MODE.set_fast_prompt(user_id, text)
            response = settings.CURRENT_MODE.get_response(user_id, start_text)

        keyboard = GROUP_AUDIO_MARKUP if is_doc else AUDIO_MARKUP

        bot.delete_message(user_id, msg.message_id)

        bot.send_message(user_id, response, parse_mode='Markdown')
        bot.send_message(message.chat.id,
                         '✅ Сканирование завершено \n'
                         'Режим работы: диктофон \n'
                         f'(Занято {settings.CURRENT_MODE.get_tokens(user_key)} токенов) \n\n'
                         'Какие у вас будут вопросы по текущему аудиофайлу? ',
                         reply_markup=keyboard,
                         )
        doc_path = docs.create_word_document(user_key, text)
        bot.send_document(user_id, document=open(doc_path, 'rb'))
        os.remove(doc_path)
        logger.info(f"Admin changed prompt, messages_db cleared")

    else:
        bot.reply_to(message, 'Неподдерживаемый формат файла.')


if __name__ == '__main__':
    try:
        bot.infinity_polling(timeout=1000)
    except (ConnectionError, ReadTimeout) as e:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)
    else:
        bot.infinity_polling(timeout=1000)
