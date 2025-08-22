# SPC Data Buffer Sheet

## dataBuffer

| name                   | addr | len | type  | unit | description                                                           |
| :--------------------- | :--: | :-: | :---: | :--: | :-------------------------------------------------------------------- |
| external_input_voltage |  0   |  2  |  u16  |  mV  | -  |
| external_input_current |  2   |  2  |  u16  |  mA  | -  |
| output_voltage         |  4   |  2  |  u16  |  mV  | -  |
| output_current         |  6   |  2  |  u16  |  mA  | -  |
| battery_voltage        |  8   |  2  |  u16  |  mV  | -  |
| battery_current        |  10  |  2  | int16 |  mA  | -  |
| battery_percentage     |  12  |  1  |  u8   |  %   | -  |
| battery_capacity       |  13  |  2  |  u16  | mAh  | -  |
| power_source           |  15  |  1  |  u8   |  -   | 0, battery isn't supplying power; <br> 1, battery is supplying power; |
| is_usb_plugged         |  16  |  1  |  u8   |  -   | 0, usb is unplugged; <br> 1, usb is plugged in;                       |
| is_battery_plugged     |  17  |  1  |  u8   |  -   | 0, battery is unplugged; <br> 1, battery is plugged in;               |
| is_charging            |  18  |  1  |  u8   |  -   | 0, not charging; <br> 1, charging;                                    |
| fan_power              |  19  |  1  |  u8   |  -   | 0 ~ 100|
| shutdown_request       |  20  |  1  |  u8   |  -   | 1, Key shutdown request; <br> 1, Low battery shutdown request;        |
| VBAT_1                      |  21  |  2  |  u16   | mV | BATERY VLOTAGE 1 |
| VBAT_2                      |  23  |  2  |  u16   | mV | BATERY VLOTAGE 2 |
| -                      |  -   |  -  |   -   |  -   | -  |
| -                      |  -   |  -  |   -   |  -   | -  |
| firmware_version_major | 128  |  1  |  u8   |  -   | -  |
| firmware_version_minor | 129  |  1  |  u8   |  -   | -|
| firmware_version_micro | 130  |  1  |  u8   |  -   | - |
| rst_code               | 131  |  1  |  u8   |  -   | mcu reset reason Code|
| rtc_year               | 132  |  1  |  u8   |  -   | -  |
| rtc_month              | 133  |  1  |  u8   |  -   | -  |
| rtc_day                | 134  |  1  |  u8   |  -   | -  |
| rtc_hour               | 135  |  1  |  u8   |  -   | -  |
| rtc_minute             | 136  |  1  |  u8   |  -   | -  |
| rtc_second             | 137  |  1  |  u8   |  -   | -  |
| rtc_ssec               | 138  |  1  |  u8   |  -   | 1/128 second                                                          |
| alwaysOn               | 139  |  1  |  u8   |  -   | 0, Enable alwaysOn <br> 1, Disable alwaysOn                           |
| board_id_h               | 140  |  1  |  u8   |  -   | 
| board_id_l               | 141 |  1  |  u8   |  -   | 
| -     | 142  |  -  |  u8  |  -   |
| shutdown_pct           | 143  |  1  |  u8   |  -   | Current low battery shutdown percentage threshold                     |
| poweroff_pct           | 144  |  1  |  u8   |  -   | Current low battery poweroff percentage threshold                     |
| battery_IR             | 145  |  2  |  u16  | mOhm | battery IR                                                            |
| battery_middle_voltage | 147  |  2  |  u16  |  mV  | battery middle voltage                                                |
| battery real voltage          | 149  |  2  |  u16   |  -   | Battery Voltage with Current and Internal Resistance Compensation                                                |
| -    | 151  |  1  |  u8   |  -   | -|
| -    | 152  |  1  |  u8   |  -   | -|
| -    | 153  |  1  |  u8   |  -   | -|
| key-state               |154 | 1  |  u8   |  -   | 0, Released; <br> 1, SingleClicked; <br> 2, DoubleClicked; <br> 3, LongPressed2S; <br> 4,     LongPressed2SAndReleased; <br> 5, LongPressed5S; <br> 6, LongPressed5SAndReleased; 
|max_charging_current  | 155 | 1  |  u8   |  -   |N*100mA|
|SELECT_PDO | 156 | 1  |  u8   |  -   | 000: default max PDO<br>001: 5V<br>010: 9V<br>011: 12V<br>100: 15V<br>101: 20V|
| CHARGE_STATE  | 157 | 1  | u8  | -   | 000: standby<br>001: trickle charge<br>010: constant current charge<br>011: constant voltage charge<br>100: waiting for power source<br>101: fully charged<br>110: charging timeout |
| IS_FAST_CHARGE| 158  |  1 |  u8  |  -   | 0: normal 5V charge0: normal 5V charge<br>1: fast charge|
| -   | 159  |  1  |  u8   |  -   | -|
| TYPE_C_STATE   | 160  |  1  |  u8   |  -   |0: no cable<br>1: connected<br>2: error|
|TYPE_C_PDO | 161  |  1  |  u8   |   | supported PDO|
| BUZZER_VOL    | 162  |  1  |  u8   |  -   | volume of buzzer|
| -   | -  |  -  |  -   |  -  | -|
| ADVANCED_CMD_START   | 172| 1 |  u8  |  -  | Placeholder|
| BOOT_VERSION_MAJOR     | 173| 1 |  u8  |  -  | |
| BOOT_VERSION_MINOR     | 174| 1 |  u8  |  -  | |
| BOOT_VERSION_PATCH     | 175| 1 |  u8  |  -  | |
| FACTORY_VERSION_MAJOR     | 176| 1 |  u8  |  -  | |
| FACTORY_VERSION_MINOR     | 177| 1 |  u8  |  -  | |
| FACTORY_VERSION_PATCH     | 178| 1 |  u8  |  -  | |
| -   | -  |  -  |  -   |  -  | -|
| REG_MAIN_ENTRY_B3     | 183| 1 |  u8  |  -  | |
| REG_MAIN_ENTRY_B2     | 184| 1 |  u8  |  -  | |
| REG_MAIN_ENTRY_B1     | 185| 1 |  u8  |  -  | |
| REG_MAIN_ENTRY_B0     | 186| 1 |  u8  |  -  | |
| -   | -  |  -  |  -   |  -  | -|

