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
    def scan(bus=1):
        cmd = "i2cdetect -y %s" % bus
        _, output = run_command(cmd)

        outputs = output.split('\n')[1:]
        addresses = []
        for tmp_addresses in outputs:
            if tmp_addresses == "":
                continue
            tmp_addresses = tmp_addresses.split(':')[1]
            tmp_addresses = tmp_addresses.strip().split(' ')
            for address in tmp_addresses:
                if address != '--':
                    addresses.append(int(address, 16))
        return addresses
