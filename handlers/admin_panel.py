from functools import wraps
import logging

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from core import bot, send_except, say_my_name
from handlers import docs
from keyboards import (
    CHANGE_USERS,
    MENU_MARKUP,
    MODE_CHOOSE_MARKUP,
    VOICE_CHOOSE_MARKUP
)
import db_process
import keyboards
import settings


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def admin_per(func):
    @wraps(func)
    def wrapped(message):
        user_id = message.chat.id
        if user_id not in settings.LIST_OF_ADMINS:
            bot.send_message(user_id, f'⛔ У вас нет администраторского доступа')
            logger.error(f'Попытка доступа к админ панели от {user_id}')
            return
        return func(message)

    return wrapped


@bot.callback_query_handler(func=lambda call: call.data in settings.VOICES)
def save_voice(call):
    user_id = call.message.chat.id

    try:
        db_process.update_voice(call.data)
        bot.send_message(user_id, 'Успешный успех ✅')
    except Exception as e:
        bot.send_message(
            user_id,
            f'⛔ Попробуйте еще раз, что то пошло не по плану: {e}'
        )
        send_except(e, say_my_name())


@admin_per
def save_prompt(message):
    try:
        with open(settings.PROMPT_DIR, 'w') as f:
            f.write(message.text if message.text is not None else docs.doc_parser(message))
        settings.CURRENT_MODE.messages_db = {}
        msg = bot.send_message(message.chat.id, '✅ Вы успешно поменяли промпт')
        logger.info(f"Admin changed prompt, messages_db cleared")
    except Exception as e:
        msg = bot.send_message(message.chat.id, f'⛔ что то не то: {e}')
        logger.error(f"Admin could not change prompt. Reason: {e}")
        send_except(e, say_my_name())
    bot.register_next_step_handler(msg, start_message)


@admin_per
def save_prompt_doc(message):
    try:
        with open(settings.PROMPT_DOC_DIR, 'w') as f:
            f.write(message.text)
        msg = bot.send_message(message.chat.id, '✅ Вы успешно поменяли промпт для работы с документами.')
        logger.info(f"Admin changed prompt document mode, messages_db cleared")
    except Exception as e:
        msg = bot.send_message(message.chat.id, f'⛔ что то не то: {e}')
        logger.error(f"Admin could not change prompt. Reason: {e}")
        send_except(e, say_my_name())
    bot.register_next_step_handler(msg, start_message)


@admin_per
def save_prompt_audio(message):
    try:
        with open(settings.PROMPT_AUDIO_DIR, 'w') as f:
            f.write(message.text)
        msg = bot.send_message(message.chat.id, '✅ Вы успешно поменяли промпт для работы с аудиофайлами.')
        logger.info(f"Admin changed prompt audio mode, messages_db cleared")
    except Exception as e:
        msg = bot.send_message(message.chat.id, f'⛔ что то не то: {e}')
        logger.error(f"Admin could not change prompt. Reason: {e}")
        send_except(e, say_my_name())
    bot.register_next_step_handler(msg, start_message)


@bot.message_handler(commands=['admin'])
@admin_per
def admin_mode(message):
    response = "Меню редактирования бота"
    bot.send_message(message.chat.id, response, reply_markup=MENU_MARKUP)


@bot.message_handler(commands=['start'])
def start_message(message):
    """Обработчик команды /start"""

    settings.State.set_state(str(message.chat.id), 'main')

    bot.send_chat_action(message.chat.id, "typing")
    response = 'Здравствуйте! Чем я могу вам помочь?'
    bot.send_message(message.chat.id, response)
    logger.info(f"User {message.chat.id}: sent /start command")


@bot.callback_query_handler(func=lambda call: call.data == 'admin')
def admin_mode_call(call):
    response = "Меню редактирования бота"
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.id,
                          text=response,
                          reply_markup=MENU_MARKUP)


@bot.callback_query_handler(func=lambda call: call.data == 'mode')
def select_model(call):
    response = (f"Сейчас активен {settings.CURRENT_MODE.model}"
                "\nКакую модель выберем? ")
    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=response,
                          reply_markup=MODE_CHOOSE_MARKUP,
                          message_id=call.message.id)


@bot.callback_query_handler(func=lambda call: str(call.data).startswith('cl') or str(call.data).startswith('gpt'))
def select_temp_claude(call):
    ai, cllbck = map(str, call.data.split("-"))
    temp_range = '(-1 ; 1)' if ai == 'cl' else '(0 ; 2)'
    db_process.update_ai_model(cllbck)
    model = settings.CURRENT_MODE = settings.CALLBACK_TO_MODES[db_process.get_ai_model()]
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    msg = bot.send_message(call.message.chat.id, f"Какую температуру выставим для {model.model}? {temp_range}\n"
                                                 f"Сейчас {settings.CHAT_TEMP}")
    bot.register_next_step_handler(msg, set_temp_cl if ai == 'cl' else set_temp_gpt)


def set_temp_cl(message):
    try:
        number = float(message.text)
        if -1 <= number <= 1:
            db_process.update_temperature(str(number))
            bot.reply_to(message, 'Все норм, вы ввели: {}'.format(number))
            settings.CHAT_TEMP = float(number)
        else:
            bot.reply_to(message, 'Минимум -1, максимум 1, default 0.7')
    except ValueError:
        bot.reply_to(message, 'Это не похоже на число. Пожалуйста, попробуйте еще раз.')
        return


