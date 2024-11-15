"""====================================================================================
                        ------->  Revision History  <------
====================================================================================

Date            Who         Ver         Changes
====================================================================================
11-Nov-24       SM          1000        Initial creation
===================================================================================="""

# Import the normal ranges and alarm colors from the config file
from config import HEART_RATE_RANGE, SPO2_RANGE, RESPIRATORY_RATE_RANGE, TEMP_RANGE, ALARM_LOW, ALARM_HIGH, ALARM_NORMAL

def check_vital_signs(heart_rate, spo2, respiratory_rate, body_temp):
    """
    This function checks whether each vital sign (heart rate, SpO2, respiratory rate, body temperature)
    is within the normal range. It returns the corresponding color (blue, red, or black) 
    based on the condition of the vital sign:
    - Blue: Below the normal range (ALARM_LOW)
    - Red: Above the normal range (ALARM_HIGH)
    - Black: Within the normal range (ALARM_NORMAL)

    Parameters:
    - heart_rate (float): The heart rate in beats per minute (bpm).
    - spo2 (float): The oxygen saturation level in percentage (%).
    - respiratory_rate (float): The respiratory rate in breaths per minute.
    - body_temp (float): The body temperature in degrees Celsius.

    Returns:
    - Tuple of strings: A tuple containing the color for each vital sign (heart rate, SpO2, respiratory rate, body temperature).
    """
    
    # Check if each vital sign is below, above, or within the normal range
    # Use the color codes defined in config.py for alarm low, alarm high, and normal status.
    
    # Heart rate check (Normal: 60-100 bpm)
    heart_rate_color = ALARM_LOW if heart_rate < HEART_RATE_RANGE[0] else ALARM_HIGH if heart_rate > HEART_RATE_RANGE[1] else ALARM_NORMAL
    
    # SpO2 check (Normal: 95-100%)
    spo2_color = ALARM_LOW if spo2 < SPO2_RANGE[0] else ALARM_HIGH if spo2 > SPO2_RANGE[1] else ALARM_NORMAL
    
    # Respiratory rate check (Normal: 12-20 breaths per minute)
    respiratory_rate_color = ALARM_LOW if respiratory_rate < RESPIRATORY_RATE_RANGE[0] else ALARM_HIGH if respiratory_rate > RESPIRATORY_RATE_RANGE[1] else ALARM_NORMAL
    
    # Body temperature check (Normal: 36.5-37.5°C)
    body_temp_color = ALARM_LOW if body_temp < TEMP_RANGE[0] else ALARM_HIGH if body_temp > TEMP_RANGE[1] else ALARM_NORMAL

    # Return a tuple of color codes for all vital signs
    return heart_rate_color, spo2_color, respiratory_rate_color, body_temp_color
