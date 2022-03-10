# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 01:16:43 2022

@author: Ivan Selin
"""

import requests
import json
import copy
import time
# import pprint
import logging
import sys
from telebot import types


class TinkoffAtm:
    """docstring"""

    def __init__(
            self,
            currency,
            interval,
            bottom_left_lat,
            bottom_left_long,
            top_right_lat,
            top_right_long,
            bot,
            message,
            # post_message,
            enable_logging,
            enable_std_out
            ):
        self.currency = currency
        self.interval = interval
        self.bottom_left_lat = bottom_left_lat
        self.bottom_left_long = bottom_left_long
        self.top_right_lat = top_right_lat
        self.top_right_long = top_right_long
        self.bot = bot
        self.message = message
        # self.post_message = post_message
        if enable_logging is True:
            logging.basicConfig(
                level=logging.INFO, filename='tinkoff_atm.log',
                format='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%d-%b-%y %H:%M:%S'
                )
            if enable_std_out is True:
                if (len(logging.getLogger().handlers) < 2):
                    logging.getLogger().addHandler(
                        logging.StreamHandler(sys.stdout)
                        )
        self.setup()

    def setup(self):
        # self.pp = pprint.PrettyPrinter(indent=2)
        self.request_body = {
            'bounds':
                {
                    'bottomLeft':
                        {
                            'lat': self.bottom_left_lat,
                            'lng': self.bottom_left_long
                        },
                    'topRight':
                        {
                            'lat': self.top_right_lat,
                            'lng': self.top_right_long
                        }
                 },
            'filters':
                {
                    'banks': ['tcs'],
                    'showUnavailable': False,
                    'currencies': [self.currency]
                },
            'zoom': 11
            }
        self.url = 'https://api.tinkoff.ru/geo/withdraw/clusters'
        self.headers = {
            'content-type': 'application/json'
            }
        self.tracking = True

    def start_tracking(self):
        print('start tracking')
        saved_points = []
        new_points = []
        print(self.tracking)

        while self.tracking:
            try:
                print('requesting')
                response = requests.post(
                    self.url,
                    headers=self.headers,
                    data=json.dumps(self.request_body)
                    )
            except requests.ConnectionError:
                logging.warning('ConnectionError. Waiting and resuming')
                time.sleep(10)
                continue

            if (response.status_code == 200):
                response_content = response.content
                json_response = json.loads(response_content)
                payload = json_response['payload']
                clusters = payload['clusters']
                new_points = []
                for idx_cluster, cluster in enumerate(clusters):
                    points = cluster['points']
                    for idx_point, point in enumerate(points):
                        atmInfo = point['atmInfo']
                        limits = atmInfo['limits']
                        new_points.append(json.dumps(point))
                difference = list(set(new_points) - set(saved_points))
                saved_points = copy.copy(new_points)
                logging.debug(
                    f'now {len(new_points)} atms, prev {len(saved_points)}, '
                    + 'diff {len(difference)}'
                    )
                for point in difference:
                    decoded = json.loads(point)
                    # self.pp.pprint(decoded)
                    print(f'{decoded["address"]} {decoded["installPlace"]}')
                    bot_message = f'{decoded["address"]}\r\n'
                    logging.info(f'{decoded["address"]}')
                    logging.info(f'{decoded["installPlace"]}')
                    atmInfo = decoded['atmInfo']
                    limits = atmInfo['limits']
                    bot_message += '\r\n'.join(
                        f'{limit["currency"]}: {limit["amount"]}'
                        for limit in limits
                        )
                    [logging.info(
                        f'currency: {limit["currency"]} - {limit["amount"]}'
                        ) for limit in limits]
                    markup = types.ReplyKeyboardRemove(selective=False)
                    self.bot.send_message(
                        self.message.chat.id,
                        bot_message,
                        reply_markup=markup
                    )

            time.sleep(self.interval)

    def stop_tracking(self):
        self.tracking = False
