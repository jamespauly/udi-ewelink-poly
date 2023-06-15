import random
import json
import requests
from typing import Any

from utils import Utilities

import udi_interface

LOGGER = udi_interface.LOGGER

class EWeLink():
    def __init__(self, password, email, region, app_id, app_secret):
        self.password = password
        self.user = email
        self.app_id = app_id
        self.app_secret = bytes(app_secret, 'utf-8')
        if region is None:
            self.region = 'us'
        else:
            self.region = region

        self.base_url = f'https://{self.region}-apia.coolkit.cc/v2'

        LOGGER.debug('URL = ' + self.base_url)

    def login(self):
        credentials = \
            {
                'lang': 'en',
                'countryCode': '+1',
                'email': self.user,
                'password': self.password
            }

        LOGGER.debug(json.dumps(credentials))

        # Create auth header
        sign = Utilities.hmac_sign(self.app_secret, credentials)

        LOGGER.debug('Sign = ' + sign)
        headers = \
            {
                'Authorization': f'Sign {sign}',
                'x-ck-appid': f'{self.app_id}',
                'x-ck-nonce': self.nonce(8)
            }

        login_response = requests.post(self.base_url + '/user/login', headers=headers,
                                       json=credentials)

        LOGGER.debug('Login Response: ' + json.dumps(login_response.json()))
        login_data: dict[str, Any] = login_response.json()

        self.token = login_data['data'].get('at')
        self.refresh_token = login_data['data'].get('rt')

        LOGGER.debug('AT = ' + self.token)

        return login_data

    def get_devices(self):
        device_response = \
            requests.get(self.base_url + '/device/thing',
                         params= \
                             {
                                 'lang': 'en'
                             },
                         headers={'Authorization': f'Bearer {self.token}'})

        LOGGER.debug('Get Devices Response: ' + json.dumps(device_response.json()))
        return device_response.json()['data']['thingList']

    def get_device(self, device_id):
        device_response = \
            requests.get(self.base_url + '/device/thing/status',
                         params= \
                             {
                                 'type': 1,
                                 'id': device_id
                             },
                         headers={'Authorization': f'Bearer {self.token}'})

        LOGGER.debug('Get Device Response: ' + json.dumps(device_response.json()))
        return device_response.json()['data']['params']

    def udpate_device(self, device_id, status):
        device_response = \
            requests.post(self.base_url + '/device/thing/status',
                         json= \
                             {
                                 'type': 1,
                                 'id': device_id,
                                 'params': {'switch': status}
                             },
                         headers={'Authorization': f'Bearer {self.token}'})


        update_response = device_response.json()
        LOGGER.debug('Update Device Response: ' + json.dumps(update_response))

        return update_response

    def get_gateway(self) -> dict[str, Any]:
        response = requests.get(
            f'https://{self.region}-dispa.coolkit.cc/dispatch/app',
            headers={
                'Authorization': f'Token {self.token}'
            }
        )
        return response.json()
    def nonce(self, length: int = 15) -> str:
        return ''.join(str(random.randint(0, 9)) for _ in range(length))