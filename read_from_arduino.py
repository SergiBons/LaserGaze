import serial
import time


class Arduino:
    
    def __init__(self, serial_port="/dev/ttyUSB0"):
        """
        Initializes the serial communication.

        @param serial_port: Object to where to listen for serial communications.
        """
        self._ser = serial.Serial(serial_port, 9600, timeout=5)
        if not self._ser.is_open:
            self._ser.open()

    def get_data(self):
        """
        Performs 4 lectures, discards the first one as it may be cut in half, and returns the mode of the other 3
        in order to avoid errors.

        @return: distance read by the TfMini LIDAR.
        """

        time0 = time.time()
        self._ser.reset_input_buffer()
        count = 0
        buffer = []
        while True:
            if time.time() > time0 + 5:
                break
            if self._ser.in_waiting > 5:
                if count > 0:
                    buffer.append(int(self._ser.readline().decode('utf-8').rstrip()))
                    if count >= 3:
                        break
                else:
                    self._ser.readline()
                count = count + 1
        if len(buffer) != 3:
            return -1
        buffer.sort()
        return buffer[1]

    def print_thread(self):
        """
        Constantly prints the distances that the TfMini LIDAR is reading.
        """

        distance = '-1'
        time0 = time.time()
        self._ser.reset_input_buffer()
        while True:
            if self._ser.in_waiting > 0:
                distance = self._ser.readline().decode('utf-8').rstrip()
                print(distance)

    def print_thread_to_file(self, file_path="dist"):
        """
        Constantly prints the distances that the TfMini LIDAR is reading to a file.

        @param file_path: File to print the distance to.
        """

        distance = '-1'
        self._ser.reset_input_buffer()
        while True:
            if self._ser.in_waiting > 0:
                distance = self._ser.readline().decode('utf-8').rstrip()
                f = open(file_path, 'w')
                f.write(distance)
                f.close
                