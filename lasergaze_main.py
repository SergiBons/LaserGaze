from lasergaze import Robot
import sys

"""
Receives the behaviour for the robot, checks if the introduced behaviour is valid, check the optional parameters
n_img_max and degrees_between_heights, creates the instance of the Robot, and calls at the corresponding function
dictated by the behaviour. When finished calls at the cleanup of the robot.
"""

robot = None
try:
    if(len(sys.argv)) < 2:
        print("Error: Argument specifying behaviour required")
        exit(1)

    valid_behaviors = ["quick_static_scan", "complete_static_scan", "quick_mobile_scan", "complete_mobile_scan",
                       "prepare_new_scan", "finish_scan", "cleanup"]
    behaviour = sys.argv[1]
    if behaviour not in valid_behaviors:
        print("Error: Incorrect behavior argument")
        exit(1)
    n_img_max = None
    degrees_between_heights = None
    extra_args = False
    if len(sys.argv) >= 4:
        extra_args = True
        n_img_max = int(sys.argv[2])
        degrees_between_heights = int(sys.argv[3])

    robot = Robot()

    if behaviour == valid_behaviors[0]:     # quick_static_scan
        if extra_args:
            robot.quick_static_scan(n_img_max, degrees_between_heights)
        else:
            robot.quick_static_scan()
    elif behaviour == valid_behaviors[1]:   # complete_static_scan
        if extra_args:
            robot.complete_static_scan(n_img_max, degrees_between_heights)
        else:
            robot.complete_static_scan()
    elif behaviour == valid_behaviors[2]:   # quick_mobile_scan
        if extra_args:
            robot.quick_mobile_scan(n_img_max, degrees_between_heights)
        else:
            robot.quick_mobile_scan()
    elif behaviour == valid_behaviors[3]:   # complete_mobile_scan
        if extra_args:
            robot.complete_mobile_scan(n_img_max, degrees_between_heights)
        else:
            robot.complete_mobile_scan()
    elif behaviour == valid_behaviors[4]:   # prepare_new_scan
        robot.prepare_new_scan()
    elif behaviour == valid_behaviors[5]:   # finish_scan
        robot.finish_scan()
    elif behaviour == valid_behaviors[6]:   # cleanup
        robot.cleanup()
        exit(0)
    else:
        # Redundancy just in case
        print("Error: Incorrect behavior argument")
        exit(1)
    
    robot.cleanup()
    exit(0)
except Exception as e:
    print("Error: " + str(e))
    if robot is None:
        robot.cleanup()
    exit(1)
except KeyboardInterrupt:
    if robot is None:
        robot.cleanup()
    exit(1)
except ValueError:
    print("Error: Number of maximum images to be taken and degrees between heights have to be integers")
    if robot is None:
        robot.cleanup()
    exit(1)
