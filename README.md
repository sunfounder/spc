# SPC

- [SPC](#spc)
  - [API](#api)
    - [Class SPC(i2c)](#class-spci2c)
    - [Properties](#properties)
      - [SPC.device -\> class Device](#spcdevice---class-device)
    - [Methods](#methods)
      - [SPC.is\_ready() -\> bool](#spcis_ready---bool)
      - [SPC.read\_input\_voltage() -\> int](#spcread_input_voltage---int)
      - [SPC.read\_input\_current() -\> int](#spcread_input_current---int)
      - [SPC.read\_output\_voltage() -\> int](#spcread_output_voltage---int)
      - [SPC.read\_output\_current() -\> int](#spcread_output_current---int)
      - [SPC.read\_battery\_voltage() -\> int](#spcread_battery_voltage---int)
      - [SPC.read\_battery\_current() -\> int](#spcread_battery_current---int)
      - [SPC.read\_battery\_percentage() -\> int](#spcread_battery_percentage---int)
      - [SPC.read\_battery\_capacity() -\> int](#spcread_battery_capacity---int)
      - [SPC.read\_power\_source() -\> int](#spcread_power_source---int)
      - [SPC.read\_is\_input\_plugged\_in() -\> bool](#spcread_is_input_plugged_in---bool)
      - [SPC.read\_is\_battery\_plugged\_in() -\> bool](#spcread_is_battery_plugged_in---bool)
      - [SPC.read\_is\_charging() -\> bool](#spcread_is_charging---bool)
      - [SPC.read\_fan\_power() -\> int](#spcread_fan_power---int)
      - [SPC.read\_shutdown\_request() -\> bool](#spcread_shutdown_request---bool)
      - [SPC.read\_always\_on() -\> bool](#spcread_always_on---bool)
      - [SPC.read\_power\_source\_voltage() -\> int](#spcread_power_source_voltage---int)
      - [SPC.read\_shutdown\_percentage() -\> int](#spcread_shutdown_percentage---int)
      - [SPC.read\_power\_off\_percentage() -\> int](#spcread_power_off_percentage---int)
      - [SPC.read\_all() -\> dict](#spcread_all---dict)
      - [SPC.write\_fan\_power(power: int) -\> None](#spcwrite_fan_powerpower-int---none)
      - [SPC.write\_shutdown\_percentage(percentage: int) -\> None](#spcwrite_shutdown_percentagepercentage-int---none)
      - [SPC.write\_power\_off\_percentage(percentage: int) -\> None](#spcwrite_power_off_percentagepercentage-int---none)
      - [SPC.read\_firmware\_version() -\> str](#spcread_firmware_version---str)
    - [Constants](#constants)
      - [SPC.EXTERNAL\_INPUT](#spcexternal_input)
      - [SPC.BATTERY](#spcbattery)
      - [SPC.SHUTDOWN\_REQUEST\_NONE](#spcshutdown_request_none)
      - [SPC.SHUTDOWN\_REQUEST\_LOW\_BATTERY](#spcshutdown_request_low_battery)
      - [SPC.SHUTDOWN\_REQUEST\_BUTTON](#spcshutdown_request_button)
  - [About SunFounder](#about-sunfounder)
  - [Contact us](#contact-us)


Sunfounder Power Control

## API

### Class SPC(i2c)

Class for SunFounder Power Control.
- i2c: I2C object from machine module.

```
from spc.spc import SPC
from machine import Pin, I2C

# For the Raspberry Pi Pico, using I2C(0), pin 0 as SDA, pin 1 as SCL
i2c = I2C(0, sda=Pin(0), scl=Pin(1))

spc = SPC(i2c)
```

### Properties

#### SPC.device -> class Device 

current device class.

```
print(spc.device.name)
print(spc.device.peripheral)
```

### Methods

#### SPC.is_ready() -> bool

Check if the SPC is ready.

```
spc.is_ready()
```

#### SPC.read_input_voltage() -> int

Read the input voltage in mV.

```
input_voltage = spc.read_input_voltage()
print(f"Input voltage: {input_voltage} mV")
```

#### SPC.read_input_current() -> int

Read the input current in mA.

```
input_current = spc.read_input_current()
print(f"Input current: {input_current} mA")
```

#### SPC.read_output_voltage() -> int

Read the output voltage in mV.

```
output_voltage = spc.read_output_voltage()
print(f"Output voltage: {output_voltage} mV")
```

#### SPC.read_output_current() -> int

Read the output current in mA.

```
output_current = spc.read_output_current()
print(f"Output current: {output_current} mA")
```

#### SPC.read_battery_voltage() -> int

Read the battery voltage in mV.

```
battery_voltage = spc.read_battery_voltage()
print(f"Battery voltage: {battery_voltage} mV")
```

#### SPC.read_battery_current() -> int

Read the battery current in mA.

```
battery_current = spc.read_battery_current()
print(f"Battery current: {battery_current} mA")
```

#### SPC.read_battery_percentage() -> int

Read the battery percentage in %.

```
battery_percentage = spc.read_battery_percentage()
print(f"Battery percentage: {battery_percentage} %")
```

#### SPC.read_battery_capacity() -> int

Read the battery capacity in mAh.

```
battery_capacity = spc.read_battery_capacity()
print(f"Battery capacity: {battery_capacity} mAh")
```

#### SPC.read_power_source() -> int

Read the power source. 0: EXTERNAL_INPUT, 1: BATTERY.

```
power_source = spc.read_power_source()
if power_source == spc.EXTERNAL_INPUT:
    print("Power source: EXTERNAL_INPUT")
elif power_source == spc.BATTERY:
    print("Power source: BATTERY")
else:
    print("Unknown power source")
```

#### SPC.read_is_input_plugged_in() -> bool

Read if the input is plugged in.

```
is_input_plugged_in = spc.read_is_input_plugged_in()
print(f"Is input plugged in: {is_input_plugged_in}")
```

#### SPC.read_is_battery_plugged_in() -> bool

Read if the battery is plugged in.

```
is_battery_plugged_in = spc.read_is_battery_plugged_in()
print(f"Is battery plugged in: {is_battery_plugged_in}")
```

#### SPC.read_is_charging() -> bool

Read if the battery is charging.

```
is_charging = spc.read_is_charging()
print(f"Is charging: {is_charging}")
```

#### SPC.read_fan_power() -> int

Read the fan power in %.

```
fan_power = spc.read_fan_power()
print(f"Fan power: {fan_power} %")
```

#### SPC.read_shutdown_request() -> bool

Read if a shutdown request is received. 0: None, 1: Low battery, 2: Button.

```
shutdown_request = spc.read_shutdown_request()
if shutdown_request == spc.SHUTDOWN_REQUEST_NONE:
    print("Shutdown request: None")
elif shutdown_request == spc.SHUTDOWN_REQUEST_LOW_BATTERY:
    print("Shutdown request: Low battery")
elif shutdown_request == spc.SHUTDOWN_REQUEST_BUTTON:
    print("Shutdown request: Button")
else:
    print("Unknown shutdown request")
```

#### SPC.read_always_on() -> bool

Read if the always-on mode is enabled.

```
always_on = spc.read_always_on()
print(f"Always on: {always_on}")
```

#### SPC.read_power_source_voltage() -> int

Read the power source voltage in mV.

```
power_source_voltage = spc.read_power_source_voltage()
print(f"Power source voltage: {power_source_voltage} mV")
```

#### SPC.read_shutdown_percentage() -> int

Read the shutdown percentage in %.

```
shutdown_percentage = spc.read_shutdown_percentage()
print(f"Shutdown percentage: {shutdown_percentage} %")
```

#### SPC.read_power_off_percentage() -> int

Read the power off percentage in %.

```
power_off_percentage = spc.read_power_off_percentage()
print(f"Power off percentage: {power_off_percentage} %")
```

#### SPC.read_all() -> dict

Read all avaliable the data.

```
data = spc.read_all()
print(data)
```

#### SPC.write_fan_power(power: int) -> None

Write the fan power in %.

```
spc.write_fan_power(50)
```

#### SPC.write_shutdown_percentage(percentage: int) -> None

Write the shutdown percentage in %. Range: 10-100

```
spc.write_shutdown_percentage(10)
```

#### SPC.write_power_off_percentage(percentage: int) -> None

Write the power off percentage in %. Range: 5-100

```
spc.write_power_off_percentage(5)
```

#### SPC.read_firmware_version() -> str

Read the firmware version.

```
firmware_version = spc.read_firmware_version()
print(f"Firmware version: {firmware_version}")
```

### Constants

#### SPC.EXTERNAL_INPUT

Power source: EXTERNAL_INPUT.

#### SPC.BATTERY

Power source: BATTERY.

#### SPC.SHUTDOWN_REQUEST_NONE

Shutdown request: None.

#### SPC.SHUTDOWN_REQUEST_LOW_BATTERY

Shutdown request: Low battery.

#### SPC.SHUTDOWN_REQUEST_BUTTON

Shutdown request: Button.


## About SunFounder
SunFounder is a company focused on STEAM education with products like open source robots, development boards, STEAM kit, modules, tools and other smart devices distributed globally. In SunFounder, we strive to help elementary and middle school students as well as hobbyists, through STEAM education, strengthen their hands-on practices and problem-solving abilities. In this way, we hope to disseminate knowledge and provide skill training in a full-of-joy way, thus fostering your interest in programming and making, and exposing you to a fascinating world of science and engineering. To embrace the future of artificial intelligence, it is urgent and meaningful to learn abundant STEAM knowledge.

## Contact us
website:
    www.sunfounder.com

E-mail:
    service@sunfounder.com