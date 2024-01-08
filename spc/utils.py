import sys

def run_command(cmd):
    import subprocess
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.read().decode()
    status = p.poll()
    return status, result
