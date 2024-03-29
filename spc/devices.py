
class Devices():
    DEVICES = [
        {
            'name': 'Pironman U1',
            'id': 'pironman_u1',
            "address": 0x00,
            "peripherals": [
                'battery',
                'external_input',
                'power_source_sensor',
                'raspberry_pi_power',
                'fan',
                'ir',
            ],
        }, {
            'name': 'Pironman 4',
            'id': 'pironman_4',
            "address": 0x01,
            "peripherals": [
                'external_input',
                'fan',
                'oled',
                'ws2812',
                'ir',
            ],
        }
    ]
    def __init__(self, address):
        self.device = self.DEVICES[address]
        self.name = self.device['name']
        self.id = self.device['id']
        self.address = self.device['address']   
        self.peripherals = self.device['peripherals']
