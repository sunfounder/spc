#!/usr/bin/env python3
from .i2c import I2C
import struct
from .config import Config
from .logger import Logger
from .system_status import get_cpu_temperature
from .devices import Devices
import sys
import time

# init log
# =================================================================
log = Logger("SPC")

# class SPC()
# =================================================================
class SPC():

    I2C_ADDRESS = 0x5A

    EXTERNAL_INPUT = 0
    BATTERY = 1

    SHUTDOWM_BATTERY_MIN = 10

    data_format = '>BHHhHhHhBHBBBBB'
    total_length = 23
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
        'fan_speed': (21, 1, 'B'),
        'shutdown_request': (22, 1, 'B'),
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
        'cpu_temperature',
    ]
    peripheral_data = {
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
            raise IOError(f'SPC init error: I2C device not found at address 0x{self.addr:02X}')

        id = self._read_data('board_id')
        self.device = Devices(id)
        log(f'SPC detect device: {self.device.name} ({self.device.id})')
        self.config = Config()
        self.fan_mode = self.config.get('auto', 'fan_mode')
        self.fan_state = self.config.get('auto', 'fan_state') == 'True'
        self.fan_speed = int(self.config.get('auto', 'fan_speed'))
        if self.fan_state:
            self.set_fan_speed(self.fan_speed)
        # shutdown_battery_pct
        self.read_shutdown_battery_pct()

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

    def read_fan_speed(self) -> int:
        result = self._read_data('fan_speed')
        return int(result)

    def read_fan_mode(self) -> str:
        self.fan_mode = self.config.get('auto', 'fan_mode')
        return self.fan_mode

    def read_fan_state(self) -> str:
        self.fan_state = self.config.get('auto', 'fan_state') == 'True'
        return self.fan_state

    def read_board_id(self) -> int:
        result = self._read_data('board_id')
        return int(result)

    def read_shutdown_request(self) -> int:
        result = self._read_data('shutdown_request')
        return int(result)

    def read_shutdown_battery_pct(self) -> int:
        try:
            self.shutdown_battery_pct= int(self.config.get('auto', 'shutdown_battery_pct', default=25))
            if self.shutdown_battery_pct <= self.SHUTDOWM_BATTERY_MIN:
                self.shutdown_battery_pct = self.SHUTDOWM_BATTERY_MIN
                self.config.set('auto', 'shutdown_battery_pct', self.shutdown_battery_pct)
            elif self.shutdown_battery_pct > 100:
                self.shutdown_battery_pct = 100
                self.config.set('auto', 'shutdown_battery_pct', self.shutdown_battery_pct)
        except:
            self.shutdown_battery_pct = 100
            self.config.set('auto', 'shutdown_battery_pct', self.shutdown_battery_pct)

        return self.shutdown_battery_pct

    
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
        data['cpu_temperature'] = get_cpu_temperature()
        data['fan_mode'] = self.read_fan_mode()
        data['fan_state'] = self.read_fan_state()
        data['shutdown_battery_pct'] = self.shutdown_battery_pct
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
        _start, _len = self.control_map['fan_speed']
        if speed <= 0:
            speed = 0
            self._write(_start, [0])
            return  # do not config
        elif speed > 100:
            speed = 100

        self.fan_speed = speed
        self.config.set('auto', 'fan_speed', self.fan_speed)
        self._write(_start, [speed])

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

    def set_shutdown_battery_pct(self, precentage):
        if percentage <= self.SHUTDOWM_BATTERY_MIN:
            percentage = self.SHUTDOWM_BATTERY_MIN
        elif percentage > 100:
            percentage = 100

        self.shutdown_battery_pct = precentage
        self.config.set('auto', 'shutdown_battery_pct', precentage)

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