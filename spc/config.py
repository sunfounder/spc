import os
from .utils import run_command
from .logger import Logger
from .ha_api import HA_API
import json

log = Logger(script_name="config")

class Config:
    default_config_file = "/opt/spc/config.json"
    default_ha_config_file = "/data/config.json" # home assistant addon config file
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
            "shutdown_battery_pct": 30,
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
        "data-logger": {
            "interval": 1,
        }
    }

    def __init__(self, config_file=None):
        if config_file is None:
            if HA_API.is_homeassistant_addon():
                config_file = self.default_ha_config_file
            else:
                config_file = self.default_config_file
        self.config_file = config_file
        
        if not os.path.exists(config_file):
            print('Configuration file does not exist, recreating ...')
            # create config_file
            status, result = run_command(cmd=f'sudo touch {config_file}' +
                                        f' && sudo chmod 777 {config_file}')

            self.config.read_dict(self.default_values)
            with open(self.config_file, 'w') as f:
                self.config.write(f)

            if status != 0:
                print('create config_file failed:\n%s' % result)
                raise Exception(result)
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def get(self, section, key, default=None):
        edited = False
        if section not in self.config:
            self.config[section] = {}
            edited = True
            log(f"Section {section} not found in config file, adding ...")
        if key not in self.config[section]:
            self.config[section][key] = default
            edited = True
            log(f"Key {key} not found in section {section}, adding ...")
        if edited:
            self.save()

        return self.config[section][key]

    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
            log(f"Section {section} not found in config file, adding ...")
        self.config[section][key] = value
        self.save()
        return value

    def get_all(self):
        return self.config
