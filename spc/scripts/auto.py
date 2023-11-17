#!/usr/bin/env python3

from argparse import ArgumentParser
from spc.spc import SPC
from spc.config import Config
from spc.oled import OLED, Rect
from spc.utils import Logger
import threading
from spc.system_status import get_cpu_usage, get_ram_info, get_disk_space, get_ip_address
from spc.ha_api import HA_API
from spc.ws2812 import WS2812, RGB_styles
from spc.configtxt import ConfigTxt

import time
import os

log = Logger("AUTO")
spc = SPC()
oled = OLED()
ha = HA_API()
config = Config()
parser = ArgumentParser()
parser.add_argument("command", choices=["start"], nargs="?", help="Command")
parser.add_argument("-r", "--reflash-interval", default=config.getint("auto",
                    "reflash_interval"), help="Data update Interval")
parser.add_argument("-R", "--retry-interval", type=int, default=config.getint(
    "auto", "retry_interval"), help="Retry interval after error")
parser.add_argument("-m", "--fan-mode", choices=["auto", "quiet", "normal",
                    "performance"], default=config.get("auto", "fan_mode"), help="Fan mode")
parser.add_argument("-t", "--temperature-unit", choices=[
                    "C", "F"], default=config.get("auto", "temperature_unit"), help="Temperature unit")
parser.add_argument("-w", "--rgb-switch", type=bool,
                    default=config.getboolean("auto", "rgb_switch"), help="RGB switch")
parser.add_argument("-y", "--rgb-style", choices=["breath", "leap", "flow", "raise_up",
                    "colorful"], default=config.get("auto", "rgb_style"), help="RGB style")
parser.add_argument("-c", "--rgb-color",
                    default=config.get("auto", "rgb_color"), help="RGB color")
parser.add_argument("-p", "--rgb-speed",
                    default=config.getint("auto", "rgb_speed"), help="RGB speed")
parser.add_argument("-f", "--rgb-pwm-frequency", type=int,
                    default=config.getint("auto", "rgb_pwm_frequency"), help="RGB PWM frequency")
parser.add_argument("-i", "--rgb-pin", type=int,
                    choices=[10, 12, 21], default=config.getint("auto", "rgb_pin"), help="RGB pin")
args = parser.parse_args()

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

last_shutdown_request = 0
fan_state = config.getboolean("auto", "fan_state")
fan_speed = config.getint("auto", "fan_speed")
last_fan_state = None
last_fan_speed = None
auto_fan_level = 0
auto_fan_initial = True
oled_timer_start = 0
ip = "DISCONNECT"
data = None
rgb = None
need_reboot = False


def handle_param_change():
    global need_reboot
    for param in args.__dict__:
        new_value = args.__dict__[param]
        if str(new_value) == config.get("auto", param):
            continue
        config.set("auto", param, new_value)
        if param == "rgb_pin":
            log(f"change rgb pin to {new_value}", level="INFO")
            config_txt = ConfigTxt()
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


def fan_auto_control(data):
    global auto_fan_level, auto_fan_initial, last_fan_state, last_fan_speed, fan_state, fan_speed

    # Check if device supports fan
    if "fan" not in spc.device.peripherals:
        return

    # Check if fan is on
    if not fan_state:
        if fan_state != last_fan_state:
            last_fan_state = fan_state
            spc.set_fan_state(fan_state)
            log(f"set fan state: {fan_state}", level="INFO")
        return
    # Check if fan is auto
    if not args.fan_mode == "auto":
        if fan_speed != last_fan_speed:
            last_fan_speed = fan_speed
            spc.set_fan_speed(fan_speed)
            log(f"set fan speed: {fan_speed}", level="INFO")
        return

    # --- fan control ---
    cpu_temp = data["cpu_temperature"]
    changed = False
    direction = -1
    new_level = auto_fan_level
    if cpu_temp < AUTO_FAN_LEVELS[auto_fan_level]["low"]:
        new_level -= 1
        changed = True
        direction = "low"
    elif cpu_temp > AUTO_FAN_LEVELS[auto_fan_level]["high"]:
        new_level += 1
        changed = True
        direction = "high"

    if changed or auto_fan_initial:
        new_level = max(0, min(new_level, len(AUTO_FAN_LEVELS) - 1))
        speed = AUTO_FAN_LEVELS[new_level]["percent"]
        spc.set_fan_speed(speed)
        if auto_fan_initial:
            log(f"cpu temperature: {cpu_temp} \"C", level="INFO")
        else:
            log(
                f"cpu temperature: {cpu_temp} \"C, {direction}er than {AUTO_FAN_LEVELS[auto_fan_level][direction]}", level="INFO")
        log(f"set fan level: {AUTO_FAN_LEVELS[new_level]['name']}", level="INFO")
        log(f"set fan speed: {speed}", level="INFO")
        auto_fan_level = new_level
        auto_fan_initial = False


