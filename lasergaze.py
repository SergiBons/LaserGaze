from stepper import StepperMotor
from read_from_arduino import Arduino
from camera import Camera
from points import *
import cloud_manager
import RPi.GPIO as GPIO
import time
import math

class Robot:

    def __init__(self):
        
        # Pins assignats al Stepper 1
        self.pins_stepper1 = [18, 23, 24, 25]

        # Pins assignats al Stepper 2
        self.pins_stepper2 = [8, 7, 12, 16]

        # Pins assignats als finals de carrera
        self.final_carrera1 = 17
        self.final_carrera2 = 27

        # Setting up pin states
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pins_stepper1[0], GPIO.OUT)
        GPIO.setup(self.pins_stepper1[1], GPIO.OUT)
        GPIO.setup(self.pins_stepper1[2], GPIO.OUT)
        GPIO.setup(self.pins_stepper1[3], GPIO.OUT)
        GPIO.setup(self.pins_stepper2[0], GPIO.OUT)
        GPIO.setup(self.pins_stepper2[1], GPIO.OUT)
        GPIO.setup(self.pins_stepper2[2], GPIO.OUT)
        GPIO.setup(self.pins_stepper2[3], GPIO.OUT)
        GPIO.setup(self.final_carrera1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.final_carrera2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Initializing motors
        self.stepper1 = StepperMotor(self.pins_stepper1)
        self.stepper2 = StepperMotor(self.pins_stepper2)

        # Initializing arduino obj
        self.arduino = Arduino()

        # Initializing camera obj
        self.camera = Camera()

        # Setting up default location, orientation and current state of the motors
        self.position = {'x': 0, 'y': 0, 'z': 0}
        self.orientation_of_x_vector = 0
        self.current_state = {'lambda': None, 'phi': None}  # lambda goes from 0 to 360, phi from 0 to -180

        self.points = []

    def localize_self(self):
        self.reset_arm_position()

        # Diagram of the movement
        # Angles:  0°   30°   60°   90°  120°  150°  180°  210°  240°  270°  300°  330°
        # ...... ......................................................................
        #   -30°: 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12
        #   -60°: 24 <- 23 <- 22 <- 21 <- 20 <- 19 <- 18 <- 17 <- 16 <- 15 <- 14 <- 13
        #   -90°: 25 -> 26 -> 27 -> 28 -> 29 -> 30 -> 31 -> 32 -> 33 -> 34 -> 35 -> 36
        #  -120°: 48 <- 47 <- 46 <- 45 <- 44 <- 43 <- 42 <- 41 <- 40 <- 39 <- 38 <- 37

        degrees_between_photos = 30  # Graus a moure la càmera entre fotos
        degrees_between_heights = -30  # Graus a moure la càmera entre altures

        h_stops = int(360 / abs(degrees_between_photos))
        v_stops = int(120 / abs(degrees_between_heights))

        virtual_h_state = 0
        virtual_v_state = 0

        anchor_1_found = False
        anchor_2_found = False
        anchor_1 = None
        anchor_2 = None

        for i in range(v_stops):
            virtual_v_state = virtual_v_state + degrees_between_heights
            self.go_to(virtual_h_state, virtual_v_state)
            for j in range(h_stops):
                if j != 0:
                    if (i % 2) == 0:
                        virtual_h_state = virtual_h_state + degrees_between_photos
                    else:
                        virtual_h_state = virtual_h_state - degrees_between_photos
                    self.go_to(virtual_h_state, virtual_v_state)
                
                n_photo = j + i * h_stops
                photo_path = "/home/lasergaze/Desktop/Repo/tmp/tmp" + str(n_photo) + ".jpg"
                self.camera.take_and_save_photo(photo_path)
                print(n_photo)
                # Enviar foto a buscar ancora
                # Rebre vector amb ancores
                # Si hi ha ancores transformar punt en angles
                # Anar a aquella configuració i mesurar la distancia
                # Guardar-se els angles i distancia

                anchor_1_found_ret, anchor_2_found_ret, anchor_1_ret, anchor_2_ret = cloud_manager.send_image_find_anchors(photo_path)

                img_config = self.current_state

                if anchor_1_found_ret and not anchor_1_found:
                    print("Num foto on s'ha trobat: " + str(n_photo))
                    new_lambda, new_phi = go_to_point(anchor_1_ret['x'], anchor_1_ret['y'], img_config['lambda'], img_config['phi'], self.camera.h_fov, self.camera.h_size, self.camera.v_size)
                    self.go_to(new_lambda, new_phi)
                    self.camera.take_and_save_photo("/home/lasergaze/Desktop/Repo/tmp/tmp_anchor_1.jpg")
                    dist = self.arduino.get_data()
                    anchor_1 = {'dist': dist, 'lambda': self.current_state['lambda'], 'phi': self.current_state['phi']}
                    
                    anchor_1_found = True
                    print("Anchor 1 found first time. Dist: " + str(dist))

                if anchor_2_found_ret and not anchor_2_found:
                    print("Num foto on s'ha trobat: " + str(n_photo))
                    new_lambda, new_phi = go_to_point(anchor_2_ret['x'], anchor_2_ret['y'], img_config['lambda'], img_config['phi'], self.camera.h_fov, self.camera.h_size, self.camera.v_size)
                    self.go_to(new_lambda, new_phi)
                    self.camera.take_and_save_photo("/home/lasergaze/Desktop/Repo/tmp/tmp_anchor_2.jpg")
                    dist = self.arduino.get_data()
                    anchor_2 = {'dist': dist, 'lambda': self.current_state['lambda'], 'phi': self.current_state['phi']}
                    
                    anchor_2_found = True
                    print("Anchor 2 found first time. Dist: " + str(dist))

                if anchor_1_found and anchor_2_found:   # Sortir del bucle intern
                    break

            if anchor_1_found and anchor_2_found:   # Sortir del bucle extern
                break

        if anchor_1_found and anchor_2_found:
            x, y, z, orient = find_coord_self(anchor_1['lambda'], anchor_1['phi'], anchor_1['dist'],
                                      anchor_2['lambda'], anchor_2['phi'], anchor_2['dist'])
            self.position = {'x': x, 'y': y, 'z': z}
            self.orientation_of_x_vector = orient
        else:
            self.position = {'x': None, 'y': None, 'z': None}
            self.orientation_of_x_vector = None

        self.go_to(90, -90)

    def find_points_of_interest(self):
        self.reset_arm_position()

        # Diagram of the movement
        # Angles:  0°   30°   60°   90°  120°  150°  180°  210°  240°  270°  300°  330°
        # ...... ......................................................................
        #   -30°: 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12
        #   -60°: 24 <- 23 <- 22 <- 21 <- 20 <- 19 <- 18 <- 17 <- 16 <- 15 <- 14 <- 13
        #   -90°: 25 -> 26 -> 27 -> 28 -> 29 -> 30 -> 31 -> 32 -> 33 -> 34 -> 35 -> 36
        #  -120°: 48 <- 47 <- 46 <- 45 <- 44 <- 43 <- 42 <- 41 <- 40 <- 39 <- 38 <- 37

        degrees_between_photos = 30  # Graus a moure la càmera entre fotos
        degrees_between_heights = -30    # Graus a moure la càmera entre altures

        h_stops = int(360/abs(degrees_between_photos))
        v_stops = int(120/abs(degrees_between_heights))

        to_vist = []
        virtual_h_state = 0
        virtual_v_state = 0
        for i in range(v_stops):
            virtual_v_state = virtual_v_state + degrees_between_heights
            self.go_to(virtual_h_state, virtual_v_state)
            for j in range(h_stops):
                if j != 0:
                    if (i % 2) == 0:
                        virtual_h_state = virtual_h_state + degrees_between_photos
                    else:
                        virtual_h_state = virtual_h_state - degrees_between_photos
                    self.go_to(virtual_h_state, virtual_v_state)

                n_photo = j + i * h_stops
                
                print("i: " + str(i) + " j: " + str(j))
                self.camera.take_and_save_photo("/home/lasergaze/Desktop/Repo/img/image" + str(n_photo) + ".jpg")

                # Enviar foto
                # Rebre array de punts
                # Transformar punts a angles
                # Afegir-los al array de angles a "visitar"
                # TO DO

        # Example angles for now
        to_vist.append([110, -30])
        to_vist.append([270, -110])
        to_vist.append([180, -90])

        for angles in to_vist:
            self.go_to(angles[0], angles[1])
            dist = self.arduino.get_data()
            #point = create_point(dist, self.current_state, self.position, self.orientation_of_x_vector)

    def take_wide_barrage_of_points(self):
        self.reset_arm_position()

        degrees_between_heights = -1  # Graus a moure la càmera entre altures
        v_stops = int(120 / abs(degrees_between_heights))

        virtual_h_state = 0
        virtual_v_state = 0
        n_img_max = 360
        print("v_stops: " + str(v_stops))
        for i in range(v_stops):

            virtual_v_state = virtual_v_state + degrees_between_heights
            self.go_to(virtual_h_state, virtual_v_state)
            h_stops = int(math.sin(math.radians(abs(virtual_v_state))) * n_img_max)
            degrees_between_photos = 360/h_stops  # Graus a moure la càmera entre fotos
            print("h_stops: " + str(h_stops))
            for j in range(h_stops):
                if j != 0:
                    if (i % 2) == 0:
                        virtual_h_state = virtual_h_state + degrees_between_photos
                    else:
                        virtual_h_state = virtual_h_state - degrees_between_photos
                    self.go_to(virtual_h_state, virtual_v_state)
                else:
                    if (i % 2) == 0:
                        virtual_h_state = 0
                    else:
                        virtual_h_state = 359
                    self.go_to(virtual_h_state, virtual_v_state)

                time.sleep(0.2)
                dist = self.arduino.get_data()
                print("Lambda: " + str(self.current_state['lambda']) + " Phi: " + str(self.current_state['phi']) + " Dist: " + str(dist))
                point = create_point(dist, self.current_state['lambda'], self.current_state['phi'], self.position['x'], self.position['y'], self.position['z'], self.orientation_of_x_vector)
                self.points.append(point)

        self.go_to(90, -90)

    def reset_arm_position(self):
        self.stepper1.direction = False
        self.stepper2.direction = True
        i = 0
        for i in range(self.stepper1.max_step_count):
            status_final_carrera1 = GPIO.input(self.final_carrera1)
            if status_final_carrera1:  # Arribem al final del gir i sortim del bucle
                break
            else:
                self.stepper1.step()
            time.sleep(self.stepper1.step_sleep)
        i = 0
        for i in range(self.stepper2.max_step_count):
            status_final_carrera2 = GPIO.input(self.final_carrera2)
            if status_final_carrera2:  # Arribem al final del gir i sortim del bucle
                break
            else:
                self.stepper2.step()
            time.sleep(self.stepper2.step_sleep)

        self.stepper1.direction = True
        self.stepper2.direction = False

        self.current_state['lambda'] = 0.0
        self.current_state['phi'] = 0.0

    def go_to(self, new_lambda, new_phi):
        if new_lambda < 0.0 or new_lambda > 359 or new_phi > 0.0 or new_phi < -180.0:
            raise Exception("Illegal new state of motors: Lambda: " + str(new_lambda) + " Phi: " + str(new_phi))

        inc_lambda = new_lambda - self.current_state['lambda']
        inc_phi = new_phi - self.current_state['phi']

        dir_stepper1 = True
        if inc_lambda < 0:
            dir_stepper1 = False

        dir_stepper2 = False
        if inc_phi > 0:
            dir_stepper2 = True

        steps_stepper1, real_inc_lambda = self.stepper1.degree_to_steps(inc_lambda)
        steps_stepper2, real_inc_phi = self.stepper2.degree_to_steps(inc_phi)

        self.stepper1.do_n_steps(steps_stepper1, dir_stepper1)
        self.current_state['lambda'] = self.current_state['lambda'] + real_inc_lambda

        self.stepper2.do_n_steps(steps_stepper2, dir_stepper2)
        self.current_state['phi'] = self.current_state['phi'] + real_inc_phi
    
    def print_points_to_file(self, file_path="/home/lasergaze/Desktop/Repo/points/test"):
        file = open(file_path, 'w')
        for i in range(len(self.points)):
            file.write(str(self.points[i]['x']) + ',' + str(self.points[i]['y']) + ',' + str(self.points[i]['z']) + '\n')
    
    def cleanup(self):
        self.stepper1.cleanup()
        self.stepper2.cleanup()
        GPIO.cleanup()
