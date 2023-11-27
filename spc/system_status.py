import os
import subprocess
import shutil
from .utils import Logger
from .ha_api import HA_API
import time

log = Logger('SYSTEM_STATUS')
ha = HA_API()

def get_cpu_temperature():
    cmd = 'cat /sys/class/thermal/thermal_zone0/temp'
    try:
        temp = int(subprocess.check_output(cmd,shell=True).decode())
        return round(temp/1000, 2)
    except Exception as e:
        log(f'get_cpu_temperature error: {e}', level='ERROR')
        return 0.0

# Return RAM information (unit=kb) in a list
# Index 0: total RAM
# Index 1: used RAM
# Index 2: free RAM
def get_ram_info():
    cmd = "free |awk 'NR==2 {print $2,$3,$4}'"
    ram = subprocess.check_output(cmd, shell=True).decode()
    return(ram.split())

# # Return % of CPU used as a character string
'''
Deprecated, high CPU usage when running top -bn1 in bookworm.
'''
# def get_cpu_usage():
#     cmd = "top -bn1 |awk 'NR==3 {print $8}'"
#     try:
#         CPU_usage = subprocess.check_output(cmd,shell=True).decode().replace(',', '.')
#         CPU_usage = round(100 - float(CPU_usage),1)
#     # except Exception as e:
#     #     log(f'get_cpu_usage error: {e}', level='ERROR')
#     #     return 0.0
#     except:
#         CPU_usage = 0.0
#     return CPU_usage

# Return CPU usage percentage as a float
def get_cpu_usage():
    '''
    cmd = 'cat /proc/stat |grep -w cpu'
    # user	nice	system	idle	iowait	irq	softirq 0 0 0
    cpu_total= user + nice + system + idle + iowait + irq + softirq
    cpu_total = cpu_total_2 - cpu_total_1
    user = user_2 - user_1
    nice = nice_2 - nice_1
    idle = idle_2 - idle_1
    ...

    # cpu usage = (1 - idle / cpu_total) * 100%
    # cpu usage = (user + nice + system)/ cpu_total * 100%
    '''
    cmd = 'cat /proc/stat |grep -w cpu'
    cpu_total = 0
    user = 0
    nice = 0
    system = 0

    try:
        for _ in range(2):
            cpu_info = []
            cpu_info = list(subprocess.check_output(cmd,shell=True).decode().split())
            cpu_info = [int(cpu_info[i]) for i in range(1, 8)]
            # print(cpu_info)
            cpu_total = sum(cpu_info) - cpu_total
            user = cpu_info[0] - user
            nice = cpu_info[1] - nice
            system = cpu_info[2] - system
            # print(cpu_total, user, nice, system)
            time.sleep(.1)

        cpu_usage = (user + nice + system)/ cpu_total * 100
        # print(cpu_usage)

    except Exception as e:
        print(f'get_cpu_usage error: {e}', level='ERROR')
        cpu_usage = 0.0

    return cpu_usage

# Return information about disk space as a list (unit included)
# Index 0: total disk space
# Index 1: used disk space
# Index 2: remaining disk space
# Index 3: percentage of disk used
# def getDiskSpace():
#     cmd ="df -h |grep /dev/root"
#     disk = subprocess.check_output(cmd ,shell=True).decode().replace(',', '.')
#     disk = disk.replace("G", "").replace("%", "").split()
#     return(disk[1:5])
def get_disk_space():
    total, used, free = shutil.disk_usage("/")
    total = round(total / (2**30), 2)
    used = round(used / (2**30), 2)
    free = round(free / (2**30), 2)
    perc = int(used/ total * 100)
    return(total, used, free, perc)

def _get_ip_address():
    IPs = {}
    NIC_devices = []
    NIC_devices = os.listdir('/sys/class/net/')
    # print(NIC_devices)

    for NIC in NIC_devices:
        if NIC == 'lo':
            continue
        try:
            IPs[NIC] = subprocess.check_output('ifconfig ' + NIC + ' | grep "inet " | awk \'{print $2}\'', shell=True).decode().strip('\n')
        except:
            continue
        # print(NIC, IPs[NIC])

    return IPs

# IP address
def get_ip_address():
    ip = None
    if ha.is_homeassistant_addon():
        IPs = ha.get_ip()
        if len(IPs) == 0:
            IPs = _get_ip_address()
    else:
        IPs = _get_ip_address()
    if 'wlan0' in IPs and IPs['wlan0'] != None and IPs['wlan0'] != '':
        ip = IPs['wlan0']
    elif 'eth0' in IPs and IPs['eth0'] != None and IPs['eth0'] != '':
        ip = IPs['eth0']
    else:
        ip = 'DISCONNECT'

    return ip

def get_mac_address():
    MACs = {}
    NIC_devices = []
    NIC_devices = os.listdir('/sys/class/net/')
    # print(NIC_devices)
    for NIC in NIC_devices:
        if NIC == 'lo':
            continue
        try:
            with open('/sys/class/net/' + NIC + '/address', 'r') as f:
                MACs[NIC] = f.readline().strip()
        except:
            continue
        # print(NIC, MACs[NIC])

    return MACs

