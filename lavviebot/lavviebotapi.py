import json
import requests
import logging
import time
import collections

from lavviebot.devices.lavviebot import LavvieBot
from lavviebot.cats.cat import Cat

APP_VERSION = '2.6.0'
DEVICE_OS = 'ios'
OS_URL = '&deviceOS=' + DEVICE_OS


BASE_URL = 'https://api.purrsongwriter.com/v2/initialScreen/'
COOKIE_URL = BASE_URL + 'startApp?appVersion=' + APP_VERSION + OS_URL
LOGIN_URL = BASE_URL + 'login'
CAT_INFO_URL = 'https://api.purrsongwriter.com/v2/purrsongScreen/mainV2'
BOT_INFO_URL = 'https://api.purrsongwriter.com/v2/purrsongScreen/iotScreen/iotDetailScreen/lavviebotDetail'


#Headers
ACCEPT = 'application/json, text/plain, */*'
CONTENT_TYPE = 'application/json;charset=utf-8'
CONNECTION = 'keep-alive'
ACCEPT_LANGUAGE = 'en-us'
ACCEPT_ENCODING = 'gzip, deflate, br'
USER_AGENT = 'purrsongapp/1 CFNetwork/1126 Darwin/19.5.0'

#Payload
DEVICE_TYPE = 'iPhone13,2'
DEVICE_TOKEN = 'A'
LANGUAGE = 'en'
TIME_ZONE = 'America/New_York'

_LOGGER = logging.getLogger(__name__)

class LavvieBotSession:

    username = ''
    password = ''
    user_token = ''
    devices = []
    cats = []

SESSION = LavvieBotSession()

