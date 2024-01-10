#!/usr/bin/env python3

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from spc.spc import SPC
from spc.ha_api import HA_API
from spc.database import DB
import json

from spc.config import Config
from spc.logger import Logger
from spc.system_status import get_memory_info, get_disks_info, get_network_info, get_cpu_info, get_boot_time

from urllib.parse import urlparse, parse_qs
from os import system as run_command

log = Logger('DASHBOARD')
STATIC_URL = '/opt/spc/www/'
COMMAND_PATH = '/opt/spc/spc_service'

spc = SPC()
ha = HA_API()
db = DB()
config = Config()

PORT = config.getint('dashboard', 'port', default=34001)

parser = argparse.ArgumentParser(description='spc-dashboard')
parser.add_argument('--ssl', action=argparse.BooleanOptionalAction, default=config.getboolean('dashboard', 'ssl'), help='Enable SSL')
parser.add_argument('--ssl-ca-cert', default=config.get('dashboard', 'ssl_ca_cert'), help='SSL CA cert')
parser.add_argument('--ssl-cert', default=config.get('dashboard', 'ssl_cert'), help='SSL cert')

args = parser.parse_args()


class RequestHandler(BaseHTTPRequestHandler):
    api_prefix = '/api/v1.0/'
    routes = ["/", "/dashboard", "/minimal"]

    def send_response(self, code, message=None):
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())
        self.send_header('Access-Control-Allow-Origin', '*')

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
    
    def do_POST(self):

        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        
        if self.path.startswith(self.api_prefix):
            command = self.path[len(self.api_prefix):]
            self.handle_post(command, data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
        
            response_data = {
                'message': 'POST request received',
                'data': data.decode()  # 将 POST 请求的内容转为字符串
            }
            response_json = json.dumps(response_data)
            
            self.wfile.write(response_json.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def handle_get(self, command, param):
        data = None
        if command == "test":
            data = "OK"
        elif command == 'get-all':
            data = spc.read_all()
            data['cpu'] = get_cpu_info()
            data['memory'] = get_memory_info()
            data['disk'] = get_disks_info()
            data['network'] = get_network_info()
            data['boot_time'] = get_boot_time()
            if ha.is_homeassistant_addon():
                data['network']["type"] = ha.get_network_connection_type()
        elif command == 'get-config':
            data = config.get_all()
        elif command == 'get-history':
            n = 1
            if 'n' in param:
                n = int(param['n'][0])
            data = db.get_latest_data('history', n=n)
        elif command == "get-time-range":
            if 'start' in param and 'end' in param:
                start = int(param['start'][0])
                end = int(param['end'][0])
                data = db.get_data_by_time_range('history', start, end)
            else:
                data = "ERROR, start or end not found"
        else:
            return json.dumps({"data": "", "error": f"Command not found {command}"})
        return json.dumps({"data": data})

    def handle_post(self, command, payload):
        payload = payload.decode()
        data = json.loads(payload)['data']
        if command == 'set-fan-mode':
            spc.set_fan_mode(data)
            db.set('history', {'fan_mode': data})
        elif command == 'set-fan-state':
            spc.set_fan_state(data)
            db.set('history', {'fan_state': data})
        elif command == 'set-config':
            db_config = {}
            for section_name in data:
                section = data[section_name]
                for key in section:
                    value = section[key]
                    config.set(section_name, key, value)
                    db_config[f"{section_name}.{key}"] = value
            db.set('config', db_config)
        elif command == 'restart-service':
            run_command(f"python3 {COMMAND_PATH} restart")

    def log_message(self, format, *args):
        msg = format % args
        log(msg, level='INFO')

server_address = ('', PORT)

httpd = HTTPServer(server_address, RequestHandler)
log(f'SPC Dashboard running at http://0.0.0.0:{PORT}/', level='INFO')

# 启动服务器
# os.chdir('/opt/spc/www')
httpd.serve_forever()
