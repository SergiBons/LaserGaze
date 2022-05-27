import serial
import time


class TfMini():

    def __init__(self, serial_port="/dev/ttyS0"):

        self._ser = serial.Serial(serial_port, 115200)
        if self._ser.is_open == False:
            self._ser.open()

        self._distance = 0
        self.distance_min = 10
        self.distance_max = 1200

    def get_data(self):

        time0 = time.time()
        distance = -1
        while True:
            count = self._ser.in_waiting
            if time.time() > time0 + 5: break
            if count > 8:
                recv = self._ser.read(9)
                self._ser.reset_input_buffer()
                if recv[0] == 0x59 and recv[1] == 0x59:  # 0x59 is 'Y'
                    distance = recv[2] + recv[3] * 256
                    self._ser.reset_input_buffer()
                    break

        self._distance = distance
        return (distance)
    
    @property
    def distance(self):
        return (self._distance)

    def print_data_thread(self):
        dist = 10
        while dist >= 5:
            dist = self.get_data()
            print(dist)

    def close(self):
        if self._ != None:
            self._ser.close()
