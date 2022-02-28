# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 01:16:43 2022

@author: Ivan Selin
"""

import requests
import json
import copy
import time

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

f = open("tinkoff_atm1.txt", "a")
url = 'https://api.tinkoff.ru/geo/withdraw/clusters'
headers = {
    'content-type':'application/json'
    }

saved_points = []
new_points = []
 
while True:
    f = open("tinkoff_atm.txt", "a")
    f.write(f'sending request at {time.strftime("%H:%M:%S", time.localtime())}\r\n')
    print(f'sending request at {time.strftime("%H:%M:%S", time.localtime())}')
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(request_body)
        )
    
    if (response.status_code == 200):
        response_content = response.content
        json_response = json.loads(response_content)
        payload = json_response['payload']
        clusters = payload['clusters']
        new_points = []
        for idx_cluster,cluster in enumerate(clusters):
            points = cluster['points']
            # print(f'cluster {idx_cluster}')
            for idx_point,point in enumerate(points):
                # print(f'point {idx_point}')
                # print(f'{point["address"]}')
                # print(f'{point["installPlace"]}')
                atmInfo = point['atmInfo']
                limits = atmInfo['limits']
                # atm_points.append(point)
                # point_to_save = copy.deepcopy(point)
                new_points.append(json.dumps(point))
                # for idx_limit, limit in enumerate(limits):
                #     print(f'currency: {limit["currency"]} - {limit["amount"]}')
        difference=list(set(new_points) - set(saved_points))
        saved_points = copy.copy(new_points)
        print(f'difference is in {len(difference)} points')
        f.write(f'difference is in {len(difference)} points\r\n')
        for point in difference:
            decoded = json.loads(point)
            # print(f'decoded {idx_point}')
            f.write(f'{decoded["address"]}\r\n')
            f.write(f'{decoded["installPlace"]}\r\n')
            print(f'{decoded["address"]}')
            print(f'{decoded["installPlace"]}')
            atmInfo = decoded['atmInfo']
            limits = atmInfo['limits']
            for idx_limit, limit in enumerate(limits):
                    print(f'currency: {limit["currency"]} - {limit["amount"]}')
                    f.write(f'currency: {limit["currency"]} - {limit["amount"]}\r\n')
    f.close()            
    time.sleep(60)
        