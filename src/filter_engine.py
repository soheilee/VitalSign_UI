"""====================================================================================
                        ------->  Revision History  <------
====================================================================================

Date            Who         Ver         Changes
====================================================================================
11-Nov-24       SM          1000        Initial creation
===================================================================================="""


from scipy.signal import butter, filtfilt  # Importing necessary functions for filtering from scipy.signal
import numpy as np  # Importing numpy for array manipulation and numerical operations

def low_pass_filter(signal, cutoff_freq, sampling_rate, order=4, padding=True):
    """
    Applies a low-pass Butterworth filter to a signal.

    Parameters:
    - signal (array-like): The input signal to be filtered.
    - cutoff_freq (float): The cutoff frequency for the low-pass filter in Hz.
    - sampling_rate (float): The sampling rate of the signal in Hz.
    - order (int, optional): The order of the filter, default is 4.
    - padding (bool, optional): Whether to apply signal padding to reduce edge effects, default is True.

    Returns:
    - filtered_signal (array): The filtered signal after applying the low-pass filter.
    """
    
    # Calculate the Nyquist frequency (half of the sampling rate)
    nyquist = 0.5 * sampling_rate

    # Normalize the cutoff frequency by the Nyquist frequency
    normal_cutoff = cutoff_freq / nyquist

    # Design the Butterworth filter using the given order and normalized cutoff frequency
    # 'b' and 'a' are the filter coefficients
    b, a = butter(order, normal_cutoff, btype='low', analog=False)

    # If padding is requested, pad the signal to minimize edge effects of the filter
    if padding:
        # Calculate the length of the padding based on the filter order
        pad_len = 3 * max(len(b), len(a))

        # Pad the signal by mirroring the beginning and end of the signal
        padded_signal = np.concatenate([signal[pad_len - 1::-1], signal, signal[:-pad_len - 1:-1]])

        # Apply the filter to the padded signal
        filtered_signal = filtfilt(b, a, padded_signal)

        # Return the filtered signal after removing the padding
        return filtered_signal[pad_len:-pad_len]

    # If no padding is requested, apply the filter directly to the original signal
    else:
        return filtfilt(b, a, signal)