def set_temp_gpt(message):
    try:
        number = float(message.text)
        if 0 <= number <= 2:
            db_process.update_temperature(str(number))
            bot.reply_to(message, 'Все норм, вы ввели: {}'.format(number))
            settings.CHAT_TEMP = float(number)
        else:
            bot.reply_to(message, 'Минимум 0, максимум 2, default 1')
    except ValueError:
        bot.reply_to(message, 'Это не похоже на число. Пожалуйста, попробуйте еще раз.')
        return


@bot.callback_query_handler(func=lambda call: call.data == 'prompt')
def new_promt(call):
    response = "Введите новый МЕТАпромпт или отправьте документ: "
    msg = bot.send_message(text=response, chat_id=call.message.chat.id)
    settings.State.set_state(str(call.message.chat.id), 'set_prompt')
    bot.register_next_step_handler(msg, save_prompt)


@bot.callback_query_handler(func=lambda call: call.data == 'prompt_doc')
def new_promt_doc(call):
    response = "Введите новый промпт(Режим Документа): "
    msg = bot.send_message(text=response, chat_id=call.message.chat.id)
    bot.register_next_step_handler(msg, save_prompt_doc)


@bot.callback_query_handler(func=lambda call: call.data == 'prompt_audio')
def new_promt_audio(call):
    response = "Введите новый промпт(Режим Диктофона): "
    msg = bot.send_message(text=response, chat_id=call.message.chat.id)
    bot.register_next_step_handler(msg, save_prompt_audio)


@bot.callback_query_handler(func=lambda call: call.data == 'voice')
def choose_voice(call):
    response = (f"Сейчас активен {settings.CURRENT_VOICE}"
                f"\nКакой голос выберем? ")
    bot.edit_message_text(response,
                          call.message.chat.id,
                          call.message.id,
                          reply_markup=VOICE_CHOOSE_MARKUP)


@admin_per
@bot.callback_query_handler(func=lambda call: call.data == "add_users")
def get_users(call):
    chat_id = call.message.chat.id
    message_id = call.message.id

    bot.delete_message(chat_id, message_id)
    current_users = set(settings.ALLOWED_USERS)
    bot.send_message(
        chat_id=chat_id,
        text="Вот список разрешенных пользователей\n"
             f"{current_users}",
        reply_markup=CHANGE_USERS
    )


@bot.callback_query_handler(func=lambda call: call.data == "change_users")
def change_users(call):
    chat_id = call.message.chat.id

    users_id = set(db_process.get_allowed_users())
    keyboard = InlineKeyboardMarkup()
    for user_id in users_id:
        keyboard.add(InlineKeyboardButton(text=f"❌{user_id}", callback_data=f"del_{user_id}"))

    bot.edit_message_text(
        text="Кого удалим?",
        chat_id=chat_id,
        message_id=call.message.id,
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('del'))
def del_user_from_allowed(call):
    _, user_id = call.data.split('_')
    db_process.remove_allowed_user(user_id)
    settings.ALLOWED_USERS = db_process.get_allowed_users()
    change_users(call)


def send_allow_request(message):
    user_id = message.chat.id
    name = message.chat.username
    user_info = message.text

    CONFIRM_TO_ALLOWED = InlineKeyboardMarkup(row_width=2)
    CONFIRM_TO_ALLOWED.add(
        InlineKeyboardButton(
            text='Да',
            callback_data=f'alw-usr_a_{user_id}'
        ),
        InlineKeyboardButton(
            text='Нет',
            callback_data=f'alw-usr_r_{user_id}'
        )
    )

    bot.send_message(
        settings.ALMAZ_ID,
        f'@{name} хочет стенографию\ntg_id: {user_id}\n\n'
        f'Его инфа: {user_info}\n\n'
        f'Добавляем?',
        reply_markup=CONFIRM_TO_ALLOWED
    )


@bot.callback_query_handler(func=lambda call: str(call.data).startswith('alw-usr'))
def allowed_user_handler(call):
    _, state, user_id = call.data.split('_')

    if state == 'r':
        bot.edit_message_text(
            f'{call.message.text}\Отвергли!',
            call.message.chat.id,
            call.message.id
        )
        msg_text = (
            'Вам не дали доступ!\n' 
            'Причину узнайте у @almazom'
        )
    else:
        bot.edit_message_text(
            f'{call.message.text}\nДобавили!',
            call.message.chat.id,
            call.message.id
        )
        db_process.add_allowed_user(int(user_id))
        msg_text = 'Вам одобрен доступ!'
        settings.ALLOWED_USERS.append(int(user_id))
    bot.send_message(user_id, msg_text, reply_markup=keyboards.CLEANER)


@bot.callback_query_handler(func=lambda call: call.data == 'get_access')
def get_full_access(call):
    msg = bot.edit_message_text(
        text='Напишите Ваши контакты:\n'
             'ФИО и номер телефона',
        chat_id=call.message.chat.id,
        message_id=call.message.id
    )
    bot.register_next_step_handler(msg, send_allow_request)
