import numpy as np
from scipy.signal import find_peaks
from config import HEART_RATE_PARAMS  # Assuming we will load parameters from the config file

def calculate_heart_rate(signal, sampling_rate=None, peak_height_factor=None, min_peak_distance=None):
    """
    Calculates the heart rate from the given signal using peak detection.
    
    :param signal: ECG or PPG signal (list or numpy array)
    :param sampling_rate: Sampling rate of the signal in Hz
    :param peak_height_factor: The factor to determine the peak height threshold (relative to max signal amplitude)
    :param min_peak_distance: Minimum distance between peaks in samples
    :return: Estimated heart rate in bpm (beats per minute)
    """
    # Use default values from the config file if not provided
    if sampling_rate is None:
        sampling_rate = HEART_RATE_PARAMS['sampling_rate']
    if peak_height_factor is None:
        peak_height_factor = HEART_RATE_PARAMS['peak_height_factor']
    if min_peak_distance is None:
        min_peak_distance = HEART_RATE_PARAMS['min_peak_distance']
    
    # Find peaks (R-peaks for ECG or pulses for PPG)
    peaks, _ = find_peaks(signal, height=np.max(signal) * peak_height_factor, distance=sampling_rate * min_peak_distance)
    
    # Calculate the intervals between consecutive peaks (in seconds)
    peak_intervals = np.diff(peaks) / sampling_rate  # Convert to time intervals in seconds
    
    # Calculate the heart rate (beats per minute)
    if len(peak_intervals) == 0:
        return 0  # If no peaks are found, return 0 as the heart rate
    
    avg_interval = np.mean(peak_intervals)  # Average time between peaks
    heart_rate_bpm = 60 / avg_interval  # Convert to beats per minute
    
    return heart_rate_bpm
