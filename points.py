import math

points_file_path = "./points/points"


def find_coord_self(lambda_a, fi_a, dist_a, lambda_b, fi_b, dist_b):
    """
    Triangulates the position of the robot in base of the direction where the anchor 1 was found, the distance to it,
    the direction where the anchor 2 was found, and the distance to it. Puts the 0, 0, 0 at the position of the anchor 1
    and the vector x pointing towards the anchor 2.

    @param lambda_a: Horizontal angle where the anchor 1 was found.
    @param fi_a: Vertical angle where the anchor 1 was found (0° in th pole north of the sphere that represents the
    working area of the arm).
    @param dist_a: Distance to the anchor 1.
    @param lambda_b: Horizontal angle where the anchor 2 was found.
    @param fi_b: Vertical angle where the anchor 2 was found (0° in th pole north of the sphere that represents the
    working area of the arm).
    @param dist_b: Distance to the anchor 2.
    @return: Coordinates x, y z of th position, and the angle of orientation from the vector x of the coordinates
    system clockwise to the 0° horizontal of the robot.
    """
    
    # Les coordenades (0,0) aniran sobre l'ancora A amb z vertical i x apuntant a la direcció de l'ancora B
    #   de tal manera que l'ancora B quedara situada sobre el pla XZ.

    z = -(math.cos(math.radians(fi_a)) * dist_a)
    # Ja que z sempre estarà en direcció perpendicular al terra, podem calcular-la directament
    
    da_xy = abs(math.sin(math.radians(fi_a)) * dist_a)   # Busquem les distàncies del LG a les àncores A i B sobre el pla XY
    db_xy = abs(math.sin(math.radians(fi_b)) * dist_b)
    
    lambda_ab = abs(lambda_a - lambda_b)   # Calculem l'angle que formen les 2 rectes
    
    if lambda_ab > 180:                 # En cas de que la orientació del LG quedi en mig de les dues ancores,
        lambda_ab = 360 - lambda_ab     # canviem la orientació de l'angle
    
    lambda_temp = 90 - lambda_ab
    # Busquem l'angle restant al dividir el triangle en 2 per aplicar raons trigonomètriques
    
    if da_xy > db_xy:
        h = math.cos(math.radians(lambda_temp)) * db_xy  # Trobem l'altura del triangle
        da_xy_s = da_xy - math.sin(math.radians(lambda_temp)) * db_xy  # Calculem la distància escurçada de dAxy per generar
        lambda_blg = math.degrees(math.atan(h/da_xy_s))  # el triangle rectangle i calculem l'angle format per les línies A-B i A-LG
        
    elif da_xy < db_xy:
        h = math.cos(math.radians(lambda_temp)) * da_xy
        db_xy_s = db_xy - math.sin(math.radians(lambda_temp)) * da_xy  # Mateix procediment però des de l'ancora B
        lambda_blg = math.degrees(math.atan(h/db_xy_s))
        
    else:
        lambda_blg = (180 - lambda_ab)/2  # Cas de triangle isosceles, calcular l'angle B-LG es trivial
        
    
    x = math.cos(math.radians(lambda_blg)) * da_xy  # La dimensió de l'angle ja determinarà si x es positiva o negativa
    y = math.sin(math.radians(lambda_blg)) * da_xy
    
    # Busquem la configuració actual del sistema per trobar l'orientació i la direcció de y
    if (lambda_a > lambda_b and lambda_a - lambda_b < 180) or (lambda_a < lambda_b and lambda_b - lambda_a > 180):
        y = -y                        # B queda a la dreta de la línia LG-A, per tant LG esta a y negativa
        orient = lambda_a - (180 - lambda_blg)
        if orient < 0:
            orient = 360 + orient
            
    else:
        orient = lambda_a + (180 - lambda_blg)
        if orient >= 360:
            orient = orient - 360
            
    
    if lambda_a == lambda_b:    # Correcció de la orientació sobre un sistema en línea
        orient = lambda_a
        if da_xy > db_xy:
            orient = orient + 180
            if orient >= 360:
                orient = orient - 360

    return x, y, z, orient


def image_point_to_angle_config(x_mov, y_mov, lambda_img, fi_img, open_h, size_h, size_v):
    """
    Receives the normalized position inside of an image, and transforms that to the angle configuration the motors have
    to go to point at that position of the image taken by the camera.

    @param x_mov: In image position horizontal (0 at the left, 1 at the right)
    @param y_mov: In image position vertical (0 at the top, 1 at the bottom)
    @param lambda_img: Horizontal position of the arm when the photo was taken.
    @param fi_img: Vertical position of the arm when the photo was taken.
    @param open_h: Horizontal aperture of the camera.
    @param size_h: Horizontal size of the image
    @param size_v: Vertical size of the image.
    @return: New configuration of angles for the motors to point in the direction of the position in the image.
    """

    x = x_mov - 0.5  # Posem el (0,0) de les coordenades normalitzades al centre de la imatge
    y = y_mov - 0.5

    dist = (size_h/2) / math.tan(math.radians(open_h / 2))  # Calculem la distancia a partir del FoV

    inc_lambda = math.degrees(math.atan(x*size_h/dist))  # Calculem el desplaçament de lambda i fi respecte el
    inc_fi = math.degrees(math.atan(y*size_v/dist))       # vector perpendicular a la imatge situat a (0,0)

    lambda_dest = lambda_img - inc_lambda + 5  # Apliquem aquest desplaçament a la posició que tenia
    fi_dest = fi_img - inc_fi              # el robot durant la presa de la imatge.

    if lambda_dest > 360:
        lambda_dest = lambda_dest - 360
    elif lambda_dest < 0:
        lambda_dest = 360 + lambda_dest

    return lambda_dest, fi_dest


def create_point(dist, current_lambda, current_fi, lg_x, lg_y, lg_z, lg_orient):
    """
    Creates a 3-dimensional point based in the distance measured, the current direction the robot is pointing towards,
    the position of the robot in the space, and its orientation.

    @param dist: Distance measured.
    @param current_lambda: Current horizontal position.
    @param current_fi: Current Vertical position.
    @param lg_x: X coordinate of the position of the robot.
    @param lg_y: Y coordinate of the position of the robot.
    @param lg_z: Z coordinate of the position of the robot.
    @param lg_orient: Angle from the vector X of the coordinates system to the 0° horizontal of the robot.
    @return: A map with the x, y, z of the created point.
    """

    dist_xy = math.sin(math.radians(current_fi)) * dist

    real_lambda = current_lambda - lg_orient

    if real_lambda < 0:
        real_lambda = 360 + real_lambda

    x = (math.cos(math.radians(real_lambda)) * dist_xy) + lg_x
    y = (math.sin(math.radians(real_lambda)) * dist_xy) + lg_y
    z = (math.cos(math.radians(current_fi)) * dist) + lg_z

    return {'x': x, 'y': y, 'z': z}


def print_points_to_file(points, file_path=points_file_path):
    """
    Prints a list of maps with the x, y, z of points to the points file.

    @param points: List of maps with the x, y, z of points
    @param file_path: Path to the points file.
    """
    with open(file_path, 'a') as file:
        for point in points:
            file.write(str(point['x']) + ',' + str(point['y']) + ',' + str(point['z']) + '\n')


def clear_points_file(file_path=points_file_path):
    """
    Clear the points stored in the points file in order to start a new scan.

    @param file_path: Path to the points file.
    """
    with open(file_path, 'r+') as file:
        file.truncate(0)
