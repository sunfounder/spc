#!/usr/bin/env python3
from smbus import SMBus
import struct
from .config import Config

BOARDS = [
    {
        "id": "ups_case",
        "name": "UPS Case",
        "address": 0x00,
        "support_data": [
            'battery_voltage',
            'battery_current',
            'usb_voltage',
            'usb_current',
            'output_voltage',
            'output_current',
            'ref_voltage',
            'power_source',
            'is_usb_plugged_in',
            'is_charging',
            'fan_speed',
            'battery_percentage',
            'board_id',
            'shutdown_request',
        ],
    },
    {
        "id": "pironman",
        "name": "Pironman",
        "address": 0x01,
        "support_data": [
            'usb_voltage',
            'output_current',
        ],
    }
]


# class SPC()
# =================================================================
class SPC():

    I2C_ADDRESS = 0x5A

    BATTERY = 1
    USB = 0

    data_format = '>BHHhHhHhBHBBBBB'
    total_length = 23
    data_map = {
        'board_id': (0, 1, 'B'),  # data start index, data length, format
        'vcc_voltage': (1, 2, '>H'),
        'usb_voltage': (3, 2, '>H'),
        'usb_current': (5, 2, '>h'),
        'output_voltage': (7, 2, '>H'),
        'output_current': (9, 2, '>h'),
        'battery_voltage': (11, 2, '>H'),
        'battery_current': (13, 2, '>h'),
        'battery_percentage': (15, 1, 'B'),
        'battery_capactiy': (16, 2, '>H'),
        #
        'power_source': (18, 1, 'B'),
        'is_usb_plugged_in': (19, 1, 'B'),
        'is_charging': (20, 1, 'B'),
        'fan_speed': (21, 1, 'B'),
        'shutdown_request': (22, 1, '>B'),
    }

    control_map = {
        'fan_speed': (0, 1),
    }

    def __init__(self, address=I2C_ADDRESS):
        self.addr = address
        try:
            self.i2c_dev = SMBus(1)
            self.i2c_dev.read_byte_data(self.addr, 0x00)  # try to read a byte
        except Exception as e:
            raise IOError(f'UPS Case init error:\b\t{e}')

        self.config = Config()
        self.fan_mode = self.config.get('auto', 'fan_mode')
        self.fan_state = self.config.get('auto', 'fan_state') == 'True'
        self.fan_speed = int(self.config.get('auto', 'fan_speed'))
        if self.fan_state:
            self.set_fan_speed(self.fan_speed)

    def _read(self, start, length):
        result = self.i2c_dev.read_i2c_block_data(self.addr, start, length)
        return result

    def _write(self, name: str, value: list):
        self.i2c_dev.write_i2c_block_data(self.addr, 0, value)

    def _read_data(self, name: str):
        _start, _len, _format = self.data_map[name]
        result = self._read(_start, _len)
        result = struct.unpack(_format, bytes(result))
        return result[0]

    def read_battery_voltage(self) -> int:
        result = self._read_data('battery_voltage')
        return int(result)

    def read_battery_current(self) -> int:
        result = self._read_data('battery_current')
        return int(result)

    def read_usb_voltage(self) -> int:
        result = self._read_data('usb_voltage')
        return int(result)

    def read_usb_current(self) -> int:
        result = self._read_data('usb_current')
        return int(result)

    def read_output_voltage(self) -> int:
        result = self._read_data('output_voltage')
        return int(result)

    def read_output_current(self) -> int:
        result = self._read_data('output_current')
        return int(result)

    def read_ref_voltage(self) -> int:
        result = self._read_data('ref_voltage')
        return int(result)

    def read_power_source(self) -> int:
        result = self._read_data('power_source')
        return int(result)

    def read_is_usb_plugged_in(self) -> int:
        result = self._read_data('is_usb_plugged_in')
        return int(result)

    def read_is_charging(self) -> int:
        result = self._read_data('is_charging')
        return int(result)

    def read_battery_percentage(self) -> int:
        result = self._read_data('battery_percentage')
        return int(result)

    def read_fan_speed(self) -> int:
        result = self._read_data('fan_speed')
        return int(result)

    def read_fan_mode(self) -> str:
        return self.fan_mode

    def read_board_id(self) -> int:
        result = self._read_data('board_id')
        return int(result)

    def read_shutdown_request(self) -> int:
        result = self._read_data('shutdown_request')
        return int(result)

    def read_cpu_temperature(self) -> float:
        import subprocess
        cmd = 'cat /sys/class/thermal/thermal_zone0/temp'
        try:
            temp = int(subprocess.check_output(cmd, shell=True).decode())
            return round(temp / 1000, 2)
        except Exception as e:
            return 0.0

    def read_all(self) -> dict:
        result = self._read(0, self.total_length)
        result = struct.unpack(self.data_format, bytes(result))
        # print(f"all: {result}")
        data = {}
        for i, name in enumerate(self.data_map):
            data[name] = result[i]
        data['is_charging'] = data['is_charging'] == 1
        data['is_usb_plugged_in'] = data['is_usb_plugged_in'] == 1
        # data['power_source'] = 'Battery' if data['power_source'] == 1 else 'USB'
        data['cpu_temperature'] = self.read_cpu_temperature()
        data['fan_mode'] = self.fan_mode
        data['fan_state'] = self.fan_state
        return data

    def set_fan_speed(self, speed):
        if speed <= 0:
            speed = 0
            self._write('fan_speed', [0])
            return
        elif speed > 100:
            speed = 100

        self.fan_speed = speed
        self.config.set('auto', 'fan_speed', self.fan_speed)
        self._write('fan_speed', [speed])

    def set_fan_state(self, switch: bool):
        self.fan_state = switch
        self.config.set('auto', 'fan_state', self.fan_state)
        if switch:
            self.set_fan_speed(self.fan_speed)
        else:
            self.set_fan_speed(0)

    def set_fan_mode(self, mode: str):
        if mode == 'quiet':
            self.set_fan_speed(40)
        elif mode == 'normal':
            self.set_fan_speed(40)
        elif mode == 'performance':
            self.set_fan_speed(40)

        self.fan_mode = mode
        self.config.set('auto', 'fan_mode', mode)
