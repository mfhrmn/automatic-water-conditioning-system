from machine import Pin
import time

rows = [Pin(2, Pin.OUT), Pin(3, Pin.OUT), Pin(4, Pin.OUT), Pin(5, Pin.OUT)]
cols = [Pin(6, Pin.IN, Pin.PULL_DOWN), Pin(7, Pin.IN, Pin.PULL_DOWN),
        Pin(8, Pin.IN, Pin.PULL_DOWN), Pin(9, Pin.IN, Pin.PULL_DOWN)]

keymap = [
    ['D', 'C', 'B', 'A'],
    ['#', '9', '6', '3'],
    ['0', '8', '5', '2'],
    ['*', '7', '4', '1']
]

def scan_keypad():
    for r in range(4):
        rows[r].on()
        for c in range(4):
            if cols[c].value() == 1:
                while cols[c].value() == 1:
                    time.sleep_ms(10)
                rows[r].off()
                return keymap[r][c]
        rows[r].off()
    return None

