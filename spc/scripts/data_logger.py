
from spc.spc import SPC
from spc.database import Database
from spc.logger import Logger
from spc.system_status import get_memory_info, get_disks_info, get_network_info, get_cpu_info, get_boot_time
import argparse
from spc.config import Config
import time

log = Logger('DATA_LOGGER')
spc = SPC()
db = Database()
config = Config()

INTERVAL = config.getint('data-logger', 'interval', default=1)

parser = argparse.ArgumentParser(description='spc-data-logger')
parser.add_argument("--interval", default=INTERVAL, help="Set interval for data logger, in second")

args = parser.parse_args()

def loop():
        data = spc.read_all()
        cpu = get_cpu_info()
        memory = get_memory_info()
        disks = get_disks_info()
        network = get_network_info()
        disks = get_disks_info()
        data['cpu_count'] = cpu['count']
        for i, core in enumerate(cpu["percent"]):
            data[f'cpu_{i}_percent'] = core
        data['cpu_freq'] = cpu['freq'][0].current
        data['cpu_freq_min'] = cpu['freq'][0].min
        data['cpu_freq_max'] = cpu['freq'][0].max
        data['memory_total'] = memory['total']
        data['memory_available'] = memory['available']
        data['memory_percent'] = memory['percent']
        data['memory_used'] = memory['used']
        data['memory_free'] = memory['free']
        for disk_name in disks:
            disk = disks[disk_name]
            if disk['total'] == 0:
                continue
            data[f'disk_{disk_name}_total'] = disk['total']
            data[f'disk_{disk_name}_used'] = disk['used']
            data[f'disk_{disk_name}_free'] = disk['free']
            data[f'disk_{disk_name}_percent'] = disk['percent']
        data['network_type'] = "&".join(network['type'])
        data['network_upload_speed'] = network['upload_speed']
        data['network_download_speed'] = network['download_speed']
        data['boot_time'] = get_boot_time()

        for key in data:
            value = data[key]
            if isinstance(value, bool):
                data[key] = int(value)

        db.set('history', data)
        log(f"Set data: {data}")
        # db.set('test', {"aa":"true"})

        time.sleep(args.interval)

def main():
    while True:
        try:
            loop()
        except Exception as e:
            log(e)
            time.sleep(5)

if __name__ == "__main__":
    main()