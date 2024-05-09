#!/usr/bin/env python3
from .i2c import I2C
from .devices import Devices

# class SPC()
# =================================================================
class SPC():

    EXTERNAL_INPUT = 0
    BATTERY = 1

    SHUTDOWN_REQUEST_NONE = 0
    SHUTDOWN_REQUEST_LOW_BATTERY = 1
    SHUTDOWN_REQUEST_BUTTON = 2

    SHUTDOWM_PERCENTAGE_MIN = 10
    POWER_OFF_PERCENTAGE_MIN = 5

    REG_READ_START = 0
    REG_READ_COMMON_LENGTH = 21

    REG_READ_INPUT_VOLTAGE = 0
    REG_READ_INPUT_CURRENT = 2
    REG_READ_OUTPUT_VOLTAGE = 4
    REG_READ_OUTPUT_CURRENT = 6
    REG_READ_BATTERY_VOLTAGE = 8
    REG_READ_BATTERY_CURRENT = 10
    REG_READ_BATTERY_PERCENTAGE = 12
    REG_READ_BATTERY_CAPACITY = 13
    REG_READ_POWER_SOURCE = 15
    REG_READ_IS_INPUT_PLUGGED_IN = 16
    REG_READ_IS_CHARGING = 18
    REG_READ_FAN_POWER = 19
    REG_READ_SHUTDOWN_REQUEST = 20

    REG_READ_FIRMWARE_VERSION_MAJOR = 128
    REG_READ_FIRMWARE_VERSION_MINOR = 129
    REG_READ_FIRMWARE_VERSION_PATCH = 130
    REG_READ_RTC_CODE = 131
    REG_READ_RTC_YEAR = 132
    REG_READ_RTC_MONTH = 133
    REG_READ_RTC_DAY = 134
    REG_READ_RTC_HOUR = 135
    REG_READ_RTC_MINUTE = 136
    REG_READ_RTC_SECOND = 137
    REG_READ_RTC_MILLISECOND = 138
    REG_READ_DEFAULT_ON = 139
    REG_READ_BOARD_ID = 140
    REG_READ_SHUTDOWN_PERCENTAGE = 143
    REG_READ_POWER_OFF_PERCENTAGE = 144

    REG_WRITE_FAN_POWER = 0
    REG_WRITE_RTC_YEAR = 1
    REG_WRITE_RTC_MONTH = 2
    REG_WRITE_RTC_DAY = 3
    REG_WRITE_RTC_HOUR = 4
    REG_WRITE_RTC_MINUTE = 5
    REG_WRITE_RTC_SECOND = 6
    REG_WRITE_RTC_MILLISECOND = 7
    REG_WRITE_RTC_SETTING = 8
    REG_WRITE_SHUTDOWN_PERCENTAGE = 9
    REG_WRITE_POWER_OFF_PERCENTAGE = 10

    def __init__(self, get_logger=None):
        if get_logger is None:
            import logging
            get_logger = logging.getLogger
        self.log = get_logger(__name__)

        addresses = I2C.scan()
        if not addresses:
            raise IOError(f"SPC init error: I2C device not found")
        elif len(addresses) > 0:
            for addr in Devices.ADDRESS:
                if addr in addresses:
                    self.addr = addr
                    break
            else:
                raise IOError(f"SPC init error: I2C device not found")
        self.device = Devices(self.addr)
        self.i2c = I2C(self.addr)
        if not self.i2c.is_ready():
            self.log.error(f'SPC init error: I2C device not found at address 0x{self.addr:02X}')
            self._is_ready = False
            return

        self.log.info(f'SPC detect device: {self.device.name} ({self.device.id})')
        self._is_ready = True

    def is_ready(self):
        return self._is_ready

    def read_input_voltage(self) -> int:
        if 'input_voltage' not in self.device.peripherals:
            raise ValueError(f"Input voltage not supported for {self.device.name}")
        return self.i2c.read_word_data(self.REG_READ_INPUT_VOLTAGE)

    def read_input_current(self) -> int:
        if 'input_current' not in self.device.peripherals:
            raise ValueError(f"Input current not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_INPUT_CURRENT)

    def read_output_voltage(self) -> int:
        if 'output_voltage' not in self.device.peripherals:
            raise ValueError(f"Output voltage not supported for {self.device.name}")
        return self.i2c.read_word_data(self.REG_READ_OUTPUT_VOLTAGE)

    def read_output_current(self) -> int:
        if 'output_current' not in self.device.peripherals:
            raise ValueError(f"Output current not supported for {self.device.name}")
        return self.i2c.read_word_data(self.REG_READ_OUTPUT_CURRENT)

    def read_battery_voltage(self) -> int:
        if 'battery_voltage' not in self.device.peripherals:
            raise ValueError(f"Battery voltage not supported for {self.device.name}")
        return self.i2c.read_word_data(self.REG_READ_BATTERY_VOLTAGE)

    def read_battery_current(self) -> int:
        if 'battery_current' not in self.device.peripherals:
            raise ValueError(f"Battery current not supported for {self.device.name}")
        return self.i2c.read_word_data(self.REG_READ_BATTERY_CURRENT)

    def read_battery_percentage(self) -> int:
        if 'battery_percentage' not in self.device.peripherals:
            raise ValueError(f"Battery percentage not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_BATTERY_PERCENTAGE)

    def read_battery_capacity(self) -> int:
        if 'battery_capacity' not in self.device.peripherals:
            raise ValueError(f"Battery capacity not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_BATTERY_CAPACITY)

    def read_power_source(self) -> int:
        if 'power_source' not in self.device.peripherals:
            raise ValueError(f"Power source not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_POWER_SOURCE)

    def read_is_input_plugged_in(self) -> int:
        if 'is_input_plugged_in' not in self.device.peripherals:
            raise ValueError(f"Input plugged in status not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_IS_INPUT_PLUGGED_IN)

    def read_is_charging(self) -> int:
        if 'is_charging' not in self.device.peripherals:
            raise ValueError(f"Charging status not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_IS_CHARGING)

    def read_fan_power(self) -> int:
        if 'fan_power' not in self.device.peripherals:
            raise ValueError(f"Fan power not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_FAN_POWER)

    def read_shutdown_request(self) -> int:
        if 'shutdown_request' not in self.device.peripherals:
            raise ValueError(f"Shutdown request not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_SHUTDOWN_REQUEST)

    def read_firmware_version(self):
        result = self.i2c.read_block_data(self.REG_READ_FIRMWARE_VERSION_MAJOR, 3)
        _version = f"{result[0]}.{result[1]}.{result[2]}"
        return _version

    def read_rtc(self):
        if 'rtc' not in self.device.peripherals:
            raise ValueError(f"RTC not supported for {self.device.name}")
        result = self.i2c.read_block_data(self.REG_READ_RTC_CODE, 7)
        result[6] = int(1000*result[6]/128) # 1/128 seconds to millisecond
        return result

    def read_default_on(self) -> int:
        if 'default_on' not in self.device.peripherals:
            raise ValueError(f"Default on not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_DEFAULT_ON)

    def read_board_id(self) -> int:
        return self.i2c.read_byte_data(self.REG_READ_BOARD_ID)

    def read_shutdown_percentage(self) -> int:
        if 'shutdown_percentage' not in self.device.peripherals:
            raise ValueError(f"Shutdown percentage not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_SHUTDOWN_PERCENTAGE)

    def read_power_off_percentage(self) -> int:
        if 'power_off_percentage' not in self.device.peripherals:
            raise ValueError(f"Power off percentage not supported for {self.device.name}")
        return self.i2c.read_byte_data(self.REG_READ_POWER_OFF_PERCENTAGE)

    def _unpack_u16(self, data, reg):
        return data[reg+1] << 8 | data[reg]

    def read_all(self) -> dict:
        result = self.i2c.read_block_data(self.REG_READ_START, self.REG_READ_COMMON_LENGTH)
        data = {}
        if 'input_voltage' in self.device.peripherals:
            data['input_voltage'] = self._unpack_u16(result, self.REG_READ_INPUT_VOLTAGE)
        if 'input_current' in self.device.peripherals:
            data['input_current'] = self._unpack_u16(result, self.REG_READ_INPUT_CURRENT)
        if 'output_voltage' in self.device.peripherals:
            data['output_voltage'] = self._unpack_u16(result, self.REG_READ_OUTPUT_VOLTAGE)
        if 'output_current' in self.device.peripherals:
            data['output_current'] = self._unpack_u16(result, self.REG_READ_OUTPUT_CURRENT)
        if 'battery_voltage' in self.device.peripherals:
            data['battery_voltage'] = self._unpack_u16(result, self.REG_READ_BATTERY_VOLTAGE)
        if 'battery_current' in self.device.peripherals:
            data['battery_current'] = self._unpack_u16(result, self.REG_READ_BATTERY_CURRENT)
        if 'battery_percentage' in self.device.peripherals:
            data['battery_percentage'] = result[self.REG_READ_BATTERY_PERCENTAGE]
        if 'battery_capacity' in self.device.peripherals:
            data['battery_capacity'] = self._unpack_u16(result, self.REG_READ_BATTERY_CAPACITY)
        if 'power_source' in self.device.peripherals:
            data['power_source'] = result[self.REG_READ_POWER_SOURCE]
        if 'is_input_plugged_in' in self.device.peripherals:
            data['is_input_plugged_in'] = result[self.REG_READ_IS_INPUT_PLUGGED_IN] == 1
        if 'is_charging' in self.device.peripherals:
            data['is_charging'] = result[self.REG_READ_IS_CHARGING] == 1
        if 'fan_power' in self.device.peripherals:
            data['fan_power'] = result[self.REG_READ_FAN_POWER]
        if 'shutdown_request' in self.device.peripherals:
            data['shutdown_request'] = result[self.REG_READ_SHUTDOWN_REQUEST]
        return data

    def write_fan_power(self, power):
        if 'fan' not in self.device.peripherals:
            raise ValueError(f"Fan not supported for {self.device.name}")
        if power <= 0:
            power = 0
        elif power > 100:
            power = 100

        self.i2c.write_byte_data(self.REG_WRITE_FAN_POWER, power)

    def write_shutdown_percentage(self, percentage):
        if 'shutdown_percentage' not in self.device.peripherals:
            raise ValueError(f"Shutdown percentage not supported for {self.device.name}")
        if percentage <= self.SHUTDOWM_PERCENTAGE_MIN:
            percentage = self.SHUTDOWM_PERCENTAGE_MIN
        elif percentage > 100:
            percentage = 100
        self.i2c.write_byte_data(self.REG_WRITE_SHUTDOWN_PERCENTAGE, percentage)

    def write_power_off_percentage(self, percentage):
        if 'power_off_percentage' not in self.device.peripherals:
            raise ValueError(f"Power off percentage not supported for {self.device.name}")
        if percentage <= self.POWER_OFF_PERCENTAGE_MIN:
            percentage = self.POWER_OFF_PERCENTAGE_MIN
        elif percentage > 100:
            percentage = 100
        self.i2c.write_byte_data(self.REG_WRITE_POWER_OFF_PERCENTAGE, percentage)

    def write_rtc(self, date:list):
        '''
            date, list for [year, month, day, hour, minute, second, 1/128 second]
        '''
        if 'rtc' not in self.device.peripherals:
            raise ValueError(f"RTC not supported for {self.device.name}")
        date.append(1)
        self.i2c.write_block_data(self.REG_WRITE_RTC_YEAR, date)
