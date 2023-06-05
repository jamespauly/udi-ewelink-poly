import udi_interface

from utils import Utilities

LOGGER = udi_interface.LOGGER

class EWeLinkNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, device_id, ewelink, rssi_perfect, rssi_worst):
        super(EWeLinkNode, self).__init__(polyglot, primary, address, name)
        self.address = address
        self.ewelink = ewelink
        self.device_id = device_id
        self.rssi_perfect = rssi_perfect
        self.rssi_worst = rssi_worst

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)

    def update(self):
        try:
            self.ewelink.login()
            self.device = self.ewelink.get_device(self.device_id)
            if self.device['currentTemperature'] == 'unavailable':
                self.setDriver('GV1', 101, True)
                LOGGER.exception("Could not communicate with sensor %s", self.device_id)
                return
            LOGGER.info('Water Temp: ' + str(Utilities.celsius_to_fahrenheit(self.device['currentTemperature'])))
            self.setDriver('WATERT', Utilities.celsius_to_fahrenheit(self.device['currentTemperature']), True)
            LOGGER.info('Device State: ' + self.device['switch'])
            if 'off' in self.device['switch']:
                self.setDriver('GV1', 0, True)
            elif 'on' in self.device['switch']:
                self.setDriver('GV1', 100, True)
            else:
                self.setDriver('GV1', 101, True)

            rssi_percent = Utilities.dbm_to_percent(self.device['rssi'], self.rssi_perfect, self.rssi_worst)
            self.setDriver('RFSS', rssi_percent, True)
        except Exception as ex:
            LOGGER.exception("Could not refresh ewelink sensor %s because %s", self.device_id, ex)
            self.setDriver('GV1', 101, True)

    def cmd_don(self, cmd):
        self.ewelink.login()
        self.device = self.ewelink.udpate_device(self.device_id, 'on')
        self.query()

    def cmd_doff(self, cmd):
        self.ewelink.login()
        self.device = self.ewelink.udpate_device(self.device_id, 'off')
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
        {'driver': 'RFSS', 'value': 0, 'uom': '51'} # RF Signal Percentage
    ]

    commands = {
        'DON': cmd_don,
        'DOFF': cmd_doff,
        'QUERY': query
    }

    id = 'ewelinknode'
