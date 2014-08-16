# vim: set fileencoding=utf8 :

import json
import os
import pickle
import requests

APIROOT = 'https://sl.se/api/MySL'
COOKIE_FILE = "%s/.mysl.cookies" % os.environ['HOME']

class MySLAPIException(Exception):

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data['ResultErrors'])


class Messages(object):

    NOT_LOGGED_IN = u'Du har blivit utloggad. Den här tjänsten kräver inloggad användare'

class MySL(object):

    def __getattr__(self, name):
        def handlerFunction(*args, **kwargs):
            if kwargs:
                return self._make_request(name, kwargs)
            return self._make_request(name)
        return handlerFunction

    def __init__(self, username=None, password=None, cookiejar=False):
        self.username = username
        self.password = password
        self.cookies = ''
        self.cookiejar = cookiejar 
        if self.cookiejar:
            try:
                with open(COOKIE_FILE, 'r') as file:
                    self.cookies = pickle.load(file)
            except:
                pass

    def _make_request(self, resource, args=None):
        if args:
            headers = {'content-type': 'application/json'}
            response = requests.post("%s/%s" % (APIROOT, resource),
                    cookies=self.cookies,
                    data=json.dumps(args),
                    headers=headers).json()
        else:
            response = requests.get("%s/%s" % (APIROOT, resource), cookies=self.cookies).json()
        if response['status'] == 'error':
            if response['data']['ResultErrors'][0] == Messages.NOT_LOGGED_IN:
                self._login()
                return self._make_request(resource, args)
            else:
                raise MySLAPIException(response['data'])
        return response['data']

    def _login(self):
        headers = {'content-type': 'application/json'}
        payload = {'username': self.username, 'password': self.password}
        p = requests.post("%s/Authenticate" % APIROOT,
                data=json.dumps(payload),
                headers=headers)
        self.cookies = p.cookies
        if self.cookiejar:
            with open(COOKIE_FILE, 'w') as file:
                pickle.dump(self.cookies, file)
