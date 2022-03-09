# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 23:06:19 2022

@author: Ivan Selin
"""
import telebot
from telebot import types
from dataclasses import dataclass
import os
import math

bot = telebot.TeleBot(os.environ['TELEGRAM_API_KEY'])

@dataclass
class State:
    currency: str
    lat: float
    long: float
    radius: int
    interval: int
    top_right_lat: float
    top_right_long: float
    bottom_left_lat: float
    bottom_left_long: float

state = State(
    currency=None,
    lat=None,
    long=None,
    radius=None,
    interval=None,
    top_right_lat=None,
    top_right_long=None,
    bottom_left_lat=None,
    bottom_left_long=None
    )

def calculate_bounds():
    # https://stackoverflow.com/questions/7222382/get-lat-long-given-current-point-distance-and-bearing
    R = 6378.1 #Radius of the Earth
    #brng = 1.57 #Bearing is 90 degrees converted to radians.
    bottom_left_bearing = math.radians(225) # 225 degrees is bottom left
    top_right_bearing = math.radians(45) # and 45 degrees is top right
    d = state.radius #Distance in km
    
    lat1 = math.radians(state.lat) #Current lat point converted to radians
    long1 = math.radians(state.long) #Current long point converted to radians
    
    lat_bottom = math.asin( math.sin(lat1)*math.cos(d/R) +
         math.cos(lat1)*math.sin(d/R)*math.cos(bottom_left_bearing))
    
    long_bottom = long1 + math.atan2(math.sin(bottom_left_bearing)*math.sin(d/R)*math.cos(lat1),
                 math.cos(d/R)-math.sin(lat1)*math.sin(lat_bottom))
    
    lat_top = math.asin( math.sin(lat1)*math.cos(d/R) +
         math.cos(lat1)*math.sin(d/R)*math.cos(top_right_bearing))
    
    long_top = long1 + math.atan2(math.sin(top_right_bearing)*math.sin(d/R)*math.cos(lat1),
                 math.cos(d/R)-math.sin(lat1)*math.sin(lat_top))
    
    state.bottom_left_lat = math.degrees(lat_bottom)
    state.bottom_left_long = math.degrees(long_bottom)
    state.top_right_lat = math.degrees(lat_top)
    state.top_right_long = math.degrees(long_top)

@bot.message_handler(commands=['start'])
def start(m, res=False):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_rur=types.KeyboardButton('RUB')
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
    
    
@bot.message_handler(
    content_types=['text'],
    func=lambda message: message.text in ['RUB', 'USD', 'EUR']
    )
def handle_currency(message):
    state.currency = message.text
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(
        message.chat.id,
        'Пришлите своё местоположение',
        reply_markup=keyboard
        )
    
@bot.message_handler(content_types=['location'])
def handle_location(message):
    print('inside location method')
    if message.location is not None:
        print('there is a location')
        state.lat = message.location.latitude
        state.long = message.location.longitude
        markup = types.ReplyKeyboardRemove(
            selective=False
            )
        bot.send_message(
            message.chat.id,
            'Укажите радиус поиска банкоматов в километрах',
            reply_markup=markup
        )
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(
            message.chat.id,
            'Пришлите своё местоположение',
            reply_markup=keyboard
            )

@bot.message_handler(
    content_types=['text'],
    func=lambda m: (m.text.isnumeric()) and (state.radius is None) 
    )
def handle_radius(message):
    state.radius = int(message.text)
    calculate_bounds()
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(
        message.chat.id,
        'Укажите частоту опроса в секундах',
        reply_markup=markup
    )
    
@bot.message_handler(
    content_types=['text'],
    func=lambda m: (m.text.isnumeric) and (state.interval is None) and (state.radius is not None)
    )
def handle_interval(message):
    state.interval = int(message.text)
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(
        message.chat.id,
        f'Все данные введены. Валюта: {state.currency}, ' +
        f'место: от ({state.bottom_left_lat},{state.bottom_left_long}) до ' +
        f'({state.top_right_lat},{state.top_right_long}), ' +
        f'интервал опроса: {state.interval} секунд',
        reply_markup=markup
    )
        
    
bot.polling(none_stop=True, interval=0)