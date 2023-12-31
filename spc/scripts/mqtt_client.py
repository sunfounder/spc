#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import json
import socket
from spc.logger import Logger
from spc.spc import SPC
from argparse import ArgumentParser
from spc.config import Config

import time

log = Logger("MQTT_Client")

class MQTT_Client:
    def __init__(self, host, port, node_name, username=None, password=None, discovery_perfix="homeassistant"):
        self.host = host
        self.port = port
        self.node_name = node_name
        self.node_id = node_name.lower().replace(' ', '_').replace('-', '_')
        self.username = username
        self.password = password
        self.discovery_perfix = discovery_perfix
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.entities = {}
        self.setters = {}
        self.preset_mode = "normal"
        self._ready = False

    def isready(self):
        return self._ready

    def start(self):
        if (self.username != None and self.password != None):
            self.client.username_pw_set(self.username, self.password)
        try:
            self.client.connect(self.host, self.port)
        except socket.gaierror:
            log(f"Connection Failed. Name or service not known: {self.host}:{self.port}", level="WARNING")
            return
        self.client.loop_start()
        self.init()

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

def main():
    config = Config()
    spc = SPC()

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
            "name": "USB Voltage",
            "device_class": "voltage",
            "unit_of_measurement": "V",
            "get_state": lambda data: data["usb_voltage"] / 1000,
        },
        {
            "component": "sensor",
            "name": "Output Voltage",
            "device_class": "voltage",
            "unit_of_measurement": "V",
            "get_state": lambda data: data["output_voltage"] / 1000,
        },
        {
            "component": "sensor",
            "name": "Output Current",
            "device_class": "current",
            "unit_of_measurement": "A",
            "get_state": lambda data: data["output_current"] / 1000,
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
            "name": "USB Plugged",
            "device_class": "plug",
            "get_state": lambda data: "ON" if data["is_usb_plugged_in"] > 3 else "OFF",
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
    parser = ArgumentParser()
    parser.add_argument("-H", "--host", default=config.get("mqtt", "host"), help="MQTT broker host")
    parser.add_argument("-p", "--port", type=int, default=config.getint("mqtt", "port"), help="MQTT broker port")
    parser.add_argument("-u", "--username", default=config.get("mqtt", "username"), help="MQTT broker username")
    parser.add_argument("-P", "--password", default=config.get("mqtt", "password"), help="MQTT broker password")
    args = parser.parse_args()

    mqtt_client = MQTT_Client(
        host=args.host,
        port=args.port,
        node_name="SPC",
        username=args.username,
        password=args.password,
    )

    for entity in ENTITIES:
        mqtt_client.create_entity(**entity)

    spc = SPC()

    mqtt_client.start()
    if not mqtt_client.isready():
        log("Failed to start MQTT client", level="ERROR")
        exit(1)

    log("Home Assistant MQTT client started", level="INFO")

    last_result = None

    def publish(topic, data):
        log("Publishing to {}: {}".format(topic, data), level="INFO")
        mqtt_client.publish(topic, data)

    while True:
        result = spc.read_all()
        for entity in mqtt_client.entities.values():
            changed = False
            if "get_state" in entity:
                if last_result == None or entity["get_state"](last_result) != entity["get_state"](result):
                    publish(entity["config"]["state_topic"], entity["get_state"](result))
                    changed = True
            if "get_preset_mode" in entity:
                if last_result == None or entity["get_preset_mode"](last_result) != entity["get_preset_mode"](result):
                    publish(entity["config"]["preset_mode_state_topic"], entity["get_preset_mode"](result))
                    changed = True
            if "get_percent" in entity:
                if last_result == None or entity["get_percent"](last_result) != entity["get_percent"](result):
                    publish(entity["config"]["percentage_state_topic"], entity["get_percent"](result))
                    changed = True
            if changed:
                publish(entity["config"]["availability"]["topic"], "online")
        last_result = result
        time.sleep(1)

if __name__ == "__main__":
    main()




