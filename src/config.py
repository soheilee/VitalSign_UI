"""====================================================================================
                        ------->  Revision History  <------
====================================================================================

Date            Who         Ver         Changes
====================================================================================
11-Nov-24       SM          1000        Initial creation
===================================================================================="""


SAMPLING_RATE = 250
WINDOW_SIZE = 1000
DATA_DIR = "../data/"

COLORS = {
    "background": "black",
    "text": "white",
    "highlight": "red",
    "secondary": "lightblue",
    "warning": "yellow"
}
HEART_RATE_RANGE = (60, 100)  # Normal heart rate range: 60-100 bpm
SPO2_RANGE = (95, 100)  # Normal SpO2 range: 95-100%
RESPIRATORY_RATE_RANGE = (12, 20)  # Normal respiratory rate: 12-20 breaths per minute
TEMP_RANGE = (36.5, 37.5)  # Normal body temperature range: 36.5-37.5 °C

# Define alarm color codes for low and high threshold violations
ALARM_LOW = '#66ccff'  # Blue color for values below the normal range
ALARM_HIGH = '#ff6666'  # Red color for values above the normal range
ALARM_NORMAL = 'black'  # Black color for values within the normal range

# Configuration settings for heart rate calculation
HEART_RATE_PARAMS = {
    'sampling_rate': 250,  # Default sampling rate for ECG/PPG in Hz
    'peak_height_factor': 0.5,  # Height factor to determine peak threshold (50% of max signal amplitude)
    'min_peak_distance': 0.4  # Minimum distance between peaks in seconds (e.g., 0.4 seconds)
}