from machine import I2C, Pin
from ads1x15 import ADS1115

ads_i2c_bus = I2C(1, scl=Pin(19), sda=Pin(18), freq=400000)
adc_level1 = ADS1115(ads_i2c_bus, address=0x48, gain=1)
adc_level2 = ADS1115(ads_i2c_bus, address=0x49, gain=1)

def read_adc_level1():
    raw_LH_Heater = adc_level1.read(channel1=0, channel2=None)
    raw_LL_Heater = adc_level1.read(channel1=1, channel2=None)
    raw_LH_Cooler = adc_level1.read(channel1=2, channel2=None)
    raw_LL_Cooler = adc_level1.read(channel1=3, channel2=None)
    return raw_LH_Heater, raw_LL_Heater, raw_LH_Cooler, raw_LL_Cooler

def read_adc_level2():
    raw_LH_Utama = adc_level2.read(channel1=0, channel2=None)
    raw_LL_Utama = adc_level2.read(channel1=1, channel2=None)
    return raw_LL_Utama, raw_LH_Utama

def raw_to_voltage_level1(raw):
    return adc_level1.raw_to_v(raw)

def raw_to_voltage_level2(raw):
    return adc_level2.raw_to_v(raw)

