#!/usr/bin/env python3

import sys
from spc import __version__
import os
import time
import threading
import argparse


DEPENDENCIES = [
    "python3-smbus",
    "unzip",
]

SPC_DASHBOARD_DOWNLOAD_LINK = "https://github.com/sunfounder/spc-dashboard/releases/latest/download/spc-dashboard.zip"

parser = argparse.ArgumentParser(description='Install script for SPC')
parser.add_argument('--no-dep', action='store_true',
                    help='Do not install dependencies')
parser.add_argument('--skip-reboot', action='store_true',
                    help='Do not reboot after install')
parser.add_argument('--disable-autostart', action='store_true',
                    help='Do not start SPC automatically')
parser.add_argument('--mqtt-client', action=argparse.BooleanOptionalAction, default=False, help='Enable MQTT client or not')
args = parser.parse_args()

if os.geteuid() != 0:
    print("Script must be run as root. Try 'python3 install.py'")
    sys.exit(1)

errors = []

user_name = os.getlogin()

#
# =================================================================


def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True)
    p.wait()
    result = p.stdout.read()
    status = p.poll()
    return status, result


at_work_tip_sw = False


def working_tip():
    char = ['/', '-', '\\', '|']
    i = 0
    global at_work_tip_sw
    while at_work_tip_sw:
        i = (i + 1) % 4
        sys.stdout.write('\033[?25l')  # cursor invisible
        sys.stdout.write('%s\033[1D' % char[i])
        sys.stdout.flush()
        time.sleep(0.5)

    sys.stdout.write(' \033[1D')
    sys.stdout.write('\033[?25h')  # cursor visible
    sys.stdout.flush()


def do(msg="", cmd=""):
    print(" - %s... " % (msg), end='', flush=True)
    # at_work_tip start
    global at_work_tip_sw
    at_work_tip_sw = True
    _thread = threading.Thread(target=working_tip)
    _thread.daemon = True
    _thread.start()
    # process run
    status, result = run_command(cmd)
    # at_work_tip stop
    at_work_tip_sw = False
    while _thread.is_alive():
        time.sleep(0.01)
    # status
    if status == 0:
        print('Done')
    else:
        print('\033[1;35mError\033[0m')
        errors.append("%s error:\n  Status:%s\n  Error:%s" %
                      (msg, status, result))


def set_config(msg="", name="", value=""):
    print(" - %s... " % (msg), end='', flush=True)
    try:
        Config().set(name, value)
        print('Done')
    except Exception as e:
        print('\033[1;35mError\033[0m')
        errors.append("%s error:\n Error:%s" % (msg, e))


class Config(object):
    '''
        To setup /boot/config.txt (Raspbian, Kali OSMC, etc)
        /boot/firmware/config.txt (Ubuntu)

    '''
    DEFAULT_FILE_1 = "/boot/config.txt"  # raspbian
    DEFAULT_FILE_2 = "/boot/firmware/config.txt"  # ubuntu

    def __init__(self, file=None):
        # check if file exists
        if file is None:
            if os.path.exists(self.DEFAULT_FILE_1):
                self.file = self.DEFAULT_FILE_1
            elif os.path.exists(self.DEFAULT_FILE_2):
                self.file = self.DEFAULT_FILE_2
            else:
                raise FileNotFoundError(
                    f"{self.DEFAULT_FILE_1} or {self.DEFAULT_FILE_2} are not found."
                )
        else:
            self.file = file
            if not os.path.exists(file):
                raise FileNotFoundError(f"{self.file} is not found.")
        # read config file
        with open(self.file, 'r') as f:
            self.configs = f.read()
        self.configs = self.configs.split('\n')

    def remove(self, expected):
        for config in self.configs:
            if expected in config:
                self.configs.remove(config)
        return self.write_file()

    def set(self, name, value=None, device="[all]"):
        '''
        device : "[all]", "[pi3]", "[pi4]" or other
        '''
        have_excepted = False
        for i in range(len(self.configs)):
            config = self.configs[i]
            if name in config:
                have_excepted = True
                tmp = name
                if value != None:
                    tmp += '=' + value
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
            config = '\n'.join(self.configs)
            with open(self.file, 'w') as f:
                f.write(config)
            return 0, config
        except Exception as e:
            return -1, e


