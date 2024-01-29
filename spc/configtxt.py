import os
from .logger import Logger

log = Logger(script_name="configtxt")

class ConfigTxt(object):
    '''
        To setup /boot/config.txt (Raspbian, Kali OSMC, etc)
        /boot/firmware/config.txt (Ubuntu)

    '''
    DEFAULT_FILE_1 = "/boot/config.txt"  # Raspberry Pi OS
    DEFAULT_FILE_2 = "/boot/firmware/config.txt"  # Ubuntu

    def __init__(self, file=None):
        # check if file exists
        self.__isready = True
        if file is None:
            if os.path.exists(self.DEFAULT_FILE_1):
                self.file = self.DEFAULT_FILE_1
            elif os.path.exists(self.DEFAULT_FILE_2):
                self.file = self.DEFAULT_FILE_2
            else:
                log("No config.txt file found.")
                self.__isready = False
                return
        else:
            self.file = file
            if not os.path.exists(file):
                log(f"config.txt not found at {file}")
                self.__isready = False
                return
        # read config file
        with open(self.file, 'r') as f:
            self.configs = f.read()
        self.configs = self.configs.split('\n')

    def isready(self):
        return self.__isready

    def remove(self, expected):
        for key in self.configs:
            if expected in key:
                self.configs.remove(key)
        return self.write_file()

    def comment(self, expected):
        for i in range(len(self.configs)):
            line = self.configs[i]
            if expected in line:
                self.configs[i] = '#' + line
        return self.write_file()

    def set(self, name, value=None, device="[all]"):
        '''
        device : "[all]", "[pi3]", "[pi4]" or other
        '''
        have_excepted = False
        for i in range(len(self.configs)):
            line = self.configs[i]
            if name in line:
                have_excepted = True
                tmp = name
                if value != None:
                    tmp += '=' + value
                if line == tmp:
                    return 1, line
                self.configs[i] = tmp
                break

        if not have_excepted:
            self.configs.append(device)
            tmp = name
            if value != None:
                tmp += '=' + value
            self.configs.append(tmp)
        return self.write_file()

    def write_file(self):
        try:
            content = '\n'.join(self.configs)
            with open(self.file, 'w') as f:
                f.write(content)
            return 0, content
        except Exception as e:
            return -1, e
