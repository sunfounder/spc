import time
import sys

class Logger(object):
    def __init__(self, script_name="CORE", log_file="/opt/spc/log"):
        self.script_name = script_name
        self.log_file = log_file

    def __call__(self, msg: str = None, level='DEBUG', end='\n', flush=False, timestampEnable=True):
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
