#!/usr/bin/env python3
import os
import time

from argparse import ArgumentParser
from spc.spc import SPC
from spc.config import Config
from spc.oled import OLED, Rect

from spc.logger import Logger
import threading
from spc.system_status import get_cpu_usage, get_ram_info, get_disk_space, get_ip_address
from spc.ha_api import HA_API
from spc.ws2812 import WS2812, RGB_styles
from spc.configtxt import ConfigTxt
from spc.database import Database


log = Logger("AUTO")
db = Database(log=log)
config = Config(log=log)
spc = SPC(log=log)
ha = HA_API(log=log)

# Argument Parser
# =================================================================
parser = ArgumentParser()
parser.add_argument("command", choices=["start", "restart"], nargs="?", help="Command")
parser.add_argument("-r", "--reflash-interval", type=float, default=config.get("auto",
                    "reflash_interval"), help="Data update Interval")
parser.add_argument("-R", "--retry-interval", type=int, default=config.get(
    "auto", "retry_interval"), help="Retry interval after error")
parser.add_argument("-m", "--fan-mode", choices=["auto", "quiet", "normal",
                    "performance"], default=config.get("auto", "fan_mode"), help="Fan mode")
parser.add_argument("-t", "--temperature-unit", choices=[
                    "C", "F"], default=config.get("auto", "temperature_unit"), help="Temperature unit")
parser.add_argument("-w", "--rgb-switch", type=bool,
                    default=config.get("auto", "rgb_switch"), help="RGB switch")
parser.add_argument("-y", "--rgb-style", choices=["breath", "leap", "flow", "raise_up",
                    "colorful"], default=config.get("auto", "rgb_style"), help="RGB style")
parser.add_argument("-c", "--rgb-color",
                    default=config.get("auto", "rgb_color"), help="RGB color")
parser.add_argument("-p", "--rgb-speed",
                    default=config.get("auto", "rgb_speed"), help="RGB speed")
parser.add_argument("-f", "--rgb-pwm-frequency", type=int,
                    default=config.get("auto", "rgb_pwm_frequency"), help="RGB PWM frequency")
parser.add_argument("-i", "--rgb-pin", type=int,
                    choices=[10, 12, 21], default=config.get("auto", "rgb_pin"), help="RGB pin")

args = parser.parse_args()

has_change = False
need_reboot = False

def handle_param_change():
    global has_change, need_reboot
    for param in args.__dict__:
        new_value = args.__dict__[param]
        if new_value == config.get("auto", param):
            continue
        has_change = True
        config.set("auto", param, new_value)
        if param == "rgb_pin":
            log(f"change rgb pin to {new_value}", level="INFO")
            config_txt = ConfigTxt(log=log)
            if not config_txt.isready():
                continue
            if new_value == 10:
                config_txt.set("dtparam=audio", "on")
                config_txt.set("dtoverlay=spi", "on")
                config_txt.set("core_freq", "500")
                config_txt.set("core_freq_min", "500")
            elif new_value == 12:
                config_txt.set("dtparam=audio", "off")
            elif new_value == 21:
                config_txt.set("dtparam=audio", "on")
                config_txt.comment("dtoverlay=hifiberry-dac")
                config_txt.comment("dtoverlay=i2s-mmap")
            need_reboot = True

data = None

# fan auto control
# =================================================================
AUTO_FAN_LEVELS = [
    {
        "name": "OFF",
        "low": 0,
        "high": 55,
        "percent": 0,
    }, {
        "name": "LOW",
        "low": 45,
        "high": 65,
        "percent": 40,
    }, {
        "name": "MEDIUM",
        "low": 55,
        "high": 75,
        "percent": 80,
    }, {
        "name": "HIGH",
        "low": 65,
        "high": 100,
        "percent": 100,
    },
]

fan_state = config.get("auto", "fan_state")
fan_speed = config.get("auto", "fan_speed")
last_fan_state = None
last_fan_speed = None
auto_fan_level = 0
auto_fan_initial = True

