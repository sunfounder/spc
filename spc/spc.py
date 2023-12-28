#!/usr/bin/env python3
from .i2c import I2C
import struct
from .config import Config
from .system_status import *
from .devices import Devices
import sys

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
    rtc_time_map = (23, 7, '>BBBBBBB')
    firmware_version_map = (30, 3, '>BBB')

    basic_data = [
        'board_id',
        'board_name',
        'shutdown_request',
        'cpu_temperature',
    ]
    peripheral_data = {
        'battery': [
            'battery_voltage',
            'battery_current',
            'battery_capactiy',
            'battery_percentage',
            'is_charging',
        ],
        'usb_in': [
            'usb_voltage',
            'usb_current',
            'is_usb_plugged_in',
        ],
        'output': [
            'output_voltage',
            'output_current',
        ],
        'fan': [
            'fan_speed',
            'fan_mode',
            'fan_state',
        ],
        'power_source_sensor': [
            'power_source',
        ]
    }
    control_map = {
        'fan_speed': (0, 1),
    }

    def __init__(self, address=I2C_ADDRESS):
        self.addr = address

        self.i2c = I2C(self.addr)
        if not self.i2c.is_ready():
            raise IOError(f'Pironman U1 init error: I2C device not found at address 0x{self.addr:02X}')

        id = self._read_data('board_id')
        self.device = Devices(id)
        log(f'SPC detect device: {self.device.name} ({self.device.id})')
        self.config = Config()
        self.fan_mode = self.config.get('auto', 'fan_mode')
        self.fan_state = self.config.get('auto', 'fan_state') == 'True'
        self.fan_speed = int(self.config.get('auto', 'fan_speed'))
        if self.fan_state:
            self.set_fan_speed(self.fan_speed)

    def _read(self, start, length):
        _retry = 5
        for i in range(_retry):
            try:
                result = self.i2c.read_block_data(start, length)
                break
            except TimeoutError:
                time.sleep(.01)
                continue
            # other exceptions will be raised
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"_read() TimeoutError: {exc_type} - {exc_value}")
            raise

        return result

    def _write(self, name: str, value: list):
        self.i2c.write_block_data(0, value)

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

    def _read_all(self) -> dict:
        result = self._read(0, self.total_length)
        result = struct.unpack(self.data_format, bytes(result))
        # print(f"all: {result}")
        data = {}
        for i, name in enumerate(self.data_map):
            data[name] = result[i]
        data['board_name'] = self.device.name
        data['is_charging'] = data['is_charging'] == 1
        data['is_usb_plugged_in'] = data['is_usb_plugged_in'] == 1
        # data['power_source'] = 'Battery' if data['power_source'] == 1 else 'USB'
        data['cpu_temperature'] = get_cpu_temperature()
        data['fan_mode'] = self.fan_mode
        data['fan_state'] = self.fan_state
        return data

    def read_all(self) -> dict:
        all_data = self._read_all()
        data = {}
        for data_name in self.basic_data:
            data[data_name] = all_data[data_name]
        for peripheral in self.device.peripherals:
            if peripheral not in self.peripheral_data:
                continue
            for data_name in self.peripheral_data[peripheral]:
                data[data_name] = all_data[data_name]
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
            self.set_fan_speed(70)
        elif mode == 'performance':
            self.set_fan_speed(100)

        self.fan_mode = mode
        self.config.set('auto', 'fan_mode', mode)


    def set_rtc(self, date:list):
        '''
            date, list for [year, month, day, hour, minute, second, 1/128 second]
        '''
        date.append(1)
        self.i2c.write_block_data(1, date)
        # self.i2c.write_block_data(7, [1]) #enable set

    def read_rtc(self):
        _start, _len, _format = self.rtc_time_map
        result = self.i2c.read_block_data(_start, _len)
        result = struct.unpack(_format, bytes(result))
        result = list(result) # change tuple to list
        result[6] = int(1000*result[6]/128) # 1/128 seconds to millisecond
        return result

    def read_firmware_version(self):
        _start, _len, _format = self.firmware_version_map
        result = self.i2c.read_block_data(_start, _len)
        result = struct.unpack(_format, bytes(result))
        _version = f"{result[0]}.{result[1]}.{result[2]}"
        return _version


