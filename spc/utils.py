import sys

class Logger(object):
    def __init__(self, script_name="CORE", log_file="/opt/spc/log"):
        self.script_name = script_name
        self.log_file = log_file

    def __call__(self, msg: str = None, level='DEBUG', end='\n', flush=False, timestampEnable=True):
        import time
        with open(f'{self.log_file}', 'a+') as log_file:
            if timestampEnable == True:
                timestamp = time.strftime("%y/%m/%d %H:%M:%S", time.localtime())
                ct = time.time()
                microsecond = '%03d' % ((ct - int(ct)) * 1000)
                msg = f'{timestamp}.{microsecond} [{self.script_name}][{level}] {msg}'
            print(msg, end=end, flush=flush, file=log_file)
            print(msg, end=end, flush=flush, file=sys.stdout)

def run_command(cmd):
    import subprocess
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.read().decode()
    status = p.poll()
    return status, result

net_io_counter = None
net_io_counter_time = None

def get_network_connection_type():
    from psutil import net_if_stats
    interfaces = net_if_stats()
    connection_type = []
    
    for interface, stats in interfaces.items():
        if stats.isup:
            if "eth" in interface or "enp" in interface or "ens" in interface:
                connection_type.append("Wired")
            if "wlan" in interface or "wlp" in interface or "wls" in interface:
                connection_type.append("Wireless")
    
    return connection_type

def get_network_speed():
    from psutil import net_io_counters
    from time import time
    global net_io_counter, net_io_counter_time
    network_speed = {}
    # 获取初始网络计数器信息
    current_net_io_counter = net_io_counters()
    current_net_io_counter_time = time()

    if net_io_counter is None:
        net_io_counter = current_net_io_counter
        net_io_counter_time = current_net_io_counter_time
        network_speed['upload_speed'] = 0
        network_speed['download_speed'] = 0
        return network_speed

    # 计算速度差异
    bytes_sent = current_net_io_counter.bytes_sent - net_io_counter.bytes_sent
    bytes_recv = current_net_io_counter.bytes_recv - net_io_counter.bytes_recv
    interval = current_net_io_counter_time - net_io_counter_time

    # 计算速度（每秒字节数）
    upload_speed = bytes_sent / interval
    download_speed = bytes_recv / interval

    network_speed['upload_speed'] = upload_speed
    network_speed['download_speed'] = download_speed

    net_io_counter = current_net_io_counter
    net_io_counter_time = current_net_io_counter_time

    return network_speed

def get_network_info():
    network_info = {}

    network_info['type'] = get_network_connection_type()
    network_speed = get_network_speed()
    network_info['upload_speed'] = network_speed['upload_speed']
    network_info['download_speed'] = network_speed['download_speed']

    return network_info


def get_memory_info():
    from psutil import virtual_memory
    memory_info = virtual_memory()
    memory = {}
    memory['total'] = memory_info.total
    memory['available'] = memory_info.available
    memory['percent'] = memory_info.percent
    memory['used'] = memory_info.used
    memory['free'] = memory_info.free
    return memory

def get_disks_info():
    from psutil import disk_partitions, disk_usage
    import subprocess
    disks = []
    output = subprocess.check_output(["lsblk", "-o", "NAME,TYPE", "-n", "-l"]).decode().strip().split('\n')
    
    for line in output:
        disk_name, disk_type = line.split()
        if disk_type == "disk":
            disks.append(disk_name)
    
    disk_info = {}
    
    for disk in disks:
        try:
            partitions = disk_partitions(all=True)
            total = 0
            used = 0
            free = 0
            percent = 0
            
            for partition in partitions:
                if partition.device.startswith("/dev/" + disk):
                    usage = disk_usage(partition.mountpoint)
                    total += usage.total
                    used += usage.used
                    free += usage.free
                    percent = max(percent, usage.percent)
            
            disk_info[disk] = {
                'total': total,
                'used': used,
                'free': free,
                'percent': percent
            }
        except Exception as e:
            print(f"Failed to get disk information for {disk}: {str(e)}")
    
    return disk_info

def get_cpu_info():
    from psutil import cpu_percent, cpu_freq, cpu_count, cpu_stats
    cpu_info = {}
    cpu_info['percent'] = cpu_percent(percpu=True)
    cpu_info['freq'] = cpu_freq(percpu=True)
    cpu_info['count'] = cpu_count()
    cpu_info['stats'] = cpu_stats()
    return cpu_info

def get_boot_time():
    from psutil import boot_time
    return boot_time()