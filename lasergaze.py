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
        """
        Sets up all data structures needed, and the components of the robot.
        """

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

    def quick_static_scan(self, n_img_max=None, degrees_between_heights=None):
        """
        Prepares a new scan, performs a wide barrage of points scan, and finishes the scan uploading the results to the
        cloud storage.

        @param n_img_max: Maximum number of images to take in a height in the wide barrage of points scan.
        @param degrees_between_heights: Degrees between each height the wide barrage of points scan will scan.
        """

        self.prepare_new_scan()
        if n_img_max is None and degrees_between_heights is None:
            self.take_wide_barrage_of_points()
        else:
            self.take_wide_barrage_of_points(n_img_max=n_img_max, degrees_between_heights=degrees_between_heights)
        self.finish_scan()

    def complete_static_scan(self, n_img_max=None, degrees_between_heights=None):
        """
        Prepares a new scan, performs a points of interest scan, a wide barrage of points scan, and finishes the scan
        uploading the results to the cloud storage.

        @param n_img_max: Maximum number of images to take in a height in the wide barrage of points scan.
        @param degrees_between_heights: Degrees between each height the wide barrage of points scan will scan.
        """

        self.prepare_new_scan()
        self.find_points_of_interest()
        if n_img_max is None and degrees_between_heights is None:
            self.take_wide_barrage_of_points(needs_reset=False)
        else:
            self.take_wide_barrage_of_points(needs_reset=False, n_img_max=n_img_max, degrees_between_heights=degrees_between_heights)
        self.finish_scan()

    def quick_mobile_scan(self, n_img_max=None, degrees_between_heights=None):
        """
        Performs a wide barrage of points scan.

        @param n_img_max: Maximum number of images to take in a height in the wide barrage of points scan.
        @param degrees_between_heights: Degrees between each height the wide barrage of points scan will scan.
        """

        self.localize_self()
        if n_img_max is None and degrees_between_heights is None:
            self.take_wide_barrage_of_points()
        else:
            self.take_wide_barrage_of_points(n_img_max=n_img_max, degrees_between_heights=degrees_between_heights)

    def complete_mobile_scan(self, n_img_max=None, degrees_between_heights=None):
        """
        Performs a points of interest scann and a wide barrage of points scan.

        @param n_img_max: Maximum number of images to take in a height in the wide barrage of points scan.
        @param degrees_between_heights: Degrees between each height the wide barrage of points scan will scan.
        """

        self.localize_self_and_find_points_of_interest()
        if n_img_max is None and degrees_between_heights is None:
            self.take_wide_barrage_of_points(needs_reset=False)
        else:
            self.take_wide_barrage_of_points(needs_reset=False, n_img_max=n_img_max, degrees_between_heights=degrees_between_heights)

    def prepare_new_scan(self):
        """
        Clears the already created points stored in the points file.
        """
        clear_points_file()

    def finish_scan(self):
        """
        Upload the created points stored in the points file to the storage.
        """
        cloud_manager.upload_points(points_file_path)

    def localize_self(self, radius_anchor_1=5, radius_anchor_2=5):
        """
        Take 48 photos following the diagram, calling to a cloud function to through computer vision, find the anchors
        in them, transform theirs in image position to angles for the motor to go, points at that direction and measures
        the distance. Once both anchors have been found, triangulates the position and orientation of the robot on the
        coordinate system that puts the 0,0,0 at the position of the anchor 1, and the x vector pointing towards the
        anchor 2.

        @param radius_anchor_1: Radius of the anchor 1. To be added to the distance measured to surface of said anchor
        to find it's center.
        @param radius_anchor_2: Radius of the anchor 2. To be added to the distance measured to surface of said anchor
        to find it's center.
        """

        # Diagram of the movement
        # Angles:  0°   30°   60°   90°  120°  150°  180°  210°  240°  270°  300°  330°
        # ...... ......................................................................
        #   -30°: 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12
        #   -60°: 24 <- 23 <- 22 <- 21 <- 20 <- 19 <- 18 <- 17 <- 16 <- 15 <- 14 <- 13
        #   -90°: 25 -> 26 -> 27 -> 28 -> 29 -> 30 -> 31 -> 32 -> 33 -> 34 -> 35 -> 36
        #  -120°: 48 <- 47 <- 46 <- 45 <- 44 <- 43 <- 42 <- 41 <- 40 <- 39 <- 38 <- 37

        self.reset_arm_position()

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
                photo_path = "./img/image" + str(n_photo) + ".jpg"
                self.camera.take_and_save_photo(photo_path)
                
                # Enviar foto a buscar ancora
                # Rebre vector amb ancores
                # Si hi ha ancores transformar punt en angles
                # Anar a aquella configuració i mesurar la distancia
                # Guardar-se els angles i distancia

                anchor_1_found_ret, anchor_2_found_ret, anchor_1_ret, anchor_2_ret = cloud_manager.send_image_find_anchors(photo_path)

                img_config = self.current_state

                if anchor_1_found_ret and not anchor_1_found:
                    new_lambda, new_phi = image_point_to_angle_config(anchor_1_ret['x'], anchor_1_ret['y'], img_config['lambda'], img_config['phi'], self.camera.h_fov, self.camera.h_size, self.camera.v_size)
                    self.go_to(new_lambda, new_phi)
                    self.camera.take_and_save_photo("./tmp/tmp_anchor_1.jpg")
                    dist = self.arduino.get_data() + radius_anchor_1
                    anchor_1 = {'dist': dist, 'lambda': self.current_state['lambda'], 'phi': self.current_state['phi']}
                    anchor_1_found = True
                    print("Anchor 1 found. Dist: " + str(dist))

                if anchor_2_found_ret and not anchor_2_found:
                    new_lambda, new_phi = image_point_to_angle_config(anchor_2_ret['x'], anchor_2_ret['y'], img_config['lambda'], img_config['phi'], self.camera.h_fov, self.camera.h_size, self.camera.v_size)
                    self.go_to(new_lambda, new_phi)
                    self.camera.take_and_save_photo("./tmp/tmp_anchor_2.jpg")
                    dist = self.arduino.get_data() + radius_anchor_2
                    anchor_2 = {'dist': dist, 'lambda': self.current_state['lambda'], 'phi': self.current_state['phi']}
                    anchor_2_found = True
                    print("Anchor 2 found. Dist: " + str(dist))

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
        """
        Performs a points of interest scan.
        Takes 48 photos following the diagram and for each one, calls a cloud function that through computer vision
        finds the points of interest. It then transforms this in image points to angles for the motors to go later on.
        Once this whole process finishes, points towards the directions saved before, and measures the distance,
        creating with the information of where was the robot pointing, the position of the robot in the space, and it's
        orientation, a 3-dimensional point. Once all the saved directions have been scanned, stores the created points
        to the points file.
        """

        # Diagram of the movement
        # Angles:  0°   30°   60°   90°  120°  150°  180°  210°  240°  270°  300°  330°
        # ...... ......................................................................
        #   -30°: 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12
        #   -60°: 24 <- 23 <- 22 <- 21 <- 20 <- 19 <- 18 <- 17 <- 16 <- 15 <- 14 <- 13
        #   -90°: 25 -> 26 -> 27 -> 28 -> 29 -> 30 -> 31 -> 32 -> 33 -> 34 -> 35 -> 36
        #  -120°: 48 <- 47 <- 46 <- 45 <- 44 <- 43 <- 42 <- 41 <- 40 <- 39 <- 38 <- 37

        self.reset_arm_position()

        degrees_between_photos = 30  # Graus a moure la càmera entre fotos
        degrees_between_heights = -30    # Graus a moure la càmera entre altures

        h_stops = int(360/abs(degrees_between_photos))
        v_stops = int(120/abs(degrees_between_heights))

        to_visit = []
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
                
                photo_path = "./img/image" + str(n_photo) + ".jpg"
                self.camera.take_and_save_photo(photo_path)

                # Enviar foto
                # Rebre array de punts
                # Transformar punts a angles
                # Afegir-los al array de angles a "visitar"

                image_points = cloud_manager.send_image_find_interesting_points(photo_path)

                for image_point in image_points:
                    normalized_x = image_point['x'] / self.camera.h_size
                    noramlized_y = image_point['y'] / self.camera.v_size
                    new_lambda, new_phi = image_point_to_angle_config(normalized_x, noramlized_y, self.current_state['lambda'], self.current_state['phi'], self.camera.h_fov, self.camera.h_size, self.camera.v_size)
                    to_visit.append([new_lambda, new_phi])

        self.__scan_specific_angles(to_visit)

        self.go_to(90, -90)

    def localize_self_and_find_points_of_interest(self, radius_anchor_1=5, radius_anchor_2=5):
        """
        Takes 48 fotos following the diagram and for each, calls cloud functions to both fins the anchors and find the
        points of interest. If the anchors are found, transform theirs in image position to angles for the motor to go,
        points at that direction, and measures the distance. For the points of interest, their in image position is
        transformed to angles for the motors to go later on.
        Once this process finishes, if both anchors have been found, triangulates the position and orientation of the
        robot on the coordinate system that puts the 0,0,0 at the position of the anchor 1, and the x vector pointing
        towards the anchor 2.
        Also, points towards the directions saved before, and measures the distance, creating with the information of
        where was the robot pointing, the position of the robot in the space, and it's orientation, a 3-dimensional
        point. Once all the saved directions have been scanned, stores the created points to the points file.

        @param radius_anchor_1: Radius of the anchor 1. To be added to the distance measured to surface of said anchor
        to find it's center.
        @param radius_anchor_2: Radius of the anchor 2. To be added to the distance measured to surface of said anchor
        to find it's center.
        """

        # Diagram of the movement
        # Angles:  0°   30°   60°   90°  120°  150°  180°  210°  240°  270°  300°  330°
        # ...... ......................................................................
        #   -30°: 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12
        #   -60°: 24 <- 23 <- 22 <- 21 <- 20 <- 19 <- 18 <- 17 <- 16 <- 15 <- 14 <- 13
        #   -90°: 25 -> 26 -> 27 -> 28 -> 29 -> 30 -> 31 -> 32 -> 33 -> 34 -> 35 -> 36
        #  -120°: 48 <- 47 <- 46 <- 45 <- 44 <- 43 <- 42 <- 41 <- 40 <- 39 <- 38 <- 37

        self.reset_arm_position()

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
        to_visit = []
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
                photo_path = "./img/image" + str(n_photo) + ".jpg"
                self.camera.take_and_save_photo(photo_path)
                img_config = self.current_state

                anchor_1_found_ret, anchor_2_found_ret, anchor_1_ret, anchor_2_ret, image_points = cloud_manager.send_image_find_anchors_and_find_interesting_points(photo_path, anchor_1_found, anchor_2_found)

                for image_point in image_points:
                    normalized_x = image_point['x'] / self.camera.h_size
                    noramlized_y = image_point['y'] / self.camera.v_size
                    new_lambda, new_phi = image_point_to_angle_config(normalized_x, noramlized_y, self.current_state['lambda'], self.current_state['phi'], self.camera.h_fov, self.camera.h_size, self.camera.v_size)
                    to_visit.append([new_lambda, new_phi])

                if anchor_1_found_ret and not anchor_1_found:
                    new_lambda, new_phi = image_point_to_angle_config(anchor_1_ret['x'], anchor_1_ret['y'],
                                                                      img_config['lambda'], img_config['phi'],
                                                                      self.camera.h_fov, self.camera.h_size,
                                                                      self.camera.v_size)
                    self.go_to(new_lambda, new_phi)
                    self.camera.take_and_save_photo("./tmp/tmp_anchor_1.jpg")
                    dist = self.arduino.get_data() + radius_anchor_1
                    anchor_1 = {'dist': dist, 'lambda': self.current_state['lambda'],
                                'phi': self.current_state['phi']}
                    anchor_1_found = True
                    print("Anchor 1 found. Dist: " + str(dist))

                if anchor_2_found_ret and not anchor_2_found:
                    new_lambda, new_phi = image_point_to_angle_config(anchor_2_ret['x'], anchor_2_ret['y'],
                                                                      img_config['lambda'], img_config['phi'],
                                                                      self.camera.h_fov, self.camera.h_size,
                                                                      self.camera.v_size)
                    self.go_to(new_lambda, new_phi)
                    self.camera.take_and_save_photo("./tmp/tmp_anchor_2.jpg")
                    dist = self.arduino.get_data() + radius_anchor_2
                    anchor_2 = {'dist': dist, 'lambda': self.current_state['lambda'],
                                'phi': self.current_state['phi']}
                    anchor_2_found = True
                    print("Anchor 2 found. Dist: " + str(dist))

        if anchor_1_found and anchor_2_found:
            x, y, z, orient = find_coord_self(anchor_1['lambda'], anchor_1['phi'], anchor_1['dist'],
                                              anchor_2['lambda'], anchor_2['phi'], anchor_2['dist'])
            self.position = {'x': x, 'y': y, 'z': z}
            self.orientation_of_x_vector = orient
        else:
            self.position = {'x': 0, 'y': 0, 'z': 0}
            self.orientation_of_x_vector = 0

        self.__scan_specific_angles(to_visit)

        self.go_to(90, -90)

    def take_wide_barrage_of_points(self, n_img_max=180, degrees_between_heights=-2, needs_reset=True):
        """
        Moves doing zig-zag from 0° to -120° in vertical, and from 0° to 360° in horizontal, stopping, and
        taking a measure of the distance to create a 3-dimensional point in base to that distance, to where is pointing
        the robot, its positioning the space and its orientation. The heights at which the robot will do an horizontal
        line scanning distances is determined by degrees_between_heights, and how many points creates at which height
        is determined using a function of sinus and n_img_max. Once finished, stores the created points in the
        points file.

        @param n_img_max: Number of scans that will be performed in the -90° height (the height at which more scans are
        performed). It will be used in the following manner: sin(vertical position) *  n_img_max.
        @param degrees_between_heights: Number of degrees between each zig-zag.
        @param needs_reset: Boolean that indicates whether the robot needs to recalibrate the 0° vertical and 0°
        horizontal of the arm, or if it has already been calibrated and we already know the arms position.
        """

        if needs_reset:
            self.reset_arm_position()
        
        if degrees_between_heights >= 0:
            raise Exception("degrees_between_heights has to be a negative number")
        
        v_stops = int(120 / abs(degrees_between_heights))

        virtual_h_state = 0
        virtual_v_state = 0

        points = []
        for i in range(v_stops):

            virtual_v_state = virtual_v_state + degrees_between_heights
            self.go_to(virtual_h_state, virtual_v_state)
            h_stops = int(math.sin(math.radians(abs(virtual_v_state))) * n_img_max)
            degrees_between_photos = 360/h_stops  # Graus a moure la càmera entre fotos
            for j in range(h_stops):
                
                if j != 0:
                    if (i % 2) == 0:
                        virtual_h_state = virtual_h_state + degrees_between_photos
                    else:
                        virtual_h_state = virtual_h_state - degrees_between_photos

                else:
                    if (i % 2) == 0:
                        virtual_h_state = 0
                    else:
                        virtual_h_state = 359.99999999999
                self.go_to(virtual_h_state, virtual_v_state)

                time.sleep(0.1)
                dist = self.arduino.get_data()
                point = create_point(dist, self.current_state['lambda'], self.current_state['phi'], self.position['x'], self.position['y'], self.position['z'], self.orientation_of_x_vector)
                points.append(point)

        print_points_to_file(points)

        self.go_to(90, -90)

    def reset_arm_position(self):
        """
        Moves the arm horizontally clockwise till the micro-switch 1 has been pressed, then moves the arm vertically
        counter-clockwise till the micro-switch 2 has been pressed. Then sets the current state of the arm as λ=0° φ=0°
        """
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

        self.go_to(90, -90)
        time.sleep(5)

    def go_to(self, new_lambda, new_phi):
        """
        Moves the arm to the new lambda and new phi from the current position.

        @param new_lambda: Lambda (horizontal position) where the arm will end up
        @param new_phi: Phi (vertical position) where the arm will end up.
        """

        if new_lambda < 0.0 or new_lambda >= 360.0 or new_phi > 0.0 or new_phi < -180.0:
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
    
    def __scan_specific_angles(self, to_visit):
        """
        Measure the distance at the angles in to_visit, creates a 3-dimensional point in base at the distance measured,
        the direction the robot is pointing, and the position and orientation of the robot in the space. Once finished,
        stores all the created points in the points file.

        @param to_visit: List of lists of 2 elements, the first is the lambda and the second the phi. Angles to go
        measure the distance.
        """

        points = []
        for angles in to_visit:
            self.go_to(angles[0], angles[1])
            dist = self.arduino.get_data()
            point = create_point(dist, self.current_state['lambda'], self.current_state['phi'], self.position['x'],
                                 self.position['y'], self.position['y'], self.orientation_of_x_vector)
            points.append(point)

        print_points_to_file(points)
    
    def cleanup(self):
        """
        Cleans up the pins of the raspberry pi.
        """
        self.stepper1.cleanup()
        self.stepper2.cleanup()
        GPIO.cleanup()
