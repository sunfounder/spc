#!/usr/bin/env python3
from spc import SPC
import time

spc = UpsCase()

error_count = 0
DATA_ALIGN_POSITION = 25

while True:
    print('----------------------------------------------')
    data_buffer = spc.read_all()
    # print(data_buffer)
    for key, value in data_buffer.items():
        key_len = len(key)
        print(
            f"{key}{' '*(DATA_ALIGN_POSITION-key_len)} {value[0]}  {value[1]}")
        if value[0] > 60000:
            error_count += 1
    print(f'\033[1;31mdata error count: {error_count} \033[0m')

    time.sleep(0.5)
