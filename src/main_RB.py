from concurrent import futures
import sys
import webbrowser
from get_data import *

class MainOP(Farzad):
    def __init__(self):
        super().__init__()
        self.app.layout = self.create_layout()
        self.setup_callbacks()
        webbrowser.open('http://127.0.0.1:8050/')

        with futures.ThreadPoolExecutor() as executor:
            executor.submit(self.run_farzad)
            executor.submit(self.run_soheil)

if __name__ == '__main__':
    sys.exit(MainOP())
