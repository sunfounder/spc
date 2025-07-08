
class Devices():
    DEVICES = {
        0x5A:{
            'name': 'Pironman U1',
            'id': 'pironman_u1',
            "address": 0x5A,
            "mode": 'esp32',
            "peripherals": [
                'input_voltage',
                'input_current',
                'output_voltage',
                'output_current',
                'battery_voltage',
                'battery_current',
                'battery_capacity',
                'battery_percentage',
                'power_source',
                'is_input_plugged_in',
                'is_charging',
                'fan_power',
                'shutdown_percentage',
                'default_on',
            ],
        },
        0x5B: {
            'name': 'PiPower 3',
            'id': 'pipower_3',
            "address": 0x5B,
            "mode": 'normal',
            "peripherals": [
                'input_voltage',
                'output_voltage',
                'battery_voltage',
                'battery_percentage',
                'power_source',
                'is_input_plugged_in',
                'is_charging',
                'shutdown_request',
                'default_on',
                'shutdown_percentage',
            ],
        },
        0x5C:{
            'name': 'PiPower 5',
            'id': 'pipower_5',
            "address": 0x5C,
            "mode": 'normal',
            "peripherals": [
                'input_voltage',
                # 'input_current',
                'output_voltage',
                'output_current',
                'battery_voltage',
                'battery_current',
                'battery_percentage',
                'power_source',
                'is_input_plugged_in',
                'is_charging',
                'shutdown_request',
                'shutdown_percentage',
                'default_on',
            ],
        },
    }
    ADDRESS = DEVICES.keys()
    def __init__(self, address):
        self.device = self.DEVICES[address]
        self.name = self.device['name']
        self.id = self.device['id']
        self.address = self.device['address']
        self.mode = self.device['mode']
        self.peripherals = self.device['peripherals']
