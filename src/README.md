# 💻 Source Code – Automatic Water Conditioning System

This folder contains all **MicroPython scripts** running on the Raspberry Pi Pico for the Automatic Water Conditioning System.  
The project is modular, with each module responsible for a specific function.

---

## Contents

- `main.py` – Main control loop that integrates all modules  
- `adc_levels.py` – Reads analog signals from sensors  
- `ads1x15.py` – Interface with ADC chip  
- `fuzzy_control.py` – Fuzzy logic to regulate water temperature and level  
- `i2c_lcd.py` – Handles LCD communication over I2C  
- `interlocks.py` – Safety interlock logic  
- `keypad.py` – Keypad input handling  
- `lcd_api.py` – LCD API support functions  
- `lcd_display.py` – High-level routines to display info on LCD  
- `relays.py` – Relay control for actuators  
- `sensors.py` – Sensor reading, calibration, and data processing  
- `servo_control.py` – Servo motor control

---

> **Tip:** Start with `main.py` to see the overall program flow, then explore individual modules to understand how each system component is handled.