def fan_auto_control(data):
    global fan_speed, last_fan_speed, auto_fan_level, auto_fan_initial
    # Check if device supports fan
    if "fan" not in spc.device.peripherals:
        return

    # read fan_state from config file
    # fan_state = config.get("auto", "fan_state")
    fan_state = db.get("config", "auto_fan_state")
    # if the fan is off
    if fan_state is False:
        if last_fan_speed is None or last_fan_speed != fan_speed:
            last_fan_speed = fan_speed
            spc.set_fan_speed(0)
        else:
            return

    # if the fan is on, and fan_mode is auto, adjust fan speed based on  CPU temperature
    # read fan_mode from config file
    # _fan_mode = config.get('auto', 'fan_mode')
    fan_mode = db.get("config", "auto_fan_mode")
    # if fan_mode is not auto
    if fan_mode != 'auto':
        if fan_mode == 'quiet':
            fan_speed = 40
        elif fan_mode == 'normal':
            fan_speed = 70
        elif fan_mode == 'performance':
            fan_speed = 100
        #
        if last_fan_speed != fan_speed:
            last_fan_speed = fan_speed
            spc.set_fan_speed(fan_speed)
        else:
            return

    # --- fan auto control ---
    cpu_temp = data["cpu_temperature"]
    changed = False
    direction = ""
    if cpu_temp < AUTO_FAN_LEVELS[auto_fan_level]["low"]:
        auto_fan_level -= 1
        changed = True
        direction = "low"
    elif cpu_temp > AUTO_FAN_LEVELS[auto_fan_level]["high"]:
        auto_fan_level += 1
        changed = True
        direction = "high"
    #
    if changed or auto_fan_initial:
        auto_fan_level = max(0, min(auto_fan_level, len(AUTO_FAN_LEVELS) - 1))
        speed = AUTO_FAN_LEVELS[auto_fan_level]["percent"]
        spc.set_fan_speed(speed)

        if auto_fan_initial:
            log(f"cpu temperature: {cpu_temp} \"C", level="INFO")
        else:
            log(
                f"cpu temperature: {cpu_temp} \"C, {direction}er than {AUTO_FAN_LEVELS[auto_fan_level][direction]}", level="INFO")
  
        log(f"set fan level: {AUTO_FAN_LEVELS[auto_fan_level]['name']}", level="INFO")
        log(f"set fan speed: {speed}", level="INFO")
    
        auto_fan_initial = False


# oled
# =================================================================
# --- oled init ---
has_oled = False
if 'oled' in spc.device.peripherals:
    try:
        oled = OLED(log=log) # if init failed, oled == None
        if oled is not None:
            log('oled init success')
    except Exception as e:
        log(f"oled init failed: {e}")

# --- oled control ---
oled_timer_start = 0
ip = "DISCONNECT"

ip_detect_interval = 2000 # ms
ip_detect_start_time = 0

