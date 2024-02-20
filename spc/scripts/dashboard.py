#!/usr/bin/env python3

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from spc.spc import SPC
from spc.ha_api import HA_API
from spc.database import Database
import json

from spc.config import Config
from spc.logger import Logger

from urllib.parse import urlparse, parse_qs

log = Logger('DASHBOARD')
LOG_PATH = '/opt/spc/log/'
STATIC_URL = '/opt/spc/www/'
COMMAND_PATH = '/opt/spc/spc_service'

spc = SPC(log=log)
ha = HA_API(log=log)
db = Database(log=log)
config = Config(log=log)

DEBUG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

PORT = config.get('dashboard', 'port', default=34001)

parser = argparse.ArgumentParser(description='spc-dashboard')
parser.add_argument('--ssl', action=argparse.BooleanOptionalAction, default=config.get('dashboard', 'ssl'), help='Enable SSL')
parser.add_argument('--ssl-ca-cert', default=config.get('dashboard', 'ssl_ca_cert'), help='SSL CA cert')
parser.add_argument('--ssl-cert', default=config.get('dashboard', 'ssl_cert'), help='SSL cert')

args = parser.parse_args()

mqtt_connected = None

def on_mqtt_connected(client, userdata, flags, rc):
    global mqtt_connected
    if rc==0:
        print("Connected to broker")
        mqtt_connected = True
    else:
        print("Connection failed")
        mqtt_connected = False

def test_mqtt(config, timeout=5):
    global mqtt_connected
    import paho.mqtt.client as mqtt
    from socket import gaierror
    import time
    mqtt_connected = None
    client = mqtt.Client()
    client.on_connect = on_mqtt_connected
    client.username_pw_set(config['username'], config['password'])
    try:
        client.connect(config['host'], config['port'])
    except gaierror:
        return False, "Connection failed, Check hostname and port"
    timestart = time.time()
    while time.time() - timestart < timeout:
        client.loop()
        if mqtt_connected == True:
            return True, None
        elif mqtt_connected == False:
            return False, "Connection failed, Check username and password"
    return False, "Timeout"

def log_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

# get all log files in /opt/spc/log
def get_log_list():
    import os
    log_files = os.listdir(LOG_PATH)
    return log_files

def get_log_level(line):
    for level in DEBUG_LEVELS:
        if f"[{level}]" in line:
            return level
    return DEBUG_LEVELS.index('INFO')
