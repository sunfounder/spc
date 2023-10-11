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
            'pid_out',
            'dac_vol',
            'test',
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

    data_format = '>HhHHHHBBBBBBBhHH'
    total_length = 25
    data_map = {
        'battery_voltage': (0, 2),  # data start index, data length
        'battery_current': (2, 2),
        'usb_voltage': (4, 2),
        'output_voltage': (6, 2),
        'output_current': (8, 2),
        'ref_voltage': (10, 2),
        'power_source': (12, 1),
        'is_usb_plugged_in': (13, 1),
        'is_charging': (14, 1),
        'fan_speed': (15, 1),
        'battery_percentage': (16, 1),
        'board_id': (17, 1),
        'shutdown_request': (18, 1),
        'pid_out': (19, 2),
        'dac_vol': (21, 2),
        'test': (23, 2),
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

    def _read_data(self, name: str, format: str):
        _start, _len = self.data_map[name]
        result = self._read(_start, _len)
        result = struct.unpack(format, bytes(result))
        return result[0]

    def read_battery_voltage(self) -> int:
        result = self._read_data('battery_voltage', '>H')
        return int(result)

    def read_battery_current(self) -> int:
        result = self._read_data('battery_current', '>h')
        return int(result)

    def read_usb_voltage(self) -> int:
        result = self._read_data('usb_voltage', '>H')
        return int(result)

    def read_output_voltage(self) -> int:
        result = self._read_data('output_voltage', '>H')
        return int(result)

    def read_output_current(self) -> int:
        result = self._read_data('output_current', '>H')
        return int(result)

    def read_ref_voltage(self) -> int:
        result = self._read_data('ref_voltage', '>H')
        return int(result)

    def read_power_source(self) -> int:
        result = self._read_data('power_source', 'B')
        return int(result)

    def read_is_usb_plugged_in(self) -> int:
        result = self._read_data('is_usb_plugged_in', 'B')
        return int(result)

    def read_is_charging(self) -> int:
        result = self._read_data('is_charging', 'B')
        return int(result)

    def read_battery_percentage(self) -> int:
        result = self._read_data('battery_percentage', 'B')
        return int(result)

    def read_fan_speed(self) -> int:
        result = self._read_data('fan_speed', 'B')
        return int(result)

    def read_fan_mode(self) -> str:
        return self.fan_mode

    def read_board_id(self) -> int:
        result = self._read_data('board_id', 'B')
        return int(result)

    def read_shutdown_request(self) -> int:
        result = self._read_data('shutdown_request', 'B')
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
        data = {}
        for i, name in enumerate(self.data_map):
            data[name] = result[i]
        data['is_charging'] = data['is_charging'] == 1
        data['is_usb_plugged_in'] = data['is_usb_plugged_in'] == 1
        data['power_source'] = 'USB' if data['power_source'] == 1 else 'Battery'
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
