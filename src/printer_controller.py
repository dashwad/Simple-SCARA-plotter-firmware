from svg_parser import svg_to_coordinates #parse svg
from svg_parser import svg_size #find svg size
from scara_kinematics_conversions import xy_to_steps #connversion
from scara_kinematics_conversions import scale_svg #connversion
import serial
import time

comPort = '/dev/cu.usbserial-10' # the port that is currently being used is /dev/cu.usbserial-10

serialPort = serial.Serial(comPort, 115200, timeout=1)

waypointsList = []
resolution = 0.2 #default resolution is 0.2 (0.1 is quite low res and 0.3 is smooth)

waypointsExample1 = [(100,  50), #Random list of example waypoints
                 (200, 100),
                 (300, 150),
                 (100,  50),
                 (50,  100),
                 (200, 300),
                 (300, 150),
                 ( 50, 200),
                 (100, 150),
                 (200, 100),
                 (300, 150),
                 (100,  50),
                 (50,  100),
                 (200, 300),
                 (300, 150),
                 ( 50, 400),
                 (700, 100)
]

waypointsExample2 = [( 100,  50), #List of example waypoints in going up (can be used for testing)
                  ( 200, 100),
                  ( 300, 150),
                  ( 400, 200),
                  ( 500, 250),
                  ( 600, 300),
                  ( 900, 350),
                  (1000, 400),
                  (1100, 450),
                  (1200, 500),
                  (1300, 550),
                  (1400, 600),
                  (1500, 650),
                  (1600, 700),
                  (1700, 750),
                  (1800, 800),
]

print("")
print("Connecting to arduino......")
print("Please wait for menu before sending any commands")

time.sleep(3)  # wait startup

def send_command(command):
    serialPort.write((command + '\n').encode()) #sending seial

    time.sleep(0.1)

def wait_for_reply(): #Loops infinitely (Which traps the code) until the reply is detected, then it will retirn
    while True:

        reply = serialPort.readline().decode().strip() #read serual

        print(reply)

        if reply == "MOVE COMPLETED":
            print("-----------")
            return


def send_waypoints(waypoints): #sends the thingys one by one
    for x, y in waypoints:

        if (x == "UP" and y == "UP") or (x == "DOWN" and y == "DOWN"):
            send_command(f"Z{x}") 
            print(x)

        else: 
            print(f"X: {x} \nY: {y}")

            waypointCommand = f"W{x},{y}"

            send_command(waypointCommand) 

        wait_for_reply() #Waiting commandd

        print("Waypoint sent")
        print("---------------------------")

    print("All waypoints sent")



while True:

    while serialPort.in_waiting:
        print(serialPort.readline().decode().strip())

    print()
    command = input("Input Commands According to guide > ")
    print()


    if command == "end": #this type to turn code off
        send_command("xx,xy")
        break
    elif command == "runExample1":
        send_waypoints(waypointsExample1)

    elif command == "runExample2":
        send_waypoints(waypointsExample2)

    elif command == "runFile": #runs file and will ask fir relpath of the file
        file = input("Please input the file's relative path > ")
        coordinateList = svg_to_coordinates(file, resolution)
        scaledCoordinates = []
        svg_width, svg_height, closest_y = svg_size(file)

        for x, y in coordinateList:

            if x == "UP" or x == "DOWN":
                waypointsList.append((x, y))

            else:
                scaled_x, scaled_y = scale_svg(x, y, svg_width, svg_height, closest_y = closest_y)
                scaledCoordinates.append((scaled_x, scaled_y))
                waypointsList.append(xy_to_steps(scaled_x, scaled_y))
        
        waypointsList.append(("UP", "UP")) #add ending code
        waypointsList.append((0, 0))
        waypointsList.append(("DOWN", "DOWN"))

        print(scaledCoordinates)
        print()
        print(waypointsList)
        send_waypoints(waypointsList)
        waypointsList = []


    else: 
        send_command(command)

    while serialPort.in_waiting:
        print(serialPort.readline().decode().strip())


print("-------------------------------------------")
print("-------------------------------------------")
print("Script succesfully ended")
print("-------------------------------------------")
print("-------------------------------------------")
