import udi_interface

from utils import Utilities

LOGGER = udi_interface.LOGGER

class EWeLinkNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, device_id, ewelink_interface):
        super(EWeLinkNode, self).__init__(polyglot, primary, address, name)
        self.address = address
        self.ewelink_interface = ewelink_interface
        self.device_id = device_id

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)

    def update(self):
        try:
            self.ewelink_interface.login()
            self.device = self.ewelink_interface.get_device(self.device_id)
            if self.device['currentTemperature'] == 'unavailable':
                self.setDriver('GV1', 101, True)
                LOGGER.exception("Could not communicate with sensor %s", self.device_id)
                return
            LOGGER.debug('Water Temp: ' + str(Utilities.celsius_to_fahrenheit(self.device['currentTemperature'])))
            self.setDriver('WATERT', Utilities.celsius_to_fahrenheit(self.device['currentTemperature']), True)
            LOGGER.debug('Device State: ' + self.device['switch'])
            if 'off' in self.device['switch']:
                self.setDriver('GV1', 0, True)
            elif 'on' in self.device['switch']:
                self.setDriver('GV1', 100, True)
            else:
                self.setDriver('GV1', 101, True)

            rssi_percent = Utilities.dbm_to_percent(self.device['rssi'], self.ewelink_interface.get_rssi_perfect(), self.ewelink_interface.get_rssi_worst())
            LOGGER.debug('Device rssi value: ' + str(self.device['rssi']))
            LOGGER.debug('Device rssi percent: ' + str(int(rssi_percent)))
            self.setDriver('RFSS', int(rssi_percent), True)
            self.setDriver('GV2', self.device['rssi'], True)
        except Exception as ex:
            LOGGER.exception("Could not refresh ewelink sensor %s because %s", self.device_id, ex)
            self.setDriver('GV1', 101, True)

    def cmd_don(self, cmd):
        self.ewelink_interface.login()
        self.device = self.ewelink_interface.udpate_device(self.device_id, 'on')
        self.query()

    def cmd_doff(self, cmd):
        self.ewelink_interface.login()
        self.device = self.ewelink_interface.udpate_device(self.device_id, 'off')
        self.query()

    def poll(self, pollType):
        if 'shortPoll' in pollType:
            LOGGER.info('shortPoll (node)')
            self.query()

    def query(self):
        LOGGER.info("Query sensor {}".format(self.device_id))
        self.update()

    def start(self):
        self.query()

    drivers = [
        {'driver': 'GV1', 'value': 0, 'uom': '78'},  # Status
        {'driver': 'WATERT', 'value': 0, 'uom': '17'},  # Water Temp
        {'driver': 'RFSS', 'value': 0, 'uom': '51'}, # RF Signal Percentage
        {'driver': 'GV2', 'value': 0, 'uom': '131'}  # RF dBm signal
    ]

    commands = {
        'DON': cmd_don,
        'DOFF': cmd_doff,
        'QUERY': query
    }

    id = 'ewelinknode'