def draw_oled(data):
    global ip, ip_detect_start_time

    # Check if device supports OLED
    if "oled" not in spc.device.peripherals:
        return
    # Check if OLED is ready
    if not oled.is_ready():
        return

    # ---- get system status data ---- 
    # cpu usage
    cpu_usage = get_cpu_usage()
    # cpu temperature
    cpu_temperature = data["cpu_temperature"]
    # RAM
    ram_stats = get_ram_info()
    ram_total = round(int(ram_stats[0]) / 1024/1024, 1)
    ram_used = round(int(ram_stats[1]) / 1024/1024, 1)
    ram_usage = round(ram_used/ram_total*100, 1)
    # Disk information
    disk_stats = get_disk_space()
    disk_total = str(disk_stats[0])
    disk_used = str(disk_stats[1])
    disk_percent = float(disk_stats[3])
   
    disk_unit = 'G1'
    if DISK_total >= 1000:
        disk_unit = 'T'
        DISK_total = round(DISK_total/1000, 3)
        DISK_used = round(DISK_used/1000, 3)
    elif DISK_total >= 100:
        disk_unit = 'G2'

    # get ip
    if ip == "DISCONNECT" \
        or (time.time() - ip_detect_start_time > ip_detect_interval):
        ip = get_ip_address()
        ip_detect_start_time = time.time()

    # ---- display info ----
    oled.clear()
    cpu_info_rect = Rect(0, 29, 34, 8)
    temp_info_rect = Rect(0, 38, 34, 8)
    ip_rect = Rect(46, 0, 87, 10)
    ram_info_rect = Rect(45, 17, 87, 10)
    ram_rect = Rect(45, 29, 87, 10)
    rom_info_rect = Rect(45, 41, 87, 10)
    rom_rect = Rect(45, 53, 87, 10)
    # draw CPU usage
    oled.draw_text("CPU", 6, 0)
    oled.draw.pieslice((0, 12, 30, 42), start=180, end=0, fill=0, outline=1)
    oled.draw.pieslice((0, 12, 30, 42), start=180, end=int(180+180*cpu_usage*0.01), fill=1, outline=1)
    oled.draw.rectangle(cpu_info_rect.rect(), outline=0, fill=0)
    oled.draw_text('{:^5.1f} %'.format(cpu_usage), 2, 27)
    # Temp
    oled.draw.rectangle(temp_info_rect.rect(), outline=0, fill=0)
    if args.temperature_unit == 'C':
        oled.draw_text('{:>4.1f} \'C'.format(cpu_temperature), 2, 38)
        oled.draw.pieslice((0, 33, 30, 63), start=0, end=180, fill=0, outline=1)
        oled.draw.pieslice((0, 33, 30, 63), start=int(180-180*cpu_temperature * 0.01), end=180, fill=1, outline=1)
    elif args.temperature_unit == 'F':
        cpu_temperature = cpu_temperature * 1.8 + 32
        oled.draw_text('{:>4.1f}'.format(cpu_temperature), 2, 38)
        oled.draw_text('\'F'.format(cpu_temperature), 26, 38)
        oled.draw.pieslice((0, 33, 30, 63), start=0, end=180, fill=0, outline=1)
        pcent = (cpu_temperature-32)/1.8
        oled.draw.pieslice((0, 33, 30, 63), start=int(180-180*pcent*0.01), end=180, fill=1, outline=1)
    # RAM
    oled.draw_text(f'RAM:  {ram_used:^4.1f}/{ram_total:^4.1f} G',*ram_info_rect.coord())
    oled.draw.rectangle(ram_rect.rect(), outline=1, fill=0)
    oled.draw.rectangle(ram_rect.rect(ram_usage), outline=1, fill=1)
    # Disk
    if disk_unit == 'G1':
        _dec = 1
        if disk_used < 10:
            _dec = 2              
        oled.draw_text(f'DISK: {disk_used:>2.{_dec}f}/{disk_total:<2.1f} G', *rom_info_rect.coord())
    elif disk_unit == 'G2':
        _dec = 0
        if disk_used < 100:
            _dec = 1
        oled.draw_text(f'DISK: {disk_used:>3.{_dec}f}/{disk_total:<3.0f} G', *rom_info_rect.coord())
    elif disk_unit == 'T':
        oled.draw_text(f'DISK: {disk_used:>2.2f}/{disk_total:<2.2f} T', *rom_info_rect.coord())

    oled.draw.rectangle(rom_rect.rect(), outline=1, fill=0)
    oled.draw.rectangle(rom_rect.rect(disk_percent), outline=1, fill=1)
    # IP
    oled.draw.rectangle((ip_rect.x-13, ip_rect.y, ip_rect.x +
                         ip_rect.width, ip_rect.height), outline=1, fill=1)
    oled.draw.pieslice((ip_rect.x-25, ip_rect.y, ip_rect.x-3,
                        ip_rect.height+10), start=270, end=0, fill=0, outline=0)
    oled.draw_text(ip, *ip_rect.coord(), 0)
    # draw the image buffer.
    oled.display()

# rgb
# =================================================================
# --- check and init rgb ---
rgb = None
if 'ws2812' in spc.device.peripherals:
    try:
        rgb = WS2812(LED_COUNT=16, LED_PIN=args.rgb_pin,
            LED_FREQ_HZ=args.rgb_pwm_frequency*1000, log=log)
        log('ws2812 init success')
    except Exception as e:
        log(f"ws2812 init failed: {e}")

# --- rgb --- control
rgb_swtich = False
rgb_style = None
rgb_color = None
rgb_speed = 0
rgb_has_change = False
rgb_retry_flag = False
# rgb_thread_lock = threading.Lock()

def rgb_thread_loop():
    while True:
        try:
            if rgb_swtich == False:
                rgb.clear()
                while not rgb_swtich:
                    time.sleep(.1)
            else:
                rgb.clear()
                # display will loop until rgb.stop singal
                rgb.display(rgb_style, rgb_color, rgb_speed)

            rgb_retry_flag = False
        except Exception as e:
            if rgb_retry_flag == False:
                rgb_retry_flag = True
                log(f"rgb error: {e}")
            # --- retrying ---
            time.sleep(1)
            continue


