import RPi.GPIO as GPIO
import time
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import stepper
 
# Pins assignats al Stepper 1
pins_stepper1 = [18, 23, 24, 25]

# Pins assignats al Stepper 2
pins_stepper2 = [8, 7, 12, 16]

# Pins assignats als finals de carrera
finalCarrera1 = 8
finalCarrera2 = 7

# setting up
GPIO.setmode(GPIO.BCM)
GPIO.setup(pins_stepper1[0], GPIO.OUT)
GPIO.setup(pins_stepper1[1], GPIO.OUT)
GPIO.setup(pins_stepper1[2], GPIO.OUT)
GPIO.setup(pins_stepper1[3], GPIO.OUT)
GPIO.setup(pins_stepper2[0], GPIO.OUT)
GPIO.setup(pins_stepper2[1], GPIO.OUT)
GPIO.setup(pins_stepper2[2], GPIO.OUT)
GPIO.setup(pins_stepper2[3], GPIO.OUT)
GPIO.setup(finalCarrera1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(finalCarrera2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# initializing
stepper1 = stepper.stepperMotor(pins_stepper1)
stepper2 = stepper.stepperMotor(pins_stepper2)

n_graus = 45    # Graus a moure la càmera cada pas

step_count = int((stepper.max_step_count/360) * n_graus) 
camera = PiCamera()

# the meat
try:
    for j in range(int(360 / n_graus)):

        i = 0

        for i in range(step_count):

            status_finalCarrera1 = GPIO.input(finalCarrera1)
            status_finalCarrera2 = GPIO.input(finalCarrera2)

            if status_finalCarrera1 is True:    # Arribem al final del gir i sortim del bucle
                break
            else:
                stepper1.step()
                stepper2.step()

            time.sleep(stepper1.step_sleep)
        
        rawCapture = PiRGBArray(camera)
        
        time.sleep(0.1)

        camera.capture(rawCapture, format="bgr", use_video_port=True)
        image = rawCapture.array

        path = "/home/lasergaze/Desktop/img/image"+str(j)+".jpg"

        cv2.imwrite(path, image)
 
 
except KeyboardInterrupt:
    stepper1.cleanup()
    stepper2.cleanup()
    exit(1)
 
offset = j+1
stepper1.cleanup()
stepper2.cleanup()

exit(0)
