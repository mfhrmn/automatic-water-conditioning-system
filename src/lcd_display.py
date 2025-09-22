from machine import I2C, Pin
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
lcd_addr = i2c.scan()[0]
lcd = I2cLcd(i2c, lcd_addr, 4, 20)

def clear():
    lcd.clear()

def putstr(text):
    lcd.putstr(text)

def move_to(x, y):
    lcd.move_to(x, y)

