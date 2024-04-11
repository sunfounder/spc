from spc.spc import SPC
import time

spc = SPC()

print(f"Board name: {spc.device.name}")
print(f"Firmware Version: {spc.read_firmware_version()}")
print(f"Shutdown battery percentage: {spc.read_shutdown_battery_percentage()}%")
time.sleep(2)
print(f"Setting shutdown battery percentage to 20%")
spc.write_shutdown_battery_percentage(20)
time.sleep(2) # Wait for the shutdown battery percentage to be updated
current_shutdown_battery_percentage = spc.read_shutdown_battery_percentage()
print(f"Shutdown battery percentage: {current_shutdown_battery_percentage}%")
if current_shutdown_battery_percentage == 20:
    print("Success")
time.sleep(2)
print(f"Setting shutdown battery percentage to 10%")
spc.write_shutdown_battery_percentage(10)
time.sleep(2) # Wait for the shutdown battery percentage to be updated
current_shutdown_battery_percentage = spc.read_shutdown_battery_percentage()
print(f"Shutdown battery percentage: {current_shutdown_battery_percentage}%")
if current_shutdown_battery_percentage == 10:
    print("Success")
    
time.sleep(2)
print(f"Setting shutdown battery percentage to 5%")
spc.write_shutdown_battery_percentage(5)
time.sleep(2) # Wait for the shutdown battery percentage to be updated
current_shutdown_battery_percentage = spc.read_shutdown_battery_percentage()
print(f"Shutdown battery percentage: {current_shutdown_battery_percentage}%")
if current_shutdown_battery_percentage == 5:
    print("Success")
else:
    print("Failed, shutdown battery percentage minimal is 10%")
