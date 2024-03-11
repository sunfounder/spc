from spc.spc import SPC
from spc.utils import run_command
from spc.logger import Logger

log = Logger("RTC")
spc = SPC(log=log)

def main():
    rtc = spc.read_rtc()

    # print(f"\033[3A", end='')  # moves cursor up 3 lines
    # print(f"\033[K RTC: {rtc}", end="\n", flush=True)
    year = rtc[0] + 2000
    month = rtc[1]
    day = rtc[2]
    hour = rtc[3]
    min = rtc[4]
    sec = rtc[5]
    ssec = rtc[6]

    time_str = f"{year}-{month:02d}-{day:02d} {hour:02d}:{min:02d}:{sec:02d}"
    log(f'set time form rtc: {time_str}')
    run_command('date --s=\"{time_str}\"')
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(e)