# main
# =================================================================
def install():
    print(f"SPC-Core {__version__} install process starts for {user_name}:\n")

    # ================
    if not args.no_dep:
        print("Install dependencies")
        do(msg="update", cmd='apt-get update')
        do(msg="install dependencies",
            cmd='apt-get install -y ' + ' '.join(DEPENDENCIES))
        do(msg="install python requirements",
            cmd='pip3 install -r requirements.txt')

    # ================
    print("Config gpio")
    # enable i2c
    _status, _ = run_command("raspi-config nonint")
    if _status == 0:
        do(msg="enable i2c ", cmd='raspi-config nonint do_i2c 0')
    set_config(msg="enable i2c in config", name="dtparam=i2c_arm", value="on")
    # dtoverlay=gpio-poweroff,gpio_pin=26,active_low=0
    set_config(msg="config gpio-poweroff GPIO26",
               name="dtoverlay=gpio-poweroff,gpio_pin",
               value="26,active_low=0")
    # dtoverlay=gpio-ir,gpio_pin=13
    set_config(msg="config gpio-ir GPIO13 ",
               name="dtoverlay=gpio-ir,gpio_pin",
               value="13")

    # ================
    print('Install spc library')
    do(msg="run setup file", cmd='python3 setup.py install')
    do(msg="cleanup", cmd='rm -rf spc.egg-info')

    # ================
    print('Install spc auto control program')
    working_dir = "/opt/spc"
    auto_script_file = "spc_auto"
    mqtt_client_file = "spc_mqtt_client"
    dashboard_script_file = "spc_dashboard"
    spc_server_file = "spc_server"
    service_config_file = "spc.service"
    config_file = "config"

    do(msg=f"check dir {working_dir}",
        cmd=f'mkdir -p {working_dir}' +
        f' && chmod -R 775 {working_dir}' +
        f' && chown -R {user_name}:{user_name} {working_dir}')
    do(msg=f"copy {spc_server_file} file",
        cmd=f'cp ./bin/{spc_server_file} {working_dir}/{spc_server_file}')
    do(msg=f"copy {auto_script_file} file",
        cmd=f'cp ./bin/{auto_script_file} {working_dir}/{auto_script_file}')
    do(msg=f"copy {mqtt_client_file} file",
        cmd=f'cp ./bin/{mqtt_client_file} {working_dir}/{mqtt_client_file}')
    do(msg=f"copy {dashboard_script_file} file",
        cmd=f'cp ./bin/{dashboard_script_file} {working_dir}/{dashboard_script_file}')
    do(msg=f"copy {dashboard_script_file} file",
        cmd=f'cp ./bin/{dashboard_script_file} {working_dir}/{dashboard_script_file}')
    do(msg=f'copy {service_config_file} file',
        cmd=f'cp ./bin/{service_config_file} /usr/lib/systemd/system/{service_config_file}')
    do(msg="add excutable mode for service file",
        cmd=f'chmod +x /usr/lib/systemd/system/{service_config_file}')
    do(msg=f'copy config file',
        cmd=f'cp ./{config_file} {working_dir}/{config_file}')
    if not args.disable_autostart:
        do(msg='enable the service to auto-start at boot',
           cmd='systemctl daemon-reload' +
           f' && systemctl enable {service_config_file}')
        do(msg=f'run the {service_config_file}',
           cmd=f'systemctl restart {service_config_file}')

    # ================
    print('Download spc dashboard')
    # cleanup www if exist
    if os.path.exists(f'{working_dir}/www'):
        do(msg=f"remove old spc dashboard",
            cmd=f'rm -rf {working_dir}/www')
    do(msg=f"download spc dashboard",
        cmd=f'wget -O /tmp/spc-dashboard.zip {SPC_DASHBOARD_DOWNLOAD_LINK}')
    do(msg=f"unzip spc dashboard",
        cmd=f'unzip /tmp/spc-dashboard.zip -d /tmp/spc-dashboard')
    do(msg=f"copy spc dashboard",
        cmd=f'cp -r /tmp/spc-dashboard/* {working_dir}/www')
    do(msg=f"remove tmp files",
        cmd=f'rm -rf /tmp/spc-dashboard*')

    # check errors
    # ================
    if len(errors) == 0:
        print("Finished")
        # if "--skip-reboot" not in options:
        #     print(
        #         "\033[1;32mWhether to restart for the changes to take effect(Y/N):\033[0m"
        #     )
        #     while True:
        #         key = input()
        #         if key == 'Y' or key == 'y':
        #             print(f'reboot')
        #             run_command('reboot')
        #         elif key == 'N' or key == 'n':
        #             print(f'exit')
        #             sys.exit(0)
        #         else:
        #             continue
    else:
        print("\n\nError happened in install process:")
        for error in errors:
            print(error)
        print(
            "Try to fix it yourself, or contact service@sunfounder.com with this message"
        )


if __name__ == "__main__":
    try:
        install()
    except KeyboardInterrupt:
        print("\n\nCanceled.")
    finally:
        sys.stdout.write(' \033[1D')
        sys.stdout.write('\033[?25h')  # cursor visible
        sys.stdout.flush()
