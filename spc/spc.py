#!/usr/bin/env python3
from .i2c import I2C
import struct
from .devices import Devices
import sys
import time

# class SPC()
# =================================================================
class SPC():

    I2C_ADDRESS = 0x5A

    EXTERNAL_INPUT = 0
    BATTERY = 1

    SHUTDOWN_REQUEST_NONE = 0
    SHUTDOWN_REQUEST_LOW_BATTERY = 1
    SHUTDOWN_REQUEST_BUTTON = 2
    SHUTDOWN_REQUESTS = [
        SHUTDOWN_REQUEST_LOW_BATTERY,
        SHUTDOWN_REQUEST_BUTTON,
    ]

    SHUTDOWM_BATTERY_MIN = 10

    data_format = '>BHHhHhHhBHBBBBBB'
    total_length = 24
    data_map = {
        'board_id': (0, 1, 'B'),  # data start index, data length, format
        'vcc_voltage': (1, 2, '>H'),
        'external_input_voltage': (3, 2, '>H'),
        'external_input_current': (5, 2, '>h'),
        'raspberry_pi_voltage': (7, 2, '>H'),
        'raspberry_pi_current': (9, 2, '>h'),
        'battery_voltage': (11, 2, '>H'),
        'battery_current': (13, 2, '>h'),
        'battery_percentage': (15, 1, 'B'),
        'battery_capacity': (16, 2, '>H'),
        #
        'power_source': (18, 1, 'B'),
        'is_plugged_in': (19, 1, 'B'),
        'is_charging': (20, 1, 'B'),
        'fan_power': (21, 1, 'B'),
        'shutdown_request': (22, 1, 'B'),
        'shutdown_battery_pct': (23, 1, 'B'),
        #
        # must be continuous in read_all()
    }

    rtc_time_map = (23, 7, '>BBBBBBB')  # Detach from data_map to not read on read_all
    firmware_version_map = (30, 3, '>BBB')
    rstflag_map = (33, 1, '>B')

    basic_data = [
        'board_id',
        'board_name',
        'shutdown_request',
    ]
    PERIPHERAL_DATA_MAP = {
        'battery': [
            'battery_voltage',
            'battery_current',
            'battery_capacity',
            'battery_percentage',
            'is_charging',
            'shutdown_battery_pct',
        ],
        'external_input': [
            'external_input_voltage',
            'external_input_current',
            'is_plugged_in',
        ],
        'raspberry_pi_power': [
            'raspberry_pi_voltage',
            'raspberry_pi_current',
        ],
        'fan': [
            'fan_power',
        ],
        'power_source_sensor': [
            'power_source',
        ]
    }
    control_map = {
        'fan_power': (0, 1),
        'shutdown_battery_pct': (1, 1),
    }

    def __init__(self, address=I2C_ADDRESS, get_logger=None):
        if get_logger is None:
            import logging
            get_logger = logging.getLogger
        self.log = get_logger(__name__)

        self.addr = address
        self.i2c = I2C(self.addr)
        if not self.i2c.is_ready():
            self.log.error(f'SPC init error: I2C device not found at address 0x{self.addr:02X}')
            self._is_ready = False
            return

        id = self._read_data('board_id')
        self.device = Devices(id)
        self.log.info(f'SPC detect device: {self.device.name} ({self.device.id})')
        self._is_ready = True

    def is_ready(self):
        return self._is_ready

    def _read(self, start, length):
        _retry = 5
        for _ in range(_retry):
            try:
                result = self.i2c.read_block_data(start, length)
                break
            except TimeoutError:
                time.sleep(0.01)
                continue
            # other exceptions will be raised
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"_read() TimeoutError: {exc_type} - {exc_value}")
            raise

        return result

    def _write(self, start, value: list):
        _retry = 5
        for _ in range(_retry):
            try:
                self.i2c.write_block_data(start, value)
                break
            except TimeoutError:
                time.sleep(.01)
                continue
            # other exceptions will be raised
        else:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"_write() TimeoutError: {exc_type} - {exc_value}")
            raise

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

    def read_external_input_voltage(self) -> int:
        result = self._read_data('external_input_voltage')
        return int(result)

    def read_external_input_current(self) -> int:
        result = self._read_data('external_input_current')
        return int(result)

    def read_raspberry_pi_voltage(self) -> int:
        result = self._read_data('raspberry_pi_voltage')
        return int(result)

    def read_raspberry_pi_current(self) -> int:
        result = self._read_data('raspberry_pi_current')
        return int(result)

    def read_ref_voltage(self) -> int:
        result = self._read_data('ref_voltage')
        return int(result)

    def read_power_source(self) -> int:
        result = self._read_data('power_source')
        return int(result)

    def read_is_plugged_in(self) -> int:
        result = self._read_data('is_plugged_in')
        return int(result)

    def read_is_charging(self) -> int:
        result = self._read_data('is_charging')
        return int(result)

    def read_battery_percentage(self) -> int:
        result = self._read_data('battery_percentage')
        return int(result)

    def read_fan_power(self) -> int:
        result = self._read_data('fan_power')
        return int(result)

    def read_board_id(self) -> int:
        result = self._read_data('board_id')
        return int(result)

    def read_shutdown_request(self) -> int:
        result = self._read_data('shutdown_request')
        return int(result)

    def read_shutdown_battery_pct(self) -> int:
        result = self._read_data('shutdown_battery_pct')
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
        data['is_plugged_in'] = data['is_plugged_in'] == 1
        return data

    def read_all(self) -> dict:
        all_data = self._read_all()
        data = {}
        for data_name in self.basic_data:
            data[data_name] = all_data[data_name]
        for peripheral in self.device.peripherals:
            if peripheral not in self.PERIPHERAL_DATA_MAP:
                continue
            for data_name in self.PERIPHERAL_DATA_MAP[peripheral]:
                data[data_name] = all_data[data_name]
        return data

    def set_fan_power(self, power):
        _start, _len = self.control_map['fan_power']
        if power <= 0:
            power = 0
        elif power > 100:
            power = 100

        self._write(_start, [power])

    def set_shutdown_battery_pct(self, percentage):
        _start, _len = self.control_map['shutdown_battery_pct']
        if percentage <= self.SHUTDOWM_BATTERY_MIN:
            percentage = self.SHUTDOWM_BATTERY_MIN
        elif percentage > 100:
            percentage = 100

        self._write(_start, [percentage])

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

    def read_rstflag(self):
        _start, _len, _format = self.rstflag_map
        result = self.i2c.read_block_data(_start, _len)
        result = struct.unpack(_format, bytes(result))
        return result[0]