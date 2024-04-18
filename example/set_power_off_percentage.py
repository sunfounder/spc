from spc.spc import SPC
import time

spc = SPC()

print(f"Board name: {spc.device.name}")
print(f"Firmware Version: {spc.read_firmware_version()}")
print(f"Set power off percentage example, power off percentage means when battery percentage")
print(f"is less than the power off percentage, the device will cut off the power to protect battery.")
time.sleep(2)

def test(value):
    print(f"Current shutdown percentage: {spc.read_power_off_percentage()}%")
    time.sleep(2)
    print(f"Setting power off percentage to {value}%")
    spc.write_power_off_percentage(value)
    time.sleep(2) # Wait for the power off percentage to be updated
    current_power_off_battery_percentage = spc.read_power_off_percentage()
    print(f"Shutdown percentage: {current_power_off_battery_percentage}%")
    if current_power_off_battery_percentage == value:
        print("Success")
    else:
        print("Failed, power off percentage range is 5-100%")

test(20)
time.sleep(2)
test(10)
time.sleep(2)
test(0)
time.sleep(2)
