# 💧 Automatic Water Conditioning System

The **Automatic Water Conditioning System** is a Raspberry Pi Pico-based project designed to **automatically control water temperature and level**.  
It integrates **sensors, actuators, and MicroPython scripts** to maintain optimal water conditions for applications such as aquaculture or water tanks.

---

## 🚀 Features
- Automatic water level monitoring and control  
- Temperature regulation with fuzzy logic  
- Modular MicroPython scripts for maintainable and scalable code  
- Real-time control via Raspberry Pi Pico  
- Safety interlocks to prevent system faults  

---

## 🛠️ Tech Stack
- ![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-ED2B2B?style=for-the-badge&logo=raspberry-pi&logoColor=white)  
- ![MicroPython](https://img.shields.io/badge/MicroPython-2B2728?style=for-the-badge&logo=micropython&logoColor=white)  

---

## 📂 Project Structure

### `docs/` – Schematics & Documentation
- Block diagrams and wiring diagrams showing system architecture  
- Project report in PDF format with design notes and calculations  
- File: `system_block_diagram.png`, `wiring_diagram.pdf`, `project_report.pdf`  

### `media/` – Prototype & Visuals
- Photos of Raspberry Pi Pico setup and sensors  
- File: `pico_setup.jpg`, `sensor_wiring.jpg`

### `src/` – Source Code
- 12 modular MicroPython scripts handling all aspects of the system:
  - `main.py` – Main control loop  
  - `adc_levels.py` – Analog-to-digital readings  
  - `ads1x15.py` – ADC chip interface  
  - `fuzzy_control.py` – Fuzzy logic regulation  
  - `i2c_lcd.py`, `lcd_api.py`, `lcd_display.py` – LCD interface and display  
  - `interlocks.py` – Safety interlocks  
  - `keypad.py` – Keypad input handling  
  - `relays.py` – Relay control for actuators  
  - `sensors.py` – Sensor reading and calibration  
  - `servo_control.py` – Servo motor control  

---

## 👤 Author
**Fathurrahman Sahib**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-mfhrmn-blue?style=flat&logo=linkedin)](https://linkedin.com/in/mfhrmn)  
[![GitHub](https://img.shields.io/badge/GitHub-mfhrmn-black?style=flat&logo=github)](https://github.com/mfhrmn)  
[![Email](https://img.shields.io/badge/Email-mfhrmn@gmail.com-red?style=flat&logo=gmail&logoColor=white)](mailto:mfhrmn@gmail.com)

---

> **Tip:** Start by exploring `docs/` for the system schematics, then `src/` to see the modular MicroPython scripts, and finally `media/` to see the prototype in action.
