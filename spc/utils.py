import time
import sys
LOG_FILE = '/opt/spc/log'
SCRIPT_NAME = 'CORE'

def log(msg: str = None, level='DEBUG', end='\n', flush=False, timestampEnable=True):
    with open(f'{LOG_FILE}', 'a+') as log_file:
        if timestampEnable == True:
            timestamp = time.strftime("%y/%m/%d %H:%M:%S", time.localtime())
            ct = time.time()
            microsecond = '%03d' % ((ct - int(ct)) * 1000)
            msg = f'{timestamp}.{microsecond} [{SCRIPT_NAME}][{level}] {msg}'
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