class LavvieBotApi:

    def __init__(self, username, password):
        SESSION.username = username
        SESSION.password = password

        if username is None or password is None:
            return None
        else:
            self.login()
            self.discover_devices()
            self.discover_cats()

    def devices(self):
        return SESSION.devices

    def cats(self):
        return SESSION.cats

    def login(self):
        cookie, etag = self._get_cookie()
        SESSION.cookie = cookie
        SESSION.etag = etag
        user_token = self._get_user_token(SESSION.cookie, SESSION.etag)
        SESSION.user_token = user_token

    def _get_cookie(self):
        response = requests.get(COOKIE_URL)
        cookie_and_etag = response.headers
        return (cookie_and_etag['Set-Cookie'], cookie_and_etag['ETag'])

    def _get_user_token(self, cookie, etag):
        headers = {
        'Accept': ACCEPT,
        'Content-Type': CONTENT_TYPE,
        'Connection': CONNECTION,
        'If-None-Match': etag,
        'Cookie': cookie,
        'Accept-Language': ACCEPT_LANGUAGE,
        'Accept-Encoding': ACCEPT_ENCODING,
        'User-Agent': USER_AGENT
        }
        payload = {
        'userId': SESSION.username,
        'password': SESSION.password,
        'deviceType': DEVICE_TYPE,
        'deviceToken': DEVICE_TOKEN,
        'language': LANGUAGE,
        'deviceOS': DEVICE_OS,
        'appVersion': APP_VERSION,
        'timezone': TIME_ZONE
        }
        response = requests.post(LOGIN_URL, headers=headers, data=json.dumps(payload))
        output = response.json()
        return output['res']['userToken']

    def _refresh_token(self):
        headers = {
        'Accept': ACCEPT,
        'Content-Type': CONTENT_TYPE,
        'Connection': CONNECTION,
        'If-None-Match': etag,
        'Cookie': cookie,
        'Accept-Language': ACCEPT_LANGUAGE,
        'Accept-Encoding': ACCEPT_ENCODING,
        'User-Agent': USER_AGENT
        }
        payload = {
        'userId': SESSION.username,
        'password': SESSION.password,
        'deviceType': DEVICE_TYPE,
        'deviceToken': DEVICE_TOKEN,
        'language': LANGUAGE,
        'deviceOS': DEVICE_OS,
        'appVersion': APP_VERSION,
        'timezone': TIME_ZONE
        }
        response = requests.post(LOGIN_URL, headers=headers, data=json.dumps(payload))
        output = response.json()
        SESSION.user_token = output['res']['userToken']

    def discover_devices(self):
        headers = {
        'Accept': ACCEPT,
        'Content-Type': CONTENT_TYPE,
        'Connection': CONNECTION,
        'If-None-Match': SESSION.etag,
        'Cookie': SESSION.cookie,
        'Accept-Language': ACCEPT_LANGUAGE,
        'Accept-Encoding': ACCEPT_ENCODING,
        'User-Agent': USER_AGENT
        }
        payload = {
        'userToken': SESSION.user_token,
        'timezone': TIME_ZONE
        }
        response = requests.post(CAT_INFO_URL, headers=headers, data=json.dumps(payload))
        lavvie_bots = response.json()['res'][1]['lavviebots']
        devices = []
        for device in lavvie_bots:
            devices.append(LavvieBot(device, self))
        SESSION.devices = devices

    def refresh_devices(self):
        for device in SESSION.devices:
            device.refresh()

    def discover_cats(self):
        headers = {
        'Accept': ACCEPT,
        'Content-Type': CONTENT_TYPE,
        'Connection': CONNECTION,
        'If-None-Match': SESSION.etag,
        'Cookie': SESSION.cookie,
        'Accept-Language': ACCEPT_LANGUAGE,
        'Accept-Encoding': ACCEPT_ENCODING,
        'User-Agent': USER_AGENT
        }
        payload = {
        'userToken': SESSION.user_token,
        'timezone': TIME_ZONE
        }
        response = requests.post(CAT_INFO_URL, headers=headers, data=json.dumps(payload))
        available_cats = response.json()['res'][1]['cats']
        cats = []
        for idx, cat in enumerate(available_cats):
            cats.append(Cat(cat, idx, self))
        SESSION.cats = cats

    def refresh_cats(self):
        for cat in SESSION.cats:
            cat.refresh()

    def lavviebot_status(self, device):
        headers = {
        'Accept': ACCEPT,
        'Content-Type': CONTENT_TYPE,
        'Connection': CONNECTION,
        'If-None-Match': SESSION.etag,
        'Cookie': SESSION.cookie,
        'Accept-Language': ACCEPT_LANGUAGE,
        'Accept-Encoding': ACCEPT_ENCODING,
        'User-Agent': USER_AGENT
        }
        payload = {
        'userToken': SESSION.user_token,
        'lavviebotId': device.lavviebot_id
        }
        response = requests.post(BOT_INFO_URL, headers=headers, data=json.dumps(payload))
        return response.json()['res']

    def cat_status(self, cat):
        headers = {
        'Accept': ACCEPT,
        'Content-Type': CONTENT_TYPE,
        'Connection': CONNECTION,
        'If-None-Match': SESSION.etag,
        'Cookie': SESSION.cookie,
        'Accept-Language': ACCEPT_LANGUAGE,
        'Accept-Encoding': ACCEPT_ENCODING,
        'User-Agent': USER_AGENT
        }
        payload = {
        'userToken': SESSION.user_token,
        'timezone': TIME_ZONE
        }
        response = requests.post(CAT_INFO_URL, headers=headers, data=json.dumps(payload))
        return response.json()['res'][1]['cats']


    def check_user_token(self):
        if SESSION.username == '' or SESSION.password == '':
            raise LavvieBotAPIException("Cannot find username or password")
            return
        if SESSION.user_token == '' or SESSION.cookie == '':
            raise LavvieBotAPIException("Cannot find user token or cookie. Attempting to log in again.")
            self.login()

    def poll_devices_update(self):
        self.check_user_token()
        self.refresh_devices()
        self.refresh_cats()

    def get_all_devices(self):
        return SESSION.devices

    def get_all_cats(self):
        return SESSION.cats


class LavvieBotAPIException(Exception):
    pass