def rgb_control(data):
    global rgb_swtich, rgb_style, rgb_color, rgb_speed, rgb_has_change
    if 'ws2812' not in spc.device.peripherals:
        return
    if args.rgb_switch != True:
        return
    if rgb is None:
        return

    # read rgb config from file
    # _rgb_switch = config.get("auto", "rgb_switch", default=False)
    # _rgb_style = config.get("auto", "rgb_style")
    # _rgb_color = config.get("auto", "rgb_color")
    # _rgb_speed = config.get("auto", "rgb_speed")
    _rgb_switch = db.get("config", "auto_rgb_switch", default=False)
    _rgb_style = db.get("config", "auto_rgb_style")
    _rgb_color = db.get("config", "auto_rgb_color")
    _rgb_speed = db.get("config", "auto_rgb_speed")
    # if change
    if (_rgb_switch != rgb_swtich or \
        _rgb_style != rgb_style or \
        _rgb_color != rgb_color or \
        _rgb_speed != rgb_speed 
        ):
        rgb_swtich = _rgb_switch
        rgb_style = _rgb_style
        rgb_color = _rgb_color
        rgb_speed = _rgb_speed
        # rgb_has_change = True
        rgb.stop_loop()
    else:
        has_change = False

def rgb_work():
    if args.rgb_switch != True:
        return
    log('rgb_control')
    try:
        if args.rgb_style in RGB_styles:
            log('rgb_show: %s' % args.rgb_style)
            rgb.display(args.rgb_style, args.rgb_color, args.rgb_speed, 255)
        else:
            log('rgb_style not in RGB_styles')
    except Exception as e:
        log(e, level='rgb_strip')

# shutdown_singal_control
# =================================================================
last_shutdown_request = 0

def shutdown_singal_control(data):
    global last_shutdown_request
    # --- read shutdown request ---
    shutdown_request = int(data["shutdown_request"])
    # print(shutdown_request)
    if last_shutdown_request != shutdown_request:
        last_shutdown_request = shutdown_request
        if last_shutdown_request != 255:
            log(f"shutdown_request code: {shutdown_request}", level="INFO")
    if shutdown_request == 1:
        log("Low power shutdown.", level="INFO")
    elif shutdown_request == 2:
        log("Manual button shutdown.", level="INFO")

    if shutdown_request in [1, 2]:
        # TODO: Handler before ending
        if ha.is_homeassistant_addon():
            log("Request HA shutdown.", level="INFO")
            ha.shutdown()
            time.sleep(1)
        else:
            os.system("sudo poweroff")
            time.sleep(1)

# external_unplugged_handler
# =================================================================
is_plugged_in = False # True, pulgged in; False, unpulgged in

def external_unplugged_handler(data):
    global is_plugged_in

    if 'external_input' not in spc.device.peripherals:
        return

    if data['is_plugged_in'] != is_plugged_in:
        is_plugged_in = data['is_plugged_in']
        if is_plugged_in == True:
            log(f"External input plug in", level="INFO")
        else:
            log(f"External input unplugged", level="INFO")
    if is_plugged_in == False:
        shutdown_pct = db.get("config", "auto_shutdown_battery_pct")
        # shutdown_pct = spc.read_shutdown_battery_pct()
        current_pct= data['battery_percentage']
        if current_pct < shutdown_pct:
            log(f"Battery is below {shutdown_pct}, shutdown!", level="INFO")
            # TODO: Handler before ending
            os.system("sudo poweroff")
            time.sleep(1)

# main
# =================================================================
def main():
    # --- param handler ---
    handle_param_change()
    if need_reboot == True:
        print("\033[1;32mWhether to restart for the changes to take effect(Y/N):\033[0m")
        while True:
            key = input()
            if key == 'Y' or key == 'y':
                print(f'reboot')
                os.system('reboot')
            elif key == 'N' or key == 'n':
                print(f'exit')
                return
            else:
                continue

    # --- auto control loop ---
    if args.command != 'start':
        return

    log(f'SPC auto started', level='INFO')
    log(f'Device: {spc.device.name}', level='DEBUG')
    log(f'Device Peripherals: {spc.device.peripherals}', level='DEBUG')
    retry_flag = False

    if "ws2812" in spc.device.peripherals\
        and args.rgb_switch == True\
        and rgb is not None:
        rgb_thread = threading.Thread(target=rgb_thread_loop)
        rgb_thread.daemon = True
        rgb_thread.start()

    while True:
        try:
            data = spc.read_all()
            shutdown_singal_control(data)
            external_unplugged_handler(data)
            fan_auto_control(data)
            draw_oled(data)
            rgb_control(data)
            time.sleep(float(args.reflash_interval))
            retry_flag = False
        except Exception as e:
            if retry_flag == False: # print error once
                retry_flag = True
                log(e, level='ERROR')
                log(f'retrying ...', level='DEBUG')
            # retrying
            time.sleep(args.retry_interval)
            continue


if __name__ == "__main__":
    main()

