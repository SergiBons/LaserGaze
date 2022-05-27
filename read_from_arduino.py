import serial
import time


class Arduino:
    
    def __init__(self, serial_port="/dev/ttyUSB0"):
        self._ser = serial.Serial(serial_port, 9600, timeout=5)
        if not self._ser.is_open:
            self._ser.open()

    def get_data(self):
        distance = '-1'
        time0 = time.time()
        self._ser.reset_input_buffer()
        count = 0
        while True:
            if time.time() > time0 + 5:
                break
            if self._ser.in_waiting > 5:
                if count > 0:
                    distance = self._ser.readline().decode('utf-8').rstrip()
                    break
                else:
                    self._ser.readline()
                    count = count + 1
        
        return int(distance)

    def print_thread(self):
        distance = '-1'
        time0 = time.time()
        self._ser.reset_input_buffer()
        while True:
            if self._ser.in_waiting > 0:
                distance = self._ser.readline().decode('utf-8').rstrip()
                print(distance)

    def print_thread_to_file(self, file_path="dist"):
        distance = '-1'
        self._ser.reset_input_buffer()
        while True:
            if self._ser.in_waiting > 0:
                distance = self._ser.readline().decode('utf-8').rstrip()
                f = open(file_path, 'w')
                f.write(distance)
                f.close
                