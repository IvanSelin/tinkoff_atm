# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 01:16:43 2022

@author: Ivan Selin
"""

import requests
import json
import copy
import time
import pprint
import logging
import sys

logging.basicConfig(level=logging.INFO, filename='tinkoff_atm.log',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
if (len(logging.getLogger().handlers) < 2):
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

pp = pprint.PrettyPrinter(indent=2)

request_body = {
    "bounds": {
        "bottomLeft": {
            "lat": 59.7892639574436,
            "lng": 30.077441043299608
        },
        "topRight": {
            "lat": 60.15889969333775,
            "lng": 30.773012942713656
        }
    },
    "filters": {
        "banks": [
            "tcs"
        ],
        "showUnavailable": True,
        "currencies": [
            "EUR"
        ]
    },
    "zoom": 11
}

url = 'https://api.tinkoff.ru/geo/withdraw/clusters'
headers = {
    'content-type':'application/json'
    }

saved_points = []
new_points = []
 
while True:
    
    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(request_body)
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
        for idx_cluster,cluster in enumerate(clusters):
            points = cluster['points']
            for idx_point,point in enumerate(points):
                atmInfo = point['atmInfo']
                limits = atmInfo['limits']
                new_points.append(json.dumps(point))
        difference=list(set(new_points) - set(saved_points))
        saved_points = copy.copy(new_points)
        logging.debug(f'now {len(new_points)} atms, prev {len(saved_points)}, diff {len(difference)}')
        for point in difference:
            decoded = json.loads(point)
            # pp.pprint(decoded)
            logging.info(f'{decoded["address"]}')
            logging.info(f'{decoded["installPlace"]}')
            atmInfo = decoded['atmInfo']
            limits = atmInfo['limits']
            [logging.info(f'currency: {limit["currency"]} - {limit["amount"]}') for limit in limits]

       
    time.sleep(60)
        