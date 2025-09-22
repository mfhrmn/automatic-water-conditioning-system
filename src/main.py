import time
from servo_control import initialize_servos, percentage_to_duty, servo_heater, servo_cooler, servo_utama, servo_states
from keypad import scan_keypad
import lcd_display
import sensors
import interlocks
import relays
import adc_levels
import permissive

from fuzzy_control import fuzzy_sugeno

# Variables for fuzzy control error tracking
last_error = 0
last_time = time.ticks_ms()

# Menu and mode variables
menu_items = [
    "Setpoint Utama",
    "Sensor Suhu",
    "Sensor Level",
    "Kontrol Manual"
]

current_selection = 0
mode = "menu"
setpoint = ""

def show_menu(selected):
    lcd_display.clear()
    for i, item in enumerate(menu_items):
        lcd_display.move_to(0, i)
        if i == selected:
            lcd_display.putstr(">")
        else:
            lcd_display.putstr(" ")
        lcd_display.putstr(item[:19])

def handle_menu():
    global current_selection, mode, setpoint
    show_menu(current_selection)

    while True:
        key = scan_keypad()
        if key:
            if mode == "menu":
                if key == 'A':
                    current_selection = (current_selection - 1) % len(menu_items)
                    show_menu(current_selection)
                elif key == 'B':
                    current_selection = (current_selection + 1) % len(menu_items)
                    show_menu(current_selection)
                elif key == '#':
                    selected_item = menu_items[current_selection]
                    if selected_item == "Setpoint Utama":
                        mode = "input_setpoint"
                    elif selected_item == "Sensor Suhu":
                        mode = "baca_suhu"
                    elif selected_item == "Sensor Level":
                        mode = "baca_level"
                    elif selected_item == "Kontrol Manual":
                        mode = "kontrol_manual"
                    break
            time.sleep(0.1)
    lcd_display.clear()

def run_fuzzy_control():
    global mode, setpoint
    inputting_setpoint = False
    new_setpoint = None
    last_error = 0
    last_time = time.ticks_ms()
    last_valid_temp = None  # Store last valid temperature here
    start_time = time.ticks_ms()  # Start time recorded here!

    sensor_detected = False  # Flag to track if sensor has been detected
    main_rom_id = None       # Store main ROM ID when detected
    target_temp = float(setpoint)

    while True:
        relay1_locked, relay2_locked, servo_locked = interlocks.apply_interlocks()
        if servo_locked:
            # Interlock active: pause PID control
            servo_heater.duty_u16(percentage_to_duty(0, "heater"))
            servo_cooler.duty_u16(percentage_to_duty(0, "cooler"))

            # Just wait and keep checking, don't proceed further
            time.sleep(0.5)
            continue

        temp_main = None

        if not sensor_detected:
            # Retry loop for detecting main_roms only if not detected yet
            retry_count = 0
            while retry_count < 10:
                heater_roms, cooler_roms, main_roms = sensors.scan_sensors()
                if main_roms:
                    main_rom_id = main_roms[0]
                    sensor_detected = True
                    temp_main = sensors.read_temp(sensors.ds_main, main_rom_id)
                    break  # Exit retry loop
                else:
                    retry_count += 1
                    time.sleep(0.2)  # Small delay between retries

            if not sensor_detected:
                lcd_display.clear()
                lcd_display.move_to(0, 0)
                lcd_display.putstr("Sensor Error")
                mode = "menu"
                time.sleep(2)
                break  # Exit run_fuzzy_control loop
        else:
            # Sensor already detected, just try to read temp directly
            try:
                temp_main = sensors.read_temp(sensors.ds_main, main_rom_id)
            except Exception:
                # Reading failed, keep temp_main as None to use last valid temp
                temp_main = None

        try:
            if temp_main is not None:
                last_valid_temp = temp_main  # Update last valid temp
            else:
                temp_main = last_valid_temp  # Use last valid temp if no new reading
                time.sleep(0.1)

            if temp_main is not None and setpoint:
                target_temp = float(setpoint)
                current_temp = temp_main

                error = target_temp - current_temp
                now = time.ticks_ms()
                dt = time.ticks_diff(now, last_time) / 1000
                delta_error = 0
                if dt > 0:
                    delta_error = (error - last_error) / dt

                last_error = error
                last_time = now

                value = fuzzy_sugeno(error, delta_error)
                percentage_value = value / 100

                elapsed_time = time.ticks_diff(now, start_time)

                # PRINT TO TERMINAL:
                print(f"Time: {elapsed_time / 1000:.2f}s, Setpoint: {float(setpoint):.2f}C, Temp: {current_temp:.2f}C, Output : {percentage_value:.2f}%")

                # Control heater servo with fuzzy output
                duty_heater = percentage_to_duty(percentage_value * 100, "heater")
                duty_cooler = percentage_to_duty((1 - percentage_value) * 100, "cooler")

                servo_heater.duty_u16(duty_heater)
                servo_cooler.duty_u16(duty_cooler)
                
                # If we're inputting new setpoint, show that UI and capture input

                key = scan_keypad()
                if key == '*':
                    mode = "menu"
                    # Turn off servo when exiting fuzzy control
                    servo_heater.duty_u16(percentage_to_duty(0, "heater"))
                    servo_cooler.duty_u16(percentage_to_duty(0, "cooler"))
                    break
                elif key == '#' and not inputting_setpoint:
                    inputting_setpoint = True
                    new_setpoint = None
                    lcd_display.clear()
                    
                if inputting_setpoint:
                    result = input_new_setpoint(new_setpoint or setpoint)
                    if result == "cancel":
                        inputting_setpoint = False
                        lcd_display.clear()
                    elif result is not None:  # New setpoint confirmed
                        setpoint = result
                        inputting_setpoint = False
                        lcd_display.clear()
                    else:
                        # Still entering, just continue showing input
                        pass

                if not inputting_setpoint:
                    lcd_display.clear()
                    lcd_display.putstr("Temp: {:.2f} C".format(current_temp))
                    lcd_display.move_to(0, 1)
                    lcd_display.putstr("Setpoint: {:.2f} C".format(target_temp))
                    lcd_display.move_to(0, 2)
                    lcd_display.putstr("Output: {:.2f}%".format(percentage_value))
                    lcd_display.move_to(0, 3)
                    lcd_display.putstr("*:EXIT #:Set New SP")
            else:
                # No valid temp or setpoint - turn off heater
                servo_heater.duty_u16(percentage_to_duty(0, "heater"))
                servo_cooler.duty_u16(percentage_to_duty(0, "cooler"))

        except Exception as e:
            print("Exception occurred:", e)
            import sys
            import traceback
            traceback.print_exc()
            lcd_display.clear()
            lcd_display.putstr("Error")
            time.sleep(2)
            break

        time.sleep(0.1)

def input_new_setpoint(current_setpoint):

    lcd_display.move_to(0, 0)
    lcd_display.putstr("Setpoint (20-40 C):")
    lcd_display.move_to(0, 1)

    entered = ""
    # Use a loop that runs for a short time, collecting input, but returns quickly.
    start_time = time.ticks_ms()

    while True:
        key = scan_keypad()
        if key:
            if key.isdigit():
                if len(entered) < 2:  # limit input length to 2 digits
                    entered += key
                    lcd_display.clear()
                    lcd_display.putstr("Setpoint (20-40 C):")
                    lcd_display.move_to(0, 1)
                    lcd_display.putstr(entered + " C")
                time.sleep(0.2)  # debounce
            elif key == '#':  # Confirm
                try:
                    val = int(entered)
                    if 20 <= val <= 40:
                        return str(val)  # valid new setpoint
                    else:
                        lcd_display.clear()
                        lcd_display.putstr("Out of range")
                        time.sleep(1)
                        lcd_display.clear()
                        lcd_display.putstr("Setpoint (20-40 C):")
                        lcd_display.move_to(0, 1)
                        entered = ""
                except:
                    lcd_display.clear()
                    lcd_display.putstr("Invalid input")
                    time.sleep(1)
                    lcd_display.clear()
                    lcd_display.putstr("Setpoint (20-40 C):")
                    lcd_display.move_to(0, 1)
                    entered = ""
            elif key == '*':  # Cancel
                return "cancel"
        # Return None to indicate still entering or no key
        # But add a timeout so this doesn't hang too long
        if time.ticks_diff(time.ticks_ms(), start_time) > 5000:  # 5 sec timeout
            return None
        time.sleep(0.1)
        
def input_setpoint_mode():
    global mode, setpoint
    lcd_display.clear()
    lcd_display.putstr("Setpoint (20-40 C):")  # changed here
    setpoint = ""
    lcd_display.move_to(0, 1)

    while True:
        interlocks.apply_interlocks()
        key = scan_keypad()
        if key:
            if key.isdigit():
                setpoint += key
                lcd_display.clear()
                lcd_display.putstr("Setpoint (20-40 C):")  # changed here
                lcd_display.move_to(0, 1)
                lcd_display.putstr(setpoint + " C")
            elif key == '#':  # Confirm
                try:
                    val = int(setpoint)
                    if 20 <= val <= 40:  # changed range here
                        lcd_display.clear()
                        lcd_display.putstr("SP saved: {} C".format(val))
                        setpoint = str(val)
                        time.sleep(2)

                        # Option after saving setpoint
                        lcd_display.clear()
                        lcd_display.putstr("#: Mulai Fuzzy")
                        lcd_display.move_to(0, 1)
                        lcd_display.putstr("*: Kembali")

                        while True:
                            key2 = scan_keypad()
                            if key2 == "#":
                                run_fuzzy_control()
                                break
                            elif key2 == "*":
                                mode = "menu"
                                break
                            time.sleep(0.1)
                        break  # exit input_setpoint_mode()
                    else:
                        lcd_display.clear()
                        lcd_display.putstr("Out of range")
                        time.sleep(2)
                        lcd_display.clear()
                        lcd_display.putstr("Setpoint (20-40 C):")  # changed here
                        setpoint = ""
                except:
                    lcd_display.clear()
                    lcd_display.putstr("Invalid input")
                    time.sleep(2)
                    lcd_display.clear()
                    lcd_display.putstr("Setpoint (20-40 C):")  # changed here
                    setpoint = ""
            elif key == '*':  # Cancel
                mode = "menu"
                break
        time.sleep(0.1)


def baca_suhu_mode():
    global mode
    lcd_display.clear()
    lcd_display.putstr("Baca Sensor Suhu")
    time.sleep(1)

    while True:
        interlocks.apply_interlocks()
        try:
            heater_roms, cooler_roms, main_roms = sensors.scan_sensors()

            temp_heater = None
            temp_cooler = None
            temp_main = None

            if heater_roms:
                try:
                    temp_heater = sensors.read_temp(sensors.ds_heater, heater_roms[0])
                except Exception:
                    temp_heater = None

            if cooler_roms:
                try:
                    temp_cooler = sensors.read_temp(sensors.ds_cooler, cooler_roms[0])
                except Exception:
                    temp_cooler = None

            if main_roms:
                try:
                    temp_main = sensors.read_temp(sensors.ds_main, main_roms[0])
                except Exception:
                    temp_main = None

            lcd_display.clear()
            lcd_display.putstr("Heater: {} C".format(f"{temp_heater:.2f}" if temp_heater is not None else "N/A"))
            lcd_display.move_to(0, 1)
            lcd_display.putstr("Cooler: {} C".format(f"{temp_cooler:.2f}" if temp_cooler is not None else "N/A"))
            lcd_display.move_to(0, 2)
            lcd_display.putstr("Utama: {} C".format(f"{temp_main:.2f}" if temp_main is not None else "N/A"))
            lcd_display.move_to(0, 3)
            lcd_display.putstr("Press '*' to exit")

            key = scan_keypad()
            if key == '*':
                mode = "menu"
                break

            time.sleep(0.5)

        except Exception as e:
            lcd_display.clear()
            lcd_display.putstr("Sensor error")
            time.sleep(2)
            break
            
def print_level_readings():
    raw_LH_Heater, raw_LL_Heater, raw_LH_Cooler, raw_LL_Cooler = adc_levels.read_adc_level1()
    raw_LL_Utama, raw_LH_Utama = adc_levels.read_adc_level2()

    val_LL_Heater = adc_levels.raw_to_voltage_level1(raw_LL_Heater)
    val_LH_Heater = adc_levels.raw_to_voltage_level1(raw_LH_Heater)
    val_LL_Cooler = adc_levels.raw_to_voltage_level1(raw_LL_Cooler)
    val_LH_Cooler = adc_levels.raw_to_voltage_level1(raw_LH_Cooler)
    val_LL_Utama = adc_levels.raw_to_voltage_level2(raw_LL_Utama)
    val_LH_Utama = adc_levels.raw_to_voltage_level2(raw_LH_Utama)

def baca_level_mode():
    global mode
    lcd_display.clear()
    lcd_display.putstr("Baca Sensor Level")
    time.sleep(1)

    while True:
        # Read all raw ADC values at once
        interlocks.apply_interlocks()
        raw_LH_Heater, raw_LL_Heater, raw_LH_Cooler, raw_LL_Cooler = adc_levels.read_adc_level1()
        raw_LL_Utama, raw_LH_Utama = adc_levels.read_adc_level2()

        # Convert raw to voltage
        val_LL_Heater = adc_levels.raw_to_voltage_level1(raw_LL_Heater)
        val_LH_Heater = adc_levels.raw_to_voltage_level1(raw_LH_Heater)
        val_LL_Cooler = adc_levels.raw_to_voltage_level1(raw_LL_Cooler)
        val_LH_Cooler = adc_levels.raw_to_voltage_level1(raw_LH_Cooler)
        val_LL_Utama = adc_levels.raw_to_voltage_level2(raw_LL_Utama)
        val_LH_Utama = adc_levels.raw_to_voltage_level2(raw_LH_Utama)

        # Update LCD with readings
        lcd_display.move_to(0, 0)
        lcd_display.putstr("Htr L:{:.2f} H:{:.2f}  ".format(val_LL_Heater, val_LH_Heater))
        lcd_display.move_to(0, 1)
        lcd_display.putstr("Clr L:{:.2f} H:{:.2f}  ".format(val_LL_Cooler, val_LH_Cooler))
        lcd_display.move_to(0, 2)
        lcd_display.putstr("UtmaL:{:.2f} H:{:.2f}  ".format(val_LL_Utama, val_LH_Utama))
        lcd_display.move_to(0, 3)
        lcd_display.putstr("(*) Kembali      ")

        # Check for exit key
        key = scan_keypad()
        if key == "*":
            mode = "menu"
            break

        time.sleep(0.5)

        
