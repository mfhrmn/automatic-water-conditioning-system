from machine import Pin

relay_1 = Pin(11, Pin.OUT)
relay_2 = Pin(10, Pin.OUT)

# True = OFF, False = ON (inverted logic)
relay_1_status = True
relay_2_status = True

relay_1.high()
relay_2.high()

def relay_1_on():
    global relay_1_status
    relay_1.low()
    relay_1_status = False

def relay_1_off():
    global relay_1_status
    relay_1.high()
    relay_1_status = True

def relay_2_on():
    global relay_2_status
    relay_2.low()
    relay_2_status = False

def relay_2_off():
    global relay_2_status
    relay_2.high()
    relay_2_status = True

