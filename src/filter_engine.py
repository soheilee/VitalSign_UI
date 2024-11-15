from scipy.signal import butter, filtfilt
import numpy as np

def low_pass_filter(signal, cutoff_freq, sampling_rate, order=4, padding=True):
    """
    Apply a low-pass filter to the signal.
    
    Parameters:
        signal (array-like): The input signal.
        cutoff_freq (float): The cutoff frequency of the low-pass filter in Hz.
        sampling_rate (float): The sampling rate of the signal in Hz.
        order (int): The order of the Butterworth filter.
        padding (bool): Whether to apply edge padding to reduce edge effects.
    
    Returns:
        np.ndarray: The filtered signal.
    """
    nyquist = 0.5 * sampling_rate
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)

    if padding:
        pad_len = 3 * max(len(b), len(a))
        padded_signal = np.concatenate([signal[pad_len - 1::-1], signal, signal[:-pad_len - 1:-1]])
        filtered_signal = filtfilt(b, a, padded_signal)
        return filtered_signal[pad_len:-pad_len]
    else:
        return filtfilt(b, a, signal)
