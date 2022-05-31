import math

points_file_path = "./points/points"


def find_coord_self(lambda_a, fi_a, dist_a, lambda_b, fi_b, dist_b):
    #print("Lambda_a: " + str(lambda_a))
    #print("Fi_a: " + str(fi_a))
    #print("Dist_a: " + str(dist_a))
    #print("Lambda_b: " + str(lambda_b))
    #print("Fi_b: " + str(fi_b))
    #print("Dist_b: " + str(dist_b))
    
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
                
    #print("x: " + str(x))
    #print("y: " + str(y))
    #print("z: " + str(z))
    #print("orient: " + str(orient))
    return x, y, z, orient


def image_point_to_angle_config(x_mov, y_mov, lambda_img, fi_img, open_h, size_h, size_v):

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
    
    #print("x_mov: " + str(x_mov))
    #print("y_mov: " + str(y_mov))
    #print("Lambda_img: " + str(lambda_img))
    #print("Fi_img: " + str(fi_img))
    #print("Open_h: " + str(open_h))
    #print("Size_h: " + str(size_h))
    #print("Size_v: " + str(size_v))
    #print("Lambda dest: " + str(lambda_dest))
    #print("Fi dest: " + str(fi_dest))
    #print("Inc Lambda: " + str(inc_lambda))
    #print("Inc Fi: " + str(inc_fi))
    return lambda_dest, fi_dest


def create_point(dist, current_lambda, current_fi, lg_x, lg_y, lg_z, lg_orient):

    dist_xy = math.sin(math.radians(current_fi)) * dist

    real_lambda = current_lambda - lg_orient

    if real_lambda < 0:
        real_lambda = 360 + real_lambda

    x = (math.cos(math.radians(real_lambda)) * dist_xy) + lg_x
    y = (math.sin(math.radians(real_lambda)) * dist_xy) + lg_y
    z = (math.cos(math.radians(current_fi)) * dist) + lg_z

    return {'x': x, 'y': y, 'z': z}


def print_points_to_file(points, file_path=points_file_path):
    with open(file_path, 'a') as file:
        for point in points:
            file.write(str(point['x']) + ',' + str(point['y']) + ',' + str(point['z']) + '\n')


def clear_points_file(file_path=points_file_path):
    with open(file_path, 'r+') as file:
        file.truncate(0)
