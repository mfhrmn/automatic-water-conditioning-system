import adc_levels
import relays
from servo_control import servo_heater, servo_cooler, servo_utama, percentage_to_duty

# Initialize lock flags
relay1_locked = False
relay2_locked = False
servo_locked = False

# Initialize sensor states for interlock sensors
sensor_states = {
    "LH_Heater": False,
    "LL_Heater": False,
    "LH_Cooler": False,
    "LL_Cooler": False,
    "LH_Utama": False,
    "LL_Utama": False,
}

def check_sensor_state(name, voltage, threshold=3.5):
    """
    Track sensor HIGH/LOW state and print on state changes.
    Returns True if HIGH, False if LOW.
    """
    global sensor_states
    if voltage > threshold and not sensor_states[name]:
        sensor_states[name] = True
        #print(f"{name} sensor is HIGH")
    elif voltage <= threshold and sensor_states[name]:
        sensor_states[name] = False
        #print(f"{name} sensor is LOW")
    return sensor_states[name]

def verify_sensor(read_voltage_func, *args, threshold=3.5, max_attempts=3):
    """
    Verify the sensor reading by checking it multiple times.
    Returns the voltage if readings agree, else None.
    """
    readings = []
    for _ in range(max_attempts):
        voltage = read_voltage_func(*args)
        readings.append(voltage)
    # Check if all readings are consistent (all above or all below threshold)
    all_high = all(v > threshold for v in readings)
    all_low = all(v <= threshold for v in readings)

    if all_high:
        return readings[-1]  # return last reading if all high
    elif all_low:
        return readings[-1]  # return last reading if all low
    else:
        # Inconsistent readings, return None to avoid state change
        return None


def apply_interlocks():
    global relay1_locked, relay2_locked, servo_locked

    high_voltage_threshold = 3.3

    # Read raw ADC values once for each sensor group
    raw_LH_Heater, raw_LL_Heater, raw_LH_Cooler, raw_LL_Cooler = adc_levels.read_adc_level1()
    raw_LL_Utama, raw_LH_Utama = adc_levels.read_adc_level2()

    # Verify and convert voltages with double check

    val_LH_Heater = verify_sensor(adc_levels.raw_to_voltage_level1, raw_LH_Heater, threshold=high_voltage_threshold)
    val_LL_Heater = verify_sensor(adc_levels.raw_to_voltage_level1, raw_LL_Heater, threshold=high_voltage_threshold)
    val_LH_Cooler = verify_sensor(adc_levels.raw_to_voltage_level1, raw_LH_Cooler, threshold=high_voltage_threshold)
    val_LL_Cooler = verify_sensor(adc_levels.raw_to_voltage_level1, raw_LL_Cooler, threshold=high_voltage_threshold)
    val_LH_Utama = verify_sensor(adc_levels.raw_to_voltage_level2, raw_LH_Utama, threshold=high_voltage_threshold)
    val_LL_Utama = verify_sensor(adc_levels.raw_to_voltage_level2, raw_LL_Utama, threshold=high_voltage_threshold)

    # If verification failed (None), keep previous states to avoid false triggering
    def safe_check(name, val):
        if val is None:
            # Return previous state without change
            return sensor_states[name]
        else:
            return check_sensor_state(name, val, high_voltage_threshold)

    # Check sensors and track states with printouts
        # Check sensors and track states with printouts
    LH_Heater_high = safe_check("LH_Heater", val_LH_Heater)
    LL_Heater_high = safe_check("LL_Heater", val_LL_Heater)
    LH_Cooler_high = safe_check("LH_Cooler", val_LH_Cooler)
    LL_Cooler_high = safe_check("LL_Cooler", val_LL_Cooler)
    LH_Utama_high = safe_check("LH_Utama", val_LH_Utama)
    LL_Utama_high = safe_check("LL_Utama", val_LL_Utama)

    # Enforce rule: If LL is LOW, then LH must be LOW (regardless of voltage)
    if not LL_Heater_high:
        if LH_Heater_high:
            #print("LL_Heater LOW forces LH_Heater LOW")
            LH_Heater_high = False

    if not LL_Cooler_high:
        if LH_Cooler_high:
            #print("LL_Cooler LOW forces LH_Cooler LOW")
            LH_Cooler_high = False

    if not LL_Utama_high:
        if LH_Utama_high:
            #print("LL_Utama LOW forces LH_Utama LOW")
            LH_Utama_high = False
            
    # Enforce rule: If LH is HIGH, then LL must be HIGH (force LL HIGH if LH HIGH)
    if LH_Heater_high and not LL_Heater_high:
        LL_Heater_high = True

    if LH_Cooler_high and not LL_Cooler_high:
        LL_Cooler_high = True

    if LH_Utama_high and not LL_Utama_high:
        LL_Utama_high = True

    # Relay 1 interlock
    if LH_Heater_high:
        relay1_locked = True
        relays.relay_1_off()
    elif not LL_Heater_high:
        relay1_locked = False
        relays.relay_1_on()

    # Relay 2 interlock
    if LH_Cooler_high:
        relay2_locked = True
        relays.relay_2_off()
    elif not LL_Cooler_high:
        relay2_locked = False
        relays.relay_2_on()

    # Servo interlock
    if LH_Utama_high:
        servo_locked = True
        servo_heater.duty_u16(percentage_to_duty(0, "heater"))   # Servo Heater OFF
        servo_cooler.duty_u16(percentage_to_duty(0, "cooler"))   # Servo Cooler OFF
        servo_utama.duty_u16(percentage_to_duty(100, "utama"))   # Servo Utama ON
    elif not LL_Utama_high:
        servo_locked = False
        servo_utama.duty_u16(percentage_to_duty(0, "utama"))     # Servo Utama OFF

    return relay1_locked, relay2_locked, servo_locked


