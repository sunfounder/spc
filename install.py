#!/usr/bin/env python3

import sys
from spc.version import __version__
from spc.configtxt import ConfigTxt
import os
import time
import threading
import argparse


DEPENDENCIES = [
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
need_reboot = False

user_name = os.getlogin()

#
# =================================================================


def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(cmd,
                         shell=True,
                         executable="/bin/bash",
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True)
    p.wait()
    result = p.stdout.read()
    error = p.stderr.read()
    status = p.poll()
    return status, result, error

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
    status, result, error = run_command(cmd)
    # at_work_tip stop
    at_work_tip_sw = False
    while _thread.is_alive():
        time.sleep(0.01)
    # status
    if status == 0:
        print('Done')
    else:
        print('\033[1;35mError\033[0m')
        errors.append(f"{msg} error:\n  Command: {cmd}\n  Status: {status}\n  Result: {result}\n  Error: {error}")


config = ConfigTxt()

def set_config(msg="", name="", value=""):
    global need_reboot
    print(" - %s... " % (msg), end='', flush=True)
    try:
        code, _ = config.set(name, value)
        if code == 0:
            need_reboot = True
            print('Done')
        else:
            print('Already')
    except Exception as e:
        print('\033[1;35mError\033[0m')
        errors.append("%s error:\n Error:%s" % (msg, e))


# main
# =================================================================
def install():
    print(f"SPC-Core {__version__} install process starts for {user_name}:\n")

    working_dir = "/opt/spc"
    spc_server_file = "spc_server"
    service_config_file = "spc.service"
    config_file = "config"


    # ================
    if not args.no_dep:
        print("Install dependencies")
        do(msg="update", cmd='apt-get update')
        do(msg="install dependencies",
            cmd='apt-get install -y ' + ' '.join(DEPENDENCIES))
    
    # ================
    print("Config gpio")
    set_config(msg="enable spi in config", name="dtparam=spi", value="on")
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
    do(msg="create virtual environment",
        cmd=f'python3 -m venv {working_dir}/venv')
    do(msg="update pip install build",
        cmd=f'source {working_dir}/venv/bin/activate && pip3 install --upgrade pip build')
    do(msg="build spc", cmd='python3 -m build')
    do(msg="install spc", cmd=f'source {working_dir}/venv/bin/activate && pip3 install ./dist/spc-{__version__}-py3-none-any.whl')
    do(msg="clean spc", cmd='rm -rf ./dist ./build ./spc.egg-info')

    # ================
    print('Install spc auto control program')
    do(msg=f"check dir {working_dir}",
        cmd=f'mkdir -p {working_dir}' +
        f' && chmod -R 775 {working_dir}' +
        f' && chown -R {user_name}:{user_name} {working_dir}')
    do(msg=f"copy {spc_server_file} file",
        cmd=f'cp ./bin/{spc_server_file} {working_dir}/{spc_server_file}')
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

    print('Copy fonts')
    if os.path.exists(f'{working_dir}/fonts'):
        do(msg=f"remove old fonts",
            cmd=f'rm -rf {working_dir}/fonts')
    do(msg=f"copy fonts",
        cmd=f'cp -r ./fonts {working_dir}/fonts')

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


    # ================
    print('change working_dir permissions')
    do(msg=f"chown -R {user_name}:{user_name} {working_dir}",
        cmd=f'chown -R {user_name}:{user_name} {working_dir}')


if __name__ == "__main__":
    try:
        install()
    except KeyboardInterrupt:
        print("\n\nCanceled.")
    finally:
        # check errors
        # ================
        if len(errors) == 0:
            print("Finished")
            if not args.skip_reboot and need_reboot:
                print(
                    "\033[1;32mWhether to restart for the changes to take effect(Y/N):\033[0m"
                )
                while True:
                    key = input()
                    if key == 'Y' or key == 'y':
                        print(f'reboot')
                        run_command('reboot')
                    elif key == 'N' or key == 'n':
                        print(f'exit')
                        sys.exit(0)
                    else:
                        continue
        else:
            print("\n\nError happened in install process:")
            for error in errors:
                print(error)
            print(
                "Try to fix it yourself, or contact service@sunfounder.com with this message"
            )

        sys.stdout.write(' \033[1D')
        sys.stdout.write('\033[?25h')  # cursor visible
        sys.stdout.flush()
