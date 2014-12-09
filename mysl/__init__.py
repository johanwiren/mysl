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

    def __init__(self, username=None, password=None, cookiejar=False, debug=False):
        self.username = username
        self.password = password
        self.cookies = requests.cookies.RequestsCookieJar()
        self.cookiejar = cookiejar 
        if self.cookiejar:
            try:
                with open(COOKIE_FILE, 'r') as file:
                    self.cookies = pickle.load(file)
            except:
                pass

    def _make_request(self, resource, args=None):
        headers = dict()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0'
        headers['Referer'] = 'https://sl.se/sv/mitt-konto/konto/'
        request_args = dict(cookies=self.cookies)
        if args:
            headers['Content-Type'] = 'application/json;charset=utf-8'
            request = "%s/%s" % (APIROOT, resource)
            request_args['data'] = json.dumps(args)
            request_args['headers'] = headers
            response = requests.post(request, **request_args)
            response_json = response.json()
            self.cookies.update(response.cookies)
        else:
            request = "%s/%s" % (APIROOT, resource)
            request_args = dict(
                    cookies=self.cookies,
                    headers=headers)
            response = requests.get(request, **request_args)
            self.cookies.update(response.cookies)
            response_json = response.json()
        if response_json['status'] == 'error':
            if unicode(response_json['data']['ResultErrors'][0]) == Messages.NOT_LOGGED_IN:
                self._login()
                return self._make_request(resource, args)
            else:
                raise MySLAPIException(response_json['data'])
        return response_json['data']

    def _login(self):
        r = requests.get('https://sl.se/sv/mitt-sl/inloggning',
                cookies=self.cookies)
        self.cookies.update(r.cookies)
        headers = {'content-type': 'application/json; charset=utf-8'}
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:30.0) Gecko/20100101 Firefox/30.0'
        headers['Referer'] = 'https://sl.se/sv/mitt-sl/inloggning/'
        payload = {'username': self.username, 'password': self.password}
        p = requests.post("%s/Authenticate" % APIROOT,
                data=json.dumps(payload),
                headers=headers,
                cookies=self.cookies)
        self.cookies.update(p.cookies)
        if self.cookiejar:
            with open(COOKIE_FILE, 'w') as file:
                pickle.dump(self.cookies, file)
