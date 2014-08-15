#!/usr/bin/env python

import json
import pickle
import requests

APIROOT = 'https://sl.se/api/MySL'
USERNAME = 'johan@johanwiren.se'
PASSWORD = '123qweASD'

class SlClient:

    def __init__(self):
        self.cookies = ''
        try:
            with open('cookies', 'r') as file:
                self.cookies = pickle.load(file)
        except:
            pass

    def get(self, resource):
        r = requests.get("%s/%s" % (APIROOT, resource), cookies=self.cookies)
        if r.json()['status'] == 'error':
            self.login()
            r = requests.get("%s/%s" % (APIROOT, resource), cookies=self.cookies)
        return r.json()['data']

    def login(self):
        headers = {'content-type': 'application/json'}
        payload = {'username': USERNAME, 'password': PASSWORD}
        p = requests.post("%s/Authenticate" % APIROOT,
                data=json.dumps(payload),
                headers=headers)
        self.cookies = p.cookies
        with open('cookies', 'w') as file:
            pickle.dump(self.cookies, file)
        

client = SlClient()
cards = client.get('GetTravelCards')['travel_card_list']
for card in cards:
    print "%s %d" % (card['travel_card']['name'],
            card['travel_card']['detail']['purse_value'])

