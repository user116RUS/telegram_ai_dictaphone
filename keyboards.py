from telebot.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup,
                           KeyboardButton,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)

from core import bot_name


"""InlineKeyboards"""


VOICE_CHOOSE_MARKUP = InlineKeyboardMarkup(row_width=2)
VC_BUTTON_1 = InlineKeyboardButton(text='Наталья', callback_data='наталья')
VC_BUTTON_2 = InlineKeyboardButton(text='Борис', callback_data='борис')
VC_BUTTON_3 = InlineKeyboardButton(text='Марфа', callback_data='марфа')
VC_BUTTON_4 = InlineKeyboardButton(text='Тарас', callback_data='тарас')
VC_BUTTON_5 = InlineKeyboardButton(text='Александра', callback_data='александра')
VC_BUTTON_6 = InlineKeyboardButton(text='Сергей', callback_data='сергей')
VC_BUTTON_7 = InlineKeyboardButton(text='Kira (EN)', callback_data='kira (EN)')
VC_BUTTON_BACK = InlineKeyboardButton(text='🔙', callback_data='admin')
VOICE_CHOOSE_MARKUP.add(
    VC_BUTTON_1,
    VC_BUTTON_2, 
    VC_BUTTON_3,
    VC_BUTTON_4,
    VC_BUTTON_5,
    VC_BUTTON_6,
    VC_BUTTON_7
).add(VC_BUTTON_BACK)

MODE_CHOOSE_MARKUP = InlineKeyboardMarkup(row_width=2)

CL_13_100k = InlineKeyboardButton(text='claude-1.3-100k', callback_data='cl-1.3_100k')
CL_I_11_100k = InlineKeyboardButton(text='claude-instant-1.1-100k', callback_data='cl-i_1.1_100k')
CL_1 = InlineKeyboardButton(text='claude-2', callback_data='cl-2')

GPT_3_5_TUR = InlineKeyboardButton(text='GPT-3.5-turbo', callback_data='gpt-3.5_tur')
GPT_4 = InlineKeyboardButton(text='GPT-4', callback_data='gpt-4')
GPT_3_5_TUR_16K = InlineKeyboardButton(text='GPT-3.5-tur16k', callback_data='gpt-3.5_tur16')

MC_BUTTON_BACK = InlineKeyboardButton(text='🔙', callback_data='admin')
MODE_CHOOSE_MARKUP.add(CL_1, GPT_3_5_TUR, CL_13_100k, GPT_3_5_TUR_16K, CL_I_11_100k, GPT_4).add(MC_BUTTON_BACK)

MENU_MARKUP = InlineKeyboardMarkup(row_width=2)
PROMPT_BUTTON = InlineKeyboardButton(text='Новый промпт 📝', callback_data='prompt')
PROMPT_DOC_BUTTON = InlineKeyboardButton(text='Новый промпт(Режим Документа) 📝', callback_data='prompt_doc')
PROMPT_AUDIO_BUTTON = InlineKeyboardButton(text='Новый промпт(Режим Диктофона) 📝', callback_data='prompt_audio')
VOICE_CHOOSE_BUTTON = InlineKeyboardButton(text='Выбрать голос 🗣', callback_data='voice')
MODE_CHOOSE_BUTTON = InlineKeyboardButton(text='Выбрать ИИ 🤖', callback_data='mode')
ADD_USERS = InlineKeyboardButton(text='Список пользователей', callback_data='add_users')
MENU_MARKUP.add(
    MODE_CHOOSE_BUTTON,
    VOICE_CHOOSE_BUTTON,
    PROMPT_BUTTON
).add(PROMPT_DOC_BUTTON).add(PROMPT_AUDIO_BUTTON).add(ADD_USERS)

CHANGE_USERS = InlineKeyboardMarkup()
CHANGE_USER = InlineKeyboardButton(text="Изменить список", callback_data="change_users")
CHANGE_USERS.add(CHANGE_USER).add().add(VC_BUTTON_BACK)


ANTHROPIC_MODELS = InlineKeyboardMarkup(row_width=2)
ANTHROPIC_MODELS.add(CL_13_100k).add(CL_I_11_100k).add(CL_1)


"""ReplyKeyboards"""


MAIN_MARKUP = ReplyKeyboardMarkup(resize_keyboard=True)
CLEAN_PROMPT = KeyboardButton("Очисти историю")
CHECK_TOKENS = KeyboardButton("Сколько токенов потратил?")
MAIN_MARKUP.add(CLEAN_PROMPT)

DOC_MARKUP = ReplyKeyboardMarkup(resize_keyboard=True)
EXIT_DOC = KeyboardButton("Выйти из режима документа")
DOC_MARKUP.add(EXIT_DOC)

GROUP_MAIN_MARKUP = ReplyKeyboardMarkup(resize_keyboard=True)
GR_CLEAN_PROMPT = KeyboardButton(f"{bot_name} Очисти историю")
GROUP_MAIN_MARKUP.add(GR_CLEAN_PROMPT)

GROUP_DOC_MARKUP = ReplyKeyboardMarkup(resize_keyboard=True)
GR_EXIT_DOC = KeyboardButton(f"{bot_name} Выйти из режима документа")
GROUP_DOC_MARKUP.add(GR_EXIT_DOC)

AUDIO_MARKUP = ReplyKeyboardMarkup(resize_keyboard=True)
EXIT_AUDIO = KeyboardButton("Выйти из режима диктофона")
AUDIO_MARKUP.add(EXIT_AUDIO)

GROUP_AUDIO_MARKUP = ReplyKeyboardMarkup(resize_keyboard=True)
GR_EXIT_AUDIO = KeyboardButton(f"{bot_name} Выйти из режима диктофона")
GROUP_AUDIO_MARKUP.add(GR_EXIT_AUDIO)

TAKE_PAY = InlineKeyboardMarkup()
SEND_PAY_REQ = InlineKeyboardButton(text="Сделать запрос на доступ!", callback_data="get_access")
TAKE_PAY.add(SEND_PAY_REQ)

CLEANER = ReplyKeyboardRemove()
