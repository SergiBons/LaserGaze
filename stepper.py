import RPi.GPIO as GPIO
import time

# defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
step_sequence = [[1, 0, 0, 1],
                 [1, 0, 0, 0],
                 [1, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 1, 0],
                 [0, 0, 1, 0],
                 [0, 0, 1, 1],
                 [0, 0, 0, 1]]


class StepperMotor:

    def __init__(self, pin_list):

        self.pins = [pin_list[0], pin_list[1], pin_list[2], pin_list[3]]
        self.step_counter = 0

        self.step_sleep = 0.001        # careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
        self.max_step_count = 4096     # 5.625*(1/64) per step, 4096 steps is 360°
        self.direction = True         # True for counter_clockwise, False for clockwise

        self.initialize()

    def initialize(self):
        GPIO.output(self.pins[0], GPIO.LOW)
        GPIO.output(self.pins[1], GPIO.LOW)
        GPIO.output(self.pins[2], GPIO.LOW)
        GPIO.output(self.pins[3], GPIO.LOW)

    def cleanup(self):
        GPIO.output(self.pins[0], GPIO.LOW)
        GPIO.output(self.pins[1], GPIO.LOW)
        GPIO.output(self.pins[2], GPIO.LOW)
        GPIO.output(self.pins[3], GPIO.LOW)

    def step(self):
        for pin in range(0, len(self.pins)):
            GPIO.output(self.pins[pin], step_sequence[self.step_counter][pin])
        if self.direction:
            self.step_counter = (self.step_counter - 1) % 8
        elif not self.direction:
            self.step_counter = (self.step_counter + 1) % 8
        else:   # defensive programming
            print("uh oh... direction should *always* be either True or False")
            self.cleanup()
            exit(1)

    def degree_to_steps(self, degrees):
        steps = int((self.max_step_count / 360) * abs(degrees))
        real_degree = (360/self.max_step_count) * steps
        if degrees < 0:
            real_degree = real_degree * -1
        return [steps, real_degree]

    def do_n_steps(self, n_steps, counter_clockwise=None):
        if counter_clockwise is not None:
            self.direction = counter_clockwise
        for i in range(n_steps):
            self.step()
            time.sleep(self.step_sleep)