## settingBuffer

| name         | addr | len | type | unit | description                                               |
| :----------- | :--: | :-: | :--: | :--: | :-------------------------------------------------------- |
| fan_power    |  0   |  1  |  u8  |  -   | setting fan power (0~100)                                 |
| rtc_year     |  1   |  1  |  u8  |  -   | setting rtc_year                                          |
| rtc_month    |  2   |  1  |  u8  |  -   | setting rtc_month                                         |
| rtc_day      |  3   |  1  |  u8  |  -   | setting rtc_day                                           |
| rtc_hour     |  4   |  1  |  u8  |  -   | setting rtc_hour                                          |
| rtc_minute   |  5   |  1  |  u8  |  -   | setting rtc_minute                                        |
| rtc_second   |  6   |  1  |  u8  |  -   | setting rtc_second                                        |
| rtc_ssec     |  7   |  1  |  u8  |  -   | setting rtc 1/128 second                                  |
| rtc_setting  |  8   |  1  |  u8  |  -   | 1, enable rtc setting                                     |
| shutdown_pct |  9   |  1  |  u8  |  -   | setting low battery shutdown percentage threshold (0~100) |
| poweroff_pct |  10  |  1  |  u8  |  -   | setting low battery poweroff percentage threshold (0~100) |
| CHARGE_SELECT |  11  |  1  |  u8  |  -   | setting charge max current, N*100mA |
|POWER_BTN_STATE| 12  |  1  |  u8  |  -   | write 0 to reset state |
| BUZZER_FEQ_L |  13  |  1  |  u8   |  -   | setting  buzzer freq_l|
| BUZZER_FEQ_H |  14  |  1  |  u8   |  -   | setting  buzzer freq_h|
| BUZZER_VOL |  15  |  1  |  u8   |  -   | setting  buzzer volumn|
| -            |  -   |  -  |  -   |  -   | -  |
