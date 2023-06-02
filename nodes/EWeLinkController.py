import udi_interface
from utils import EWeLink

from nodes import EWeLinkNode

# IF you want a different log format than the current default
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class EWeLinkController(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name):
        super(EWeLinkController, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.name = name
        self.primary = primary
        self.address = address

        self.Notices = Custom(polyglot, 'notices')
        self.Parameters = Custom(polyglot, 'customparams')

        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameter_handler)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)

        self.poly.ready()
        self.poly.addNode(self)

    def start(self):
        LOGGER.info('Staring eWeLink NodeServer')
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()
        self.discover()
        LOGGER.info('Started eWeLink NodeServer')

    def query(self, command=None):
        LOGGER.info("Starting eWeLink Device Query")
        self.discover()
        LOGGER.info('Ending eWeLink Device Query')

    def poll(self, pollType):
        if 'longPoll' in pollType:
            LOGGER.info('longPoll (node)')
            self.discover()

    def parameter_handler(self, params):
        self.Parameters.load(params)

        userValid = False
        passwordValid = False
        appIDValid = False
        appSecretValid = False

        self.user = self.Parameters['username']
        self.password = self.Parameters['password']
        self.region = self.Parameters['region']
        self.app_id = self.Parameters['app_id']
        self.app_secret = self.Parameters['app_secret']

        LOGGER.debug(self.user)
        LOGGER.debug(self.password)
        LOGGER.debug(self.region)
        LOGGER.debug(self.app_id)
        LOGGER.debug(self.app_secret)

        if self.region is not None and len(self.region) > 0:
            regionValid = True
        else:
            LOGGER.error('Region is Blank setting to US')
            REGION = 'us'

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

        self.Notices.clear()

        if userValid and passwordValid and appIDValid and appSecretValid:
            self.configured = True
            self.ewelink = EWeLink(self.password, self.user, self.region, self.app_id, bytes(self.app_secret, 'utf-8'))
            self.query()
        else:
            if not userValid:
                self.Notices['username'] = 'username must be configured.'
            if not passwordValid:
                self.Notices['password'] = 'password must be configured.'
            if not appIDValid:
                self.Notices['app_id'] = 'app_id must be configured.'
            if not appSecretValid:
                self.Notices['app_secret'] = 'app_secret must be configured.'

    def discover(self, *args, **kwargs):
        LOGGER.info("Starting eWeLink Device Discovery")
        self.ewelink.login()
        devices = self.ewelink.get_devices()
        LOGGER.info("Starting eWeLink Device Node Load")
        for node in self.poly.getNodes():
            LOGGER.debug('Listing Nodes: ' + node)

        for device in devices:
            device_id = device['itemData']['deviceid']
            address_id = 'n' + device_id[:6]
            if self.poly.getNode(address_id) is None:
                LOGGER.info("Adding Node {}".format(device_id))
                self.poly.addNode(
                    EWeLinkNode(self.poly, self.address, address_id, device['itemData']['name'],
                                device_id, ewelink=self.ewelink))
            else:
                ewelink_node = self.poly.getNode(address_id)
                ewelink_node.query()
                LOGGER.info('eWeLink Node {} already exists, skipping'.format(device_id))
        LOGGER.info('Finished eWeLink Node Load')
        LOGGER.info('Finished eWeLink Device Discovery')

    def delete(self):
        LOGGER.info('Deleting eWeLink Node Server')

    def stop(self):
        LOGGER.info('eWeLink NodeServer stopped.')

    id = 'ewelink'
    commands = {
        'DISCOVER': discover
    }

    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2}
    ]