class RequestHandler(BaseHTTPRequestHandler):
    api_prefix = '/api/v1.0/'
    routes = ["/", "/dashboard", "/minimal"]


    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')

    @log_error
    def do_GET(self):
        response = None
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        if self.path.startswith(self.api_prefix):
            # 处理API请求
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            command = parsed_path.path[len(self.api_prefix):]
            response = self.handle_get(command, query_params)
            self.wfile.write(response.encode())
        elif self.path in self.routes:
            # 处理其他请求
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(f"{STATIC_URL}index.html", 'r') as f:
                response = f.read()
                self.wfile.write(response.encode())
        else:
            try:
                filename = self.path[1:]
                
                content_type = {
                    'css': 'text/css',
                    'js': 'application/javascript',
                    'jpg': 'image/jpeg',
                    'png': 'image/png'
                }
                extension = filename.split('.')[-1]
                self.send_response(200)
                self.send_header('Content-type', content_type.get(extension, 'text/plain'))
                self.end_headers()
                with open(f"{STATIC_URL}{filename}", 'rb') as file:
                    self.wfile.write(file.read())
            except FileNotFoundError:
                log('File not found: %s' % filename, level='ERROR')
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'File not found: %s' % filename.encode())

    @log_error
    def do_POST(self):

        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        
        if self.path.startswith(self.api_prefix):
            command = self.path[len(self.api_prefix):]
            result = self.handle_post(command, data)
            if result["status"]:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
        
            response_json = json.dumps(result)
            log(response_json, level='DEBUG')
            self.wfile.write(response_json.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def handle_get(self, command, param):
        data = None
        status = True
        error = None
        if command == "test":
            data = "OK"
            status = True
        elif command == 'test-mqtt':
            mqtt_config = {}
            if 'host' not in param:
                status = False
                error = "ERROR, host not found"
            elif 'port' not in param:
                status = False
                error = "ERROR, port not found"
            elif 'username' not in param:
                status = False
                error = "ERROR, username not found"
            elif 'password' not in param:
                status = False
                error = "ERROR, password not found"
            else:
                mqtt_config['host'] = param['host'][0]
                mqtt_config['port'] = int(param['port'][0])
                mqtt_config['username'] = param['username'][0]
                mqtt_config['password'] = param['password'][0]
                result = test_mqtt(mqtt_config)
                data = {
                    "status": result[0],
                    "error": result[1]
                }
                status = True
        elif command == 'get-config':
            status = True
            data = config.get_all()
            log(f"config: {data}", level='DEBUG')
        elif command == 'get-history':
            n = 1
            if 'n' in param:
                n = int(param['n'][0])
            status = True
            data = db.get('history', n=n)
            # print(data)
        elif command == "get-time-range":
            if 'start' not in param or 'end' not in param:
                status = False
                error = "ERROR, start or end not found"
            else:
                start = int(param['start'][0])
                end = int(param['end'][0])
                key = "*"
                if 'key' in param:
                    key = param['key'][0]
                status = True
                data = db.get_data_by_time_range('history', start, end, key)
        elif command == "get-log-list":
            status = True
            data = get_log_list()
        elif command == "get-log":
            if 'log' not in param:
                status = False
                error = "ERROR, file not specified"
            else:
                log_file = param['log'][0]
                n = 100
                if "n" in param:
                    n = int(param['n'][0])
                filter = []
                if "filter" in param:
                    filter = param['filter'][0]
                    filter = filter.split(',')
                level = "INFO"
                if "level" in param:
                    level = param['level'][0]
                status = True
                with open(f"{LOG_PATH}{log_file}", 'r') as f:
                    lines = f.readlines()
                    lines = lines[-n:]
                    data = []
                    for line in lines:
                        check = True
                        if len(filter) > 0:
                            for f in filter:
                                if f in line:
                                    break
                            else:
                                check = False
                        log_level = DEBUG_LEVELS.index(level)
                        current_log_level = DEBUG_LEVELS.index(get_log_level(line))
                        if current_log_level < log_level:
                            check = False
                        if check:
                            data.append(line)
                status = True
        else:
            status = False
            error = f"Command not found {command}"
        result = {"status": status}
        if status:
            result['data'] = data
        else:
            result['error'] = error
        return json.dumps(result)

    def handle_post(self, command, payload):
        payload = payload.decode()
        payload = json.loads(payload)
        if ("data" not in payload):
            return {"status": False, "error": f'Key [data] not found'}
        data = payload['data']
        if command == 'set-fan-mode':
            spc.set_fan_mode(data)
            db.set('config', {'auto_fan_mode': data})
        elif command == 'set-fan-state':
            spc.set_fan_state(data)
            db.set('config', {'auto_fan_state': data})
        elif command == 'set-config':
            db_config = {}
            print(data)
            for section_name in data:
                section = data[section_name]
                for key in section:
                    value = section[key]
                    config.set(section_name, key, value)
                    print(f"Value: {value}, Type: {type(value)}")
                    db_config[f"{section_name}_{key}"] = value
                    print(f"Set {section_name}.{key} = {value}")
            
            status, result = db.set('config', db_config)
            if not status:
                return {"status": False, "error": result}
        else:
            return {"status": False, "error": f"Command not found [{command}]"}
        return {"status": True, "data": data}

    def log_message(self, format, *args):
        msg = format % args
        log(msg, level='INFO')

server_address = ('', PORT)

httpd = HTTPServer(server_address, RequestHandler)
log(f'SPC Dashboard running at http://0.0.0.0:{PORT}/', level='INFO')

# 启动服务器
# os.chdir('/opt/spc/www')
httpd.serve_forever()
