from smbus2 import SMBus
from .utils import run_command

class I2C():
    def __init__(self, address, bus=1):
        self._address = address
        self._bus = bus
        self._smbus = SMBus(self._bus)

    def write_byte(self, data):
        return self._smbus.write_byte(self._address, data)

    def write_byte_data(self, reg, data):
        return self._smbus.write_byte_data(self._address, reg, data)

    def write_word_data(self, reg, data):
        return self._smbus.write_word_data(self._address, reg, data)

    def write_block_data(self, reg, data):
        return self._smbus.write_i2c_block_data(self._address, reg, data)

    def read_byte(self):
        return self._smbus.read_byte(self._address)

    def read_block_data(self, reg, num):
        return self._smbus.read_i2c_block_data(self._address, reg, num)

    def is_ready(self):
        addresses = I2C.scan(self._bus)
        if self._address in addresses:
            return True
        else:
            return False

    @staticmethod
    def scan(busnum=1, force=False):
        devices = []
        for addr in range(0x03, 0x77 + 1):
            read = SMBus.read_byte, (addr,), {'force':force}
            write = SMBus.write_byte, (addr, 0), {'force':force}
            for func, args, kwargs in (read, write):
                try:
                    with SMBus(busnum) as bus:
                        data = func(bus, *args, **kwargs)
                        devices.append(addr)
                        break
                except OSError as expt:
                    if expt.errno == 16:
                        # just busy, maybe permanent by a kernel driver or just temporary by some user code
                        pass
        return devices
