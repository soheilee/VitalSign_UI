# heart_rate_engine.py
import numpy as np
from scipy.signal import find_peaks

def calculate_heart_rate(signal, sampling_rate=250):
    """
    Calculates the heart rate from the given signal using peak detection.
    
    :param signal: ECG or PPG signal (list or numpy array)
    :param sampling_rate: Sampling rate of the signal in Hz (default is 1000 Hz)
    :return: Estimated heart rate in bpm (beats per minute)
    """
    # Find peaks (R-peaks for ECG or pulses for PPG)
    peaks, _ = find_peaks(signal, height=np.max(signal)*0.5, distance=sampling_rate*0.4)  # Detect peaks
    
    # Calculate the intervals between consecutive peaks (in seconds)
    peak_intervals = np.diff(peaks) / sampling_rate  # Convert to time intervals in seconds
    
    # Calculate the heart rate (beats per minute)
    if len(peak_intervals) == 0:
        return 0  # If no peaks are found, return 0 as the heart rate
    
    avg_interval = np.mean(peak_intervals)  # Average time between peaks
    heart_rate_bpm = 60 / avg_interval  # Convert to beats per minute
    
    return heart_rate_bpm