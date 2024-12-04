# alarm_engine.py

# Define threshold ranges for vital signs
HEART_RATE_RANGE = (60, 140)  # Normal heart rate range: 60-100 bpm
SPO2_RANGE = (95, 100)  # Normal SpO2 range: 95-100%
RESPIRATORY_RATE_RANGE = (12, 20)  # Normal respiratory rate: 12-20 breaths per minute
TEMP_RANGE = (36.5, 37.5)  # Normal body temperature range: 36.5-37.5 °C

def check_vital_signs(heart_rate, spo2, respiratory_rate, body_temp):
    """
    This function checks if each vital sign is within its normal range.
    It returns the color (blue, red, or black) for each vital sign based on whether 
    it falls below or above the normal range.
    """
    # Check if each vital sign is below or above the normal range
    heart_rate_color = '#66ccff' if heart_rate < HEART_RATE_RANGE[0] else '#ff6666' if heart_rate > HEART_RATE_RANGE[1] else 'black'
    spo2_color = '#66ccff' if spo2 < SPO2_RANGE[0] else '#ff6666' if spo2 > SPO2_RANGE[1] else 'black'
    respiratory_rate_color = '#66ccff' if respiratory_rate < RESPIRATORY_RATE_RANGE[0] else '#ff6666' if respiratory_rate > RESPIRATORY_RATE_RANGE[1] else 'black'
    body_temp_color = '#66ccff' if body_temp < TEMP_RANGE[0] else '#ff6666' if body_temp > TEMP_RANGE[1] else 'black'

    return heart_rate_color, spo2_color, respiratory_rate_color, body_temp_color