def shutdown_control(data):
    global last_shutdown_request
    # --- shutdown request ---
    shutdown_request = data["shutdown_request"]
    # print(shutdown_request)
    if last_shutdown_request != shutdown_request:
        last_shutdown_request = shutdown_request
        log(f"shutdown_request code: {shutdown_request}", level="INFO")
    if shutdown_request == 1:
        log("Low power shutdown.", level="INFO")
        os.system("sudo poweroff")
        time.sleep(1)
    elif shutdown_request == 2:
        log("Manual button shutdown.", level="INFO")
        os.system("sudo poweroff")
        time.sleep(1)


def draw_oled(data):
    # Check if device supports OLED
    if "oled" not in spc.device.peripherals:
        return
    # Check if OLED is ready
    if not oled.is_ready():
        return
    global ip

    # Currently iled is on for:
    # current_on_for = time.time() - oled_timer_start
    # if oled_on_for > 0 and current_on_for > oled_on_for:
    #     oled.off()
    #     return

    cpu_usage = get_cpu_usage()
    cpu_temperature = data["cpu_temperature"]
    oled.clear()
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

    # display info
    ip_rect = Rect(48, 0, 81, 10)
    cpu_info_rect = Rect(0, 29, 30, 8)
    temp_info_rect = Rect(0, 38, 30, 8)
    ram_info_rect = Rect(46, 17, 81, 10)
    ram_rect = Rect(46, 29, 81, 10)
    rom_info_rect = Rect(46, 41, 81, 10)
    rom_rect = Rect(46, 53, 81, 10)

    # get ip if disconnected
    if ip == "DISCONNECT":
        ip = get_ip_address()

    oled.draw_text("CPU", 6, 0)
    oled.draw.pieslice((0, 12, 30, 42), start=180,
                       end=0, fill=0, outline=1)
    oled.draw.pieslice((0, 12, 30, 42), start=180, end=int(
        180+180*cpu_usage*0.01), fill=1, outline=1)
    # Clear the CPU info area
    oled.draw.rectangle(cpu_info_rect.rect(), outline=0, fill=0)
    oled.draw_text('{:^5.1f} %'.format(cpu_usage), 2, 27)
    # Temp
    # Clear the temperature info area
    oled.draw.rectangle(temp_info_rect.rect(), outline=0, fill=0)
    if args.temperature_unit == 'C':
        oled.draw_text('{:>4.1f} \'C'.format(cpu_temperature), 2, 38)
        oled.draw.pieslice((0, 33, 30, 63), start=0,
                           end=180, fill=0, outline=1)
        oled.draw.pieslice((0, 33, 30, 63), start=int(
            180-180*cpu_temperature * 0.01), end=180, fill=1, outline=1)
    elif args.temperature_unit == 'F':
        cpu_temperature = cpu_temperature * 1.8 + 32
        oled.draw_text('{:>4.1f} \'F'.format(cpu_temperature), 2, 38)
        oled.draw.pieslice((0, 33, 30, 63), start=0,
                           end=180, fill=0, outline=1)
        pcent = (cpu_temperature-32)/1.8
        oled.draw.pieslice((0, 33, 30, 63), start=int(
            180-180*pcent*0.01), end=180, fill=1, outline=1)
    # RAM
    oled.draw_text('RAM: {}/{} GB'.format(ram_used,
                                          ram_total), *ram_info_rect.coord())
    # draw_text('{:>5.1f}'.format(RAM_usage)+' %',92,0)
    oled.draw.rectangle(ram_rect.rect(), outline=1, fill=0)
    oled.draw.rectangle(ram_rect.rect(ram_usage), outline=1, fill=1)
    # Disk
    oled.draw_text('ROM: {}/{} GB'.format(disk_used,
                                          disk_total), *rom_info_rect.coord())
    # draw_text('     ',72,32)
    # draw_text(''+' G',72,32)
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


def rgb_control():
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


# main
# =================================================================
def main():
    retry_flag = False

    handle_param_change()
    if need_reboot == True:
        print(
            "\033[1;32mWhether to restart for the changes to take effect(Y/N):\033[0m"
        )
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
    if args.command == None:
        return
    # Check if device support WS2812
    if 'ws2812' in spc.device.peripherals:
        rgb = WS2812(LED_COUNT=16, LED_PIN=args.rgb_pin,
                     LED_FREQ_HZ=args.rgb_pwm_frequency*1000)

        # rgb_strip thread
        if args.rgb_switch == True:
            rgb_thread = threading.Thread(target=rgb_control)
            rgb_thread.daemon = True
            rgb_thread.start()
        else:
            rgb.clear()

    log(f'SPC auto started', level='INFO')

    while True:
        # try:
        data = spc.read_all()
        shutdown_control(data)
        fan_auto_control(data)
        draw_oled(data)
        time.sleep(args.reflash_interval)
        retry_flag = False
        # except Exception as e:
        #     if retry_flag == False:
        #         retry_flag = True
        #         log(e, level='ERROR')
        #         log(f'retrying ...', level='DEBUG')
        #     # retrying
        #     time.sleep(args.retry_interval)
        #     continue


if __name__ == "__main__":
    # try:
    main()
    # except Exception as e:
    #     print(e)
