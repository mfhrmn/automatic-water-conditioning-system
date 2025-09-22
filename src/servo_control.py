from machine import Pin, PWM
from time import sleep

# Duty cycle ranges
max_duty_heater = 5000
min_duty_heater = 2900

max_duty_cooler = 5500
min_duty_cooler = 2900

max_duty_utama = 4600
min_duty_utama = 1400

# Setup servo pins and PWM
pin_servo_heater = Pin(12, Pin.OUT)
pin_servo_cooler = Pin(13, Pin.OUT)
pin_servo_utama = Pin(14, Pin.OUT)

servo_heater = PWM(pin_servo_heater)
servo_cooler = PWM(pin_servo_cooler)
servo_utama = PWM(pin_servo_utama)

servo_heater.freq(50)
servo_cooler.freq(50)
servo_utama.freq(50)

servo_states = {
    "heater": False,
    "cooler": False,
    "utama": False
}
def percentage_to_duty(percentage, device):
    # Clamp percentage between 0 and 100
    if percentage < 0:
        percentage = 0
    elif percentage > 100:
        percentage = 100

    if device == "heater":
        duty = max_duty_heater - (percentage / 100) * (max_duty_heater - min_duty_heater)
    elif device == "cooler":
        duty = min_duty_cooler + (percentage / 100) * (max_duty_cooler - min_duty_cooler)
    elif device == "utama":
        duty = max_duty_utama - (percentage / 100) * (max_duty_utama - min_duty_utama)
    else:
        duty = 0
    return int(duty)

def initialize_servos():
    servo_heater.duty_u16(percentage_to_duty(0, "heater"))
    servo_cooler.duty_u16(percentage_to_duty(0, "cooler"))
    servo_utama.duty_u16(percentage_to_duty(0, "utama"))

