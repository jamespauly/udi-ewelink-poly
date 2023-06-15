import udi_interface
from lib.ewelink import EWeLink

from nodes import EWeLinkNode

# IF you want a different log format than the current default
LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class EWeLinkController(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, ewelink_interface):
        super(EWeLinkController, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.ewelink_interface = ewelink_interface

        self.poly.addNode(self, conn_status='ST')
        LOGGER.info('eWeLink Controller Initialized')

    def query(self, command=None):
        LOGGER.info("Starting eWeLink Device Query")
        self.discover()
        LOGGER.info('Ending eWeLink Device Query')

    def discover(self, *args, **kwargs):
        LOGGER.info("Starting eWeLink Device Discovery")
        self.ewelink_interface.login()
        devices = self.ewelink_interface.get_devices()
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
                                device_id, self.ewelink_interface, self.rssi_perfect, self.rssi_worst))
            else:
                ewelink_node = self.poly.getNode(address_id)
                ewelink_node.query()
                LOGGER.info('eWeLink Node {} already exists, skipping'.format(device_id))
        LOGGER.info('Finished eWeLink Node Load')
        LOGGER.info('Finished eWeLink Device Discovery')

    id = 'ewelink'
    commands = {
        'DISCOVER': discover
    }

    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2}
    ]
