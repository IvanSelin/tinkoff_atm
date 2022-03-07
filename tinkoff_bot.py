# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 23:06:19 2022

@author: Ivan Selin
"""
import telebot
from telebot import types
from dataclasses import dataclass
import os

bot = telebot.TeleBot(os.environ['TELEGRAM_API_KEY'])

@dataclass
class State:
    currency: str
    lat: float
    long: float
    on: bool

state = State(currency=None, lat=None, long=None, on=False)




@bot.message_handler(commands=['start'])
def start(m, res=False):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_rur=types.KeyboardButton('RUR')
    item_usd=types.KeyboardButton('USD')
    item_eur=types.KeyboardButton('EUR')
    markup.add(item_rur)
    markup.add(item_usd)
    markup.add(item_eur)
    
    bot.send_message(
        m.chat.id,
        'Выберите валюту',
        reply_markup=markup
    )

@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_message(message.chat.id, message.text.strip())
    
bot.polling(none_stop=True, interval=0)