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
        """
        sets up all the required attributes of the class and initializes the pins where the motor is wired to.

        @param pin_list: List of 4 integers with the pins where the motor is wired to.
        """
        self.pins = [pin_list[0], pin_list[1], pin_list[2], pin_list[3]]
        self.step_counter = 0

        self.step_sleep = 0.001        # careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
        self.max_step_count = 4096     # 5.625*(1/64) per step, 4096 steps is 360°
        self.direction = True         # True for counter_clockwise, False for clockwise
        self.initialize()

    def initialize(self):
        """
        Initializes the pins where the motor is wired to.
        """

        GPIO.output(self.pins[0], GPIO.LOW)
        GPIO.output(self.pins[1], GPIO.LOW)
        GPIO.output(self.pins[2], GPIO.LOW)
        GPIO.output(self.pins[3], GPIO.LOW)

    def cleanup(self):
        """
         Cleans up the pins where the motor is wired to.
        """

        GPIO.output(self.pins[0], GPIO.LOW)
        GPIO.output(self.pins[1], GPIO.LOW)
        GPIO.output(self.pins[2], GPIO.LOW)
        GPIO.output(self.pins[3], GPIO.LOW)

    def step(self):
        """
        Performs one step in the direction that self.direction is set.
        """

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
        """
        Receive a number of degrees and returns those transformed to how many steps does it take to travel to the
        closest point to that angle + the real angle that those steps would travel.

        @param degrees: Degree to be transformed to steps of this motor.
        @return: Steps to travels said angle, the real angle traveled by the steps that are being returned.
        """

        steps = int((self.max_step_count / 360) * abs(degrees))
        real_degree = (360/self.max_step_count) * steps
        if degrees < 0:
            real_degree = real_degree * -1
        return [steps, real_degree]

    def do_n_steps(self, n_steps, counter_clockwise=None):
        """
        Does a number of steps in the specified direction.

        @param n_steps: Steps to do.
        @param counter_clockwise: Direction to do the steps to. True counter-clockwise, False clock-wise.
        """

        if counter_clockwise is not None:
            self.direction = counter_clockwise
        for i in range(n_steps):
            self.step()
            time.sleep(self.step_sleep)
