import math

#Note to self + TO DO:
#L1 and L2 have already been inserted, but STEPS_PER_REV_1 and STEPS_PER_REV_2 haven't
#To calculate that, Ineed to calculate the gear rations and spin motor too. DO LATER
#ALSO figure out what to do when the coordinate is out of range

# ---- Physical arm configuration — adjust these to match your hardware ----
L1 = 227.8  # length of arm 1 in mm
L2 = 141.06  # length of arm 2 in mm

ARM_REACH = L1 + L2

STEPS_PER_REV_1 = 4000  # motor1 steps for one full 360° rotation (incl. microstepping/gearing)
STEPS_PER_REV_2 = 3200  

import math

def scale_svg(x, y, svg_width, svg_height, arm_reach=ARM_REACH, margin=0.75, closest_y = 0, min_forward_dist=100):
    # filteringh snmall
    if svg_width == 0 and svg_height == 0:
        return 0.0, float(min_forward_dist)

    usable_radius = arm_reach * margin

    a = (svg_width / 2) ** 2 + svg_height ** 2
    b = 2 * svg_height * min_forward_dist
    c = min_forward_dist ** 2 - usable_radius ** 2

    if a == 0:
        scale = (usable_radius - min_forward_dist) / max(svg_height, svg_width, 1.0)
    else:
        discriminant = b**2 - 4 * a * c
        if discriminant < 0:
            scale = 1.0  # Fallback if configuration radius is invalid
        else:
            scale = (-b + math.sqrt(discriminant)) / (2 * a)

    # Center horizontally and offset forward
    x_centered = x - (svg_width / 2)
    y_from_top = y - closest_y

    x_scaled = x_centered * scale
    y_scaled = (y_from_top * scale) + min_forward_dist

    return round(x_scaled, 2), round(y_scaled, 2)

def xy_to_angles(x, y, right_handed=True): #This function does the inverse kinematics geometry calcs
    
    #Converts an (x, y) position into the two joint angles (in radians)needed to reach it using  inverse kinematics.

    # Distance from the bot to poiny
    distance = math.sqrt(x**2 + y**2)

    # make sure possible
    max_reach = L1 + L2
    min_reach = abs(L1 - L2)
    if distance > max_reach or distance < min_reach:
        print(f"OUT OF RANGE")
        print(f"Target ({x}, {y}) is unreachable cause distance {distance} is outside arm's range [{min_reach}, {max_reach}]")
        raise ValueError(f"Target ({x}, {y}) is unreachable cause distance {distance} "
                          f"is outside arm's range [{min_reach}, {max_reach}]")

    cos_angle2 = (distance**2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_angle2 = max(-1.0, min(1.0, cos_angle2))  

    angle2 = math.acos(cos_angle2)
    if right_handed:
        angle2 = -angle2  # right or left handed configuration

    k1 = L1 + L2 * math.cos(angle2)
    k2 = L2 * math.sin(angle2)

    angle1 = math.atan2(y, x) - math.atan2(k2, k1)

    return angle1, angle2


def angles_to_steps(angle1, angle2): #This function does the conversion between radians and step count

    #Converts joint angles (in radians) into motor step num

    steps1 = int((angle1 / (2 * math.pi)) * STEPS_PER_REV_1)
    steps2 = int((angle2 / (2 * math.pi)) * STEPS_PER_REV_2)
    return steps1, steps2


def xy_to_steps(x, y, right_handed=True): #This function converts the radian input into steps 

    #Combines first and seccond function for convinence for calling elsewhere

    angle1, angle2 = xy_to_angles(x, y, right_handed)
    steps1, steps2 = angles_to_steps(angle1, angle2)

    return (steps1, steps2)


if __name__ == "__main__":  # Quick test just run these add testpoint ir smthing if want more detailed tear
    
    test_points = [(200, 0), (150, 150), (0, 200)]

    test_pointsError = [(200, 0), (150, 150), (0, 200), (200, 400), (150, 150), (0, 200)]
    
    for x, y in test_points:
        try:

            steps1, steps2 = xy_to_steps(x, y)

            print(f"The coordinates ({x}, {y}) require the stepcounts (shoulder: {steps1}, elbow: {steps2})")

        except ValueError as e:
            print(e)