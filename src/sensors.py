import onewire, ds18x20
from machine import Pin
import time

ds_heater = ds18x20.DS18X20(onewire.OneWire(Pin(26)))
ds_cooler = ds18x20.DS18X20(onewire.OneWire(Pin(27)))
ds_main = ds18x20.DS18X20(onewire.OneWire(Pin(28)))

def scan_sensors():
    heater_roms = ds_heater.scan()
    cooler_roms = ds_cooler.scan()
    main_roms = ds_main.scan()
    return heater_roms, cooler_roms, main_roms

def read_temp(ds_sensor, rom):
    try:
        ds_sensor.convert_temp()
        time.sleep(0.75)
        temp = ds_sensor.read_temp(rom)
    except Exception as e:
        temp = None
    return temp

