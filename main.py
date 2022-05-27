from lasergaze import Robot
import cloud_manager
import time

robot = Robot()
#robot.cleanup()

try:
    #robot.localize_self()
    robot.take_wide_barrage_of_points()
    robot.print_points_to_file()
    #robot.find_points_of_interest()
    #robot.reset_arm_position()
    #robot.go_to(90, -90)
    #print(robot.arduino.get_data())
    #robot.camera.take_and_save_photo("/home/lasergaze/Desktop/Repo/tmp/tmp.jpg")
    #for i in range(20):
    #    print(robot.arduino.get_data())
    #    time.sleep(0.5)
    
    robot.cleanup()
except Exception as e:
    print("Error: " + str(e))
    robot.cleanup()
except KeyboardInterrupt:
    robot.cleanup()
