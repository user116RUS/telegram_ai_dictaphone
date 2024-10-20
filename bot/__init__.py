import logging
import traceback

import requests
import telebot
from telebot import apihelper

from django.conf import settings

# Создание объекта бота
bot = telebot.TeleBot(settings.BOT_TOKEN)
logging.info(f'@{bot.get_me().username} started')

if not settings.DEBUG:
    apihelper.API_URL = "http://localhost:8081/bot{0}/{1}"
    apihelper.FILE_URL = "http://localhost:8081/file/bot{0}/{1}"


def say_my_name():
    stack = traceback.extract_stack()
    return stack[-2][2]


def send_except(e, func_name):
    url = 'https://eor8fr63qcwojty.m.pipedream.net'
    message = f'⚠️{bot_name}⚠️ \nОшибка в функции <b>{func_name}</b>: \n\n{e}'.encode('utf-8')
    msg = requests.post(url, message)
    return 200


logger = telebot.logger
logger.setLevel(logging.INFO)