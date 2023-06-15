import json
import requests
from typing import Any

from interfaces.oauth import OAuth
from utils import Utilities

from udi_interface import LOGGER, Custom

class EWeLinkInterface(OAuth):
    def __init__(self, polyglot):
        super().__init__(polyglot)

        self.poly = polyglot
        self.customParams = Custom(polyglot, 'customparams')

        LOGGER.info('eWeLink interface initialized...')

    # The OAuth class needs to be hooked to these 3 handlers
    def customDataHandler(self, data):
        super()._customDataHandler(data)

    def customNsHandler(self, key, data):
        super()._customNsHandler(key, data)

    def oauthHandler(self, token):
        super()._oauthHandler(token)

    def customParamsHandler(self, data):
        self.customParams.load(data)
        LOGGER.info("Custom Parameters Loaded!")
        userValid = False
        passwordValid = False
        appIDValid = False
        appSecretValid = False

        self.user = self.customParams['username']
        self.password = self.customParams['password']
        self.region = self.customParams['region']
        self.app_id = self.customParams['app_id']
        self.app_secret = self.customParams['app_secret']
        self.rssi_perfect = self.customParams['rssi_perfect']
        self.rssi_worst = self.customParams['rssi_worst']

        LOGGER.debug(self.user)
        LOGGER.debug(self.password)
        LOGGER.debug(self.region)
        LOGGER.debug(self.app_id)
        LOGGER.debug(self.app_secret)
        LOGGER.debug(self.rssi_perfect)
        LOGGER.debug(self.rssi_worst)

        if self.rssi_perfect is not None:
            pass
        else:
            LOGGER.error('rssi_perfect is Blank setting to -20')
            self.rssi_perfect = -20

        if self.rssi_worst is not None:
            pass
        else:
            LOGGER.error('rssi_worst is Blank setting to -85')
            self.rssi_worst = -85

        if self.region is not None and len(self.region) > 0:
            regionValid = True
        else:
            LOGGER.error('Region is Blank setting to US')
            self.region = 'us'

        # Set the api base URL based on the region set.
        self.base_url = f'https://{self.region}-apia.coolkit.cc/v2'

        if self.user is not None and len(self.user) > 0:
            userValid = True
        else:
            LOGGER.error('username is Blank')

        if self.password is not None and len(self.password) > 0:
            passwordValid = True
        else:
            LOGGER.error('password is Blank')

        if self.app_id is not None and len(self.app_id) > 0:
            appIDValid = True
        else:
            LOGGER.error('app_id is Blank')

        if self.app_secret is not None and len(self.app_secret) > 0:
            appSecretValid = True
        else:
            LOGGER.error('app_secret is Blank')

        self.poly.Notices.clear()

        if userValid and passwordValid and appIDValid and appSecretValid:
            self.configured = True
            # self.ewelink = EWeLink(self.password, self.user, self.region, self.app_id, self.app_secret)
            # self.query()
        else:
            if not userValid:
                self.poly.Notices['username'] = 'username must be configured.'
            if not passwordValid:
                self.poly.Notices['password'] = 'password must be configured.'
            if not appIDValid:
                self.poly.Notices['app_id'] = 'app_id must be configured.'
            if not appSecretValid:
                self.poly.Notices['app_secret'] = 'app_secret must be configured.'

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
                'x-ck-nonce': Utilities.nonce(8)
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