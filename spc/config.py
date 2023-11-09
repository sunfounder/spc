import configparser
import os
from .utils import run_command, Logger

log = Logger(script_name="config")

class Config:
    default_config_file = "/opt/spc/config"
    default_values = {
        "auto": {
            "reflash_interval": 1,
            "retry_interval": 3,
            "fan_mode": "auto",
            "fan_state": True,
            "fan_speed": 65,
            "temperature_unit": "C",
            "rgb_switch": True,
            "rgb_style": 'breath',  # 'breath', 'leap', 'flow', 'raise_up', 'colorful'
            "rgb_color": "#0a1aff",
            "rgb_speed": 50,
            "rgb_pwm_frequency": 1000,
            "rgb_pin": 10,  # 10, 12, 21
        },
        "mqtt": {
            "host": "core-mosquitto",
            "port": 1883,
            "username": "mqtt",
            "password": "mqtt"
        },
        "dashboard": {
            "port": 34001,
            "ssl": False,
            "ssl_ca_cert": "",
            "ssl_cert": ""
        },
    }

    def __init__(self, config_file=default_config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            print('Configuration file does not exist, recreating ...')
            # create config_file
            status, result = run_command(cmd=f'sudo touch {config_file}' +
                                        f' && sudo chmod 775 {config_file}')
            if status != 0:
                print('create config_file failed:\n%s' % result)
                raise Exception(result)

        self.config.read(config_file)

    def get(self, section, key, default=None):
        if default is None:
            default = self.default_values.get(section, {}).get(key, None)
        try:
            return self.config.get(section, key)
        except configparser.NoSectionError:
            self.config[section] = {}
            self.set(section, key, default)
            log(f'NoSectionError: {section} {key} {default}', level='DEBUG')
            return default
        except configparser.NoOptionError:
            self.set(section, key, default)
            log(f'NoOptionError: {section} {key} {default}', level='DEBUG')
            return default

    def getboolean(self, section, key, default=None):
        result = self.get(section, key, default)
        if result == 'True':
            return True
        elif result == 'False':
            return False
        else:
            return result

    def getint(self, section, key, default=None):
        result = self.get(section, key, default)
        try:
            return int(result)
        except ValueError:
            return result

    def set(self, section, key, value):
        self.config[section][key] = str(value)
        with open(self.config_file, 'w') as f:
            self.config.write(f)