def kontrol_manual_mode():
    global mode, relay_1_status, relay_2_status

    relay_1_status = False
    relay_2_status = False
    lcd_display.clear()
    lcd_display.putstr("B:Servo; C:S1; D:S2")
    lcd_display.move_to(0, 3)
    lcd_display.putstr("(*) Kembali")
    max_retries = 3
    retry_delay = 0.5  # seconds

    while True:
        # Try to read interlocks with retries
        for attempt in range(max_retries):
            try:
                relay1_locked, relay2_locked, servo_locked = interlocks.apply_interlocks()
                break  # success, exit retry loop
            except Exception as e:
                time.sleep(retry_delay)
        else:
            time.sleep(2)
            mode = "menu"
            break
        
        key = scan_keypad()
        if key:
            if key == "*":
                mode = "menu"
                break
            elif key == "1":
                if servo_locked:
                    lcd_display.move_to(0, 1)
                    lcd_display.putstr("Servo Heater Locked!")
                else:
                    servo_states["heater"] = not servo_states["heater"]
                    pos = 100 if servo_states["heater"] else 0
                    servo_heater.duty_u16(percentage_to_duty(pos, "heater"))
                    
                    lcd_display.move_to(0, 1)
                    if servo_states["utama"]:
                        lcd_display.putstr("Servo Heater Opened  ")
                    else:
                        lcd_display.putstr("Servo Heater Closed  ")
                        
            elif key == "2":
                if servo_locked:
                    lcd_display.move_to(0, 1)
                    lcd_display.putstr("Servo Cooler Locked!")
                else:
                    servo_states["cooler"] = not servo_states["cooler"]
                    pos = 100 if servo_states["cooler"] else 0
                    servo_cooler.duty_u16(percentage_to_duty(pos, "cooler"))
                    
                    lcd_display.move_to(0, 1)
                    if servo_states["utama"]:
                        lcd_display.putstr("Servo Cooler Opened  ")
                    else:
                        lcd_display.putstr("Servo Cooler Closed  ")

            elif key == "3":
                lcd_display.move_to(0, 1)
                lcd_display.putstr("               ")
                servo_states["utama"] = not servo_states["utama"]
                pos = 100 if servo_states["utama"] else 0
                servo_utama.duty_u16(percentage_to_duty(pos, "utama"))
                
                lcd_display.move_to(0, 1)
                if servo_states["utama"]:
                    lcd_display.putstr("Servo Utama Opened  ")
                else:
                    lcd_display.putstr("Servo Utama Closed  ")
                    

            elif key == "C":
                if relay1_locked:
                    lcd_display.move_to(0, 1)
                    lcd_display.putstr("Relay Heater Locked!")
                else:
                    if relay_1_status:
                        relays.relay_1_off()
                        relay_1_status = False
                        lcd_display.move_to(0, 1)
                        lcd_display.putstr("Relay Heater OFF   ")
                    else:
                        relays.relay_1_on()
                        relay_1_status = True
                        lcd_display.move_to(0, 1)
                        lcd_display.putstr("Relay Heater ON    ")

            elif key == "D":
                if relay2_locked:
                    lcd_display.move_to(0, 1)
                    lcd_display.putstr("Relay Cooler Locked!")
                else:
                    if relay_2_status:
                        relays.relay_2_off()
                        relay_2_status = False
                        lcd_display.move_to(0, 1)
                        lcd_display.putstr("Relay Cooler OFF   ")
                    else:
                        relays.relay_2_on()
                        relay_2_status = True
                        lcd_display.move_to(0, 1)
                        lcd_display.putstr("Relay Cooler ON    ")
                    

        time.sleep(0.1)

initialize_servos()

while True:
    interlocks.apply_interlocks()
    if mode == "menu":
        handle_menu()
    elif mode == "input_setpoint":
        input_setpoint_mode()
    elif mode == "baca_suhu":
        baca_suhu_mode()
    elif mode == "baca_level":
        baca_level_mode()
    elif mode == "kontrol_manual":
        kontrol_manual_mode()
    else:
        mode = "menu"

    time.sleep(0.1)