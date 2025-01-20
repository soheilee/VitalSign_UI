import time
import pandas as pd
import collections
import serial
from set_GUI import *

DEBUG = False
class Constants:
    port = 'COM9'
    baud_rate = 9600
    sampling_rate = 500
    window_size = 5*sampling_rate

class Farzad(Soheil):
    def __init__(self):
        super().__init__()
        self.ecg_filtered = []
        self.ppg_filtered = []
        if DEBUG:
            self.ser = serial.Serial(Constants.port, Constants.baud_rate, write_timeout=0)
            self.ser.close()
            self.ser.open()
        else:
            ecg_df = pd.read_csv('../data/ECG.csv', header=None, names=['ECG'])
            ppg_df = pd.read_csv('../data/PPG.csv', header=None, names=['PPG'])
            self.ecg_array = ecg_df.to_numpy().reshape(-1)
            self.ppg_array = ppg_df.to_numpy().reshape(-1)
            self.ecg_idx = 0
            self.ppg_idx = 0

        self.data_buffer = collections.deque(maxlen=Constants.window_size)
        self.xticks = collections.deque(maxlen=Constants.window_size)
        self.ecg_buffer = collections.deque(maxlen=Constants.window_size)
        self.ppg_buffer = collections.deque(maxlen=Constants.window_size)

        self.xplot_idx = 0
        # self.setup_callbacks(self.ecg_filtered, self.ppg_filtered)

    def run_farzad(self):
        while True:
            if DEBUG:
                line = self.ser.read(self.ser.in_waiting).decode('utf-8').strip()
                if line:
                    self.data_buffer.append(float(line))
                    if len(self.xticks) == 0:
                        last_tick = 0
                    else:
                        last_tick = self.xticks[-1] + 1 / Constants.sampling_rate
                    self.xticks.append(last_tick)
                    # Todo filter self.ecg_filtered
            else:
                if len(self.xticks) == 0:
                    last_tick = 0
                else:
                    last_tick = self.xticks[-1] + 1 / Constants.sampling_rate
                self.xticks.append(last_tick)
                self.ecg_buffer.append(self.ecg_array[self.ecg_idx])
                self.ppg_buffer.append(self.ppg_array[self.ppg_idx])
                self.ecg_idx = (self.ecg_idx + 1) % len(self.ecg_array)
                self.ppg_idx = (self.ppg_idx + 1) % len(self.ppg_array)
                self.ecg_filtered = list(self.ecg_buffer)
                self.ppg_filtered = list(self.ppg_buffer)
                self.ecg = self.ecg_filtered
                self.ppg = self.ppg_filtered
                time.sleep(0.01)