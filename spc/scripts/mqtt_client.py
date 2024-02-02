#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import json
import socket
from spc.logger import Logger
from spc.spc import SPC
from argparse import ArgumentParser
from spc.config import Config
from spc.database import Database

import time

log = Logger("MQTT_Client")

class MQTT_Client:
    TIMEOUT = 5

    def __init__(self, node_name, discovery_perfix="homeassistant"):
        self.node_name = node_name
        self.node_id = node_name.lower().replace(' ', '_').replace('-', '_')
        self.discovery_perfix = discovery_perfix
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.entities = {}
        self.setters = {}
        self.preset_mode = "normal"
        self.connected = None

    def config(self, host, port, username=None, password=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def start(self):
        self.connected = None
        if (self.username != None and self.password != None):
            self.client.username_pw_set(self.username, self.password)
        try:
            self.client.connect(self.host, self.port)
        except socket.gaierror:
            log(f"Connection Failed. Name or service not known: {self.host}:{self.port}", level="WARNING")
            return False
        
        self.client.loop_start()
        timestart = time.time()
        while time.time() - timestart < self.TIMEOUT:
            if self.connected == True:
                log(f"Connected to broker", level="INFO")
                self.init()
                return True
            elif self.connected == False:
                log(f"Connection Failed. Check username and password", level="WARNING")
                return False
            time.sleep(1)
        log(f"Connection Failed. Timeout", level="WARNING")
        return False

    # upload configs:
    def init(self):
        for entity in self.entities.values():
            self.publish(entity["config_topic"], entity["config"])
            if "percentage_command_topic" in entity["config"]:
                topic = entity["config"]["percentage_command_topic"]
                self.client.subscribe(topic)
                self.setters[topic] = entity["set_percent"]
            if "command_topic" in entity["config"]:
                topic = entity["config"]["command_topic"]
                self.client.subscribe(topic)
                self.setters[topic] = entity["set_state"]
            if "preset_mode_command_topic" in entity["config"]:
                topic = entity["config"]["preset_mode_command_topic"]
                self.client.subscribe(topic)
                self.setters[topic] = entity["set_preset_mode"]
            time.sleep(0.1)

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print(f"Connection Failed.")
            self.connected = False
        else:
            print(f"Connected to broker")
            self.connected = True
    
    def on_message(self, client, userdata, msg):
        if msg.topic in self.setters:
            self.setters[msg.topic](msg.payload.decode())

    def create_entity(self,
        component, name,
        device_class=None,
        unit_of_measurement=None,
        get_state=None,
        set_state=None,
        get_percent=None,
        set_percent=None,
        get_preset_mode=None,
        set_preset_mode=None,
        preset_modes=None):

        id = name.lower().replace(' ', '_')
        name = f"{self.node_name} {name}"
        entity_id = f"{self.node_id}_{id}"
        config_topic = f"{self.discovery_perfix}/{component}/{self.node_id}/{id}/config"
        topic_prefix = f"{self.discovery_perfix}/{self.node_id}/{id}"
        state_topic = f"{topic_prefix}/state"
        availability_topic = f"{topic_prefix}/availability"
        percent_topic = f"{topic_prefix}/percent"
        command_topic = f"{topic_prefix}/set"
        percent_command_topic = f"{topic_prefix}/set_percent"
        preset_mode_state_topic = f"{topic_prefix}/preset_mode"
        preset_mode_command_topic = f"{topic_prefix}/set_preset_mode"

        data = {
            "component": component,
            "config_topic": config_topic,
            "config": {
                "name": name,
                "unique_id": f"{entity_id}",
                "state_topic": state_topic,
                "value_template": "{{ value_json.state }}",
                "state_value_template": "{{ value_json.state }}",
                "availability": {
                    "topic": availability_topic,
                    "value_template": "{{ value_json.state }}",
                }
            }
        }
        if device_class != None:
            data["config"]["device_class"] = device_class
        if unit_of_measurement != None:
            data["config"]["unit_of_measurement"] = unit_of_measurement
        if get_state != None:
            data["get_state"] = get_state
        if set_state != None:
            data["set_state"] = set_state
            data["config"]["command_topic"] = command_topic
        if get_percent != None:
            data["get_percent"] = get_percent
        if set_percent != None:
            data["set_percent"] = set_percent
            data["config"]["percentage_value_template"] = "{{ value_json.state }}"
            data["config"]["percentage_state_topic"] = percent_topic
            data["config"]["percentage_command_topic"] = percent_command_topic
        if get_preset_mode != None:
            data["get_preset_mode"] = get_preset_mode
        if set_preset_mode != None:
            data["set_preset_mode"] = set_preset_mode
        if preset_modes != None:
            data["config"]["preset_modes"] = preset_modes
            data["config"]["preset_modes_value_template"] = "{{ value_json.state }}"
            data["config"]["preset_mode_state_topic"] = preset_mode_state_topic
            data["config"]["preset_mode_command_topic"] = preset_mode_command_topic

        self.entities[id] = data

    def publish(self, topic, data):
        self.client.publish(topic, json.dumps(data))
    def publish_state(self, topic, state):
        self.publish(topic, {"state": state})

class SPC_MQTT_Client:
    ENTITIES = [
        {
            "component": "sensor",
            "name": "Battery Voltage",
            "device_class": "voltage",
            "unit_of_measurement": "V",
            "get_state": lambda data: data["battery_voltage"] / 1000,
        },
        {
            "component": "sensor",
            "name": "Battery Current",
            "device_class": "current",
            "unit_of_measurement": "A",
            "get_state": lambda data: data["battery_current"] / 1000,
        },
        {
            "component": "sensor",
            "name": "Battery Percentage",
            "device_class": "battery",
            "unit_of_measurement": "%",
            "get_state": lambda data: data["battery_percentage"],
        },
        {
            "component": "sensor",
            "name": "External Input Voltage",
            "device_class": "voltage",
            "unit_of_measurement": "V",
            "get_state": lambda data: data["external_input_voltage"] / 1000,
        },
        {
            "component": "sensor",
            "name": "Raspberry Pi Voltage",
            "device_class": "voltage",
            "unit_of_measurement": "V",
            "get_state": lambda data: data["raspberry_pi_voltage"] / 1000,
        },
        {
            "component": "sensor",
            "name": "Raspberry Pi Current",
            "device_class": "current",
            "unit_of_measurement": "A",
            "get_state": lambda data: data["raspberry_pi_current"] / 1000,
        },
        {
            "component": "binary_sensor",
            "name": "Power Source",
            "device_class": "power",
            "get_state": lambda data: data["power_source"],
        },
        {
            "component": "binary_sensor",
            "name": "Battery Charging",
            "device_class": "battery_charging",
            "get_state": lambda data: "ON" if data["is_charging"] else "OFF",
        },
        {
            "component": "binary_sensor",
            "name": "Battery Status",
            "device_class": "battery_status",
            "get_state": lambda data: "ON" if data["battery_percentage"] > 25 else "OFF",
        },
        {
            "component": "binary_sensor",
            "name": "External Plugged in",
            "device_class": "plug",
            "get_state": lambda data: "ON" if data["is_plugged_in"] > 3 else "OFF",
        },
        {
            "component": "fan",
            "name": "Fan",
            "get_state": lambda data: "ON" if data["fan_state"] else "OFF",
            "set_state": lambda data: spc.set_fan_state(data == "ON"),
            "get_percent": lambda data: data["fan_speed"],
            "set_percent": lambda data: spc.set_fan_speed(int(data)),
            "get_preset_mode": lambda data: data["fan_state"],
            "set_preset_mode": lambda data: print(data),
            "preset_modes": ["auto", "quiet", "normal", "performance"],
        },
    ]


    def __init__(self):
        self.config = Config(log=log)
        self.spc = SPC(log=log)
        name = self.spc.device.name
        self.mqtt_client = MQTT_Client(node_name=name)
        self.db = Database(log=log)
        self.connected = None

        self.host = self.config.get("mqtt", "host")
        self.port = self.config.get("mqtt", "port")
        self.username = self.config.get("mqtt", "username")
        self.password = self.config.get("mqtt", "password")

        self.result = None

    def set_config(self, host=None, port=None, username=None, password=None):
        configs = {}
        if host != None:
            self.host = host
            self.config.set("mqtt", "host", host)
            configs["mqtt_host"] = host
        if port != None:
            self.port = port
            self.config.set("mqtt", "port", port)
            configs["mqtt_port"] = port
        if username != None:
            self.username = username
            self.config.set("mqtt", "username", username)
            configs["mqtt_username"] = username
        if password != None:
            self.password = password
            self.config.set("mqtt", "password", password)
            configs["mqtt_password"] = password
        
        if len(configs) > 0:
            self.db.set("config", configs)

    def connect_mqtt(self):
        self.mqtt_client.config(self.host, self.port, self.username, self.password)

        for entity in self.ENTITIES:
            self.mqtt_client.create_entity(**entity)

        status = self.mqtt_client.start()
        return status

    def check_config_update(self):
        host = self.db.get("config", "mqtt_host")
        port = self.db.get("config", "mqtt_port")
        username = self.db.get("config", "mqtt_username")
        password = self.db.get("config", "mqtt_password")
        changed = False
        if host != None and host != "" and host != self.host:
            self.host = host
            changed = True
            log(f'MQTT host changed to "{host}"', level="DEBUG")
        if port != None and port != "" and port != self.port:
            self.port = port
            changed = True
            log(f'MQTT port changed to "{port}"', level="DEBUG")
        if username != None and username != "" and username != self.username:
            self.username = username
            changed = True
            log(f'MQTT username changed to "{username}"', level="DEBUG")
        if password != None and password != "" and password != self.password:
            self.password = password
            changed = True
            log(f'MQTT password changed to "{password}"', level="DEBUG")
        return changed

    def publish(self, topic, data):
        log("Publishing to {}: {}".format(topic, data), level="INFO")
        self.mqtt_client.publish(topic, data)

    def run(self):
        result = self.spc.read_all()
        for entity in self.mqtt_client.entities.values():
            # changed = False
            data = {}
            if "get_state" in entity:
                if self.result == None or entity["get_state"](self.result) != entity["get_state"](result):
                    # self.publish(entity["config"]["state_topic"], entity["get_state"](result))
                    # changed = True
                    data["state"] = entity["get_state"](result)
            if "get_preset_mode" in entity:
                if self.result == None or entity["get_preset_mode"](self.result) != entity["get_preset_mode"](result):
                    # self.publish(entity["config"]["preset_mode_state_topic"], entity["get_preset_mode"](result))
                    # changed = True
                    data["state"] = entity["get_preset_mode"](result)
            if "get_percent" in entity:
                if self.result == None or entity["get_percent"](self.result) != entity["get_percent"](result):
                    # self.publish(entity["config"]["percentage_state_topic"], entity["get_percent"](result))
                    # changed = True
                    data["state"] = entity["get_percent"](result)
            # if changed:
            #     self.publish(entity["config"]["availability"]["topic"], "online")
            if len(data) > 0:
                self.publish(entity["config"]["state_topic"], data)
                self.publish(entity["config"]["availability"]["topic"], {"state": "online"})
        self.result = result
        time.sleep(1)

def main():
    RETRY_TIME = 1
    parser = ArgumentParser()
    parser.add_argument("-H", "--host", default=None, help="MQTT broker host")
    parser.add_argument("-p", "--port", type=int, default=None, help="MQTT broker port")
    parser.add_argument("-u", "--username", default=None, help="MQTT broker username")
    parser.add_argument("-P", "--password", default=None, help="MQTT broker password")
    args = parser.parse_args()

    client = SPC_MQTT_Client()
    client.set_config(args.host, args.port, args.username, args.password)
    
    while True:
        connected = client.connect_mqtt()
        if connected:
            break
        else:
            log(f"Failed to start MQTT client", level="ERROR")
            while True:
                time.sleep(RETRY_TIME)
                # log("Checking MQTT client config update", level="DEBUG")
                updated = client.check_config_update()
                if updated:
                    log("MQTT client config updated, Trying to connect", level="DEBUG")
                    break
                # else:
                #     log("MQTT client config not updated", level="DEBUG")

    log("Home Assistant MQTT client started", level="INFO")

    while True:
        client.run()

if __name__ == "__main__":
    main()




