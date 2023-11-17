
class Devices():
    DEVICES = [
        {
            'name': 'UPS Case',
            'id': 'ups_case',
            "address": 0x00,
            "peripherals": [
                'battery',
                'usb_in',
                'power_source_sensor',
                'output',
                'fan',
            ],
        }, {
            'name': 'Pironman 4',
            'id': 'pironman_4',
            "address": 0x01,
            "peripherals": [
                'usb_in',
                'fan',
                'oled',
                'ws2812',
            ],
        }
    ]
    def __init__(self, address):
        self.device = self.DEVICES[address]
        self.name = self.device['name']
        self.id = self.device['id']
        self.address = self.device['address']   
        self.peripherals = self.device['peripherals']
