from svgpathtools import svg2paths
import numpy as np

wThresh = 10 #Change these to change the minimum subpath size 
hThresh = 10 #Too large, many intended paths will be skipped, to small, artifacts will easste timre

def svg_to_coordinates(svg_file, number_of_samples):
    #Basically converts svg to coordinates
    #but also add like z axis moces
    paths, attributes = svg2paths(svg_file) #The attributes data is not used

    all_waypoints = []

    for path in paths:

        subpaths = path.continuous_subpaths() #Split inon continuous segments nto disconnected pieces 

        for subpath in subpaths:

            boundingBox = subpath.bbox()  # returns (xmin, xmax, ymin, ymax)
            width = boundingBox[1] - boundingBox[0]
            height = boundingBox[3] - boundingBox[2]

            if width < wThresh and height < hThresh: 
                continue
            

            all_waypoints.append(("UP","UP")) #Lift pen before moving to start ponut

            for i, t in enumerate(np.linspace(0, 1, number_of_samples)):
                point = subpath.point(t)

                x, y = point.real, point.imag
                x, y = float(x), float(y)
                all_waypoints.append((round(x, 2), round(y, 2)))

                if i == 0:
                    all_waypoints.append(("DOWN","DOWN")) #Pen down at the first point

    return all_waypoints


def svg_size(svg_file):
    #Reads svg nd returns width, heught and minimum y
    paths, attributes = svg2paths(svg_file)

    overall_xmin = float('inf')
    overall_xmax = float('-inf')
    overall_ymin = float('inf')
    overall_ymax = float('-inf')

    for path in paths:
        subpaths = path.continuous_subpaths()

        for subpath in subpaths:
            boundingBox = subpath.bbox()  
            width = boundingBox[1] - boundingBox[0]
            height = boundingBox[3] - boundingBox[2]

            if width < wThresh and height < hThresh:
                continue  

            overall_xmin = min(overall_xmin, boundingBox[0])
            overall_xmax = max(overall_xmax, boundingBox[1])
            overall_ymin = min(overall_ymin, boundingBox[2])
            overall_ymax = max(overall_ymax, boundingBox[3])

    svg_width = round(overall_xmax - overall_xmin, 2)
    svg_height = round(overall_ymax - overall_ymin, 2)
    ymin = round(overall_ymin, 2) #btw im sending the total umin by rounding the value of the closest y valu

    return svg_width, svg_height, ymin

if __name__ == "__main__":

    SVGfile = "Python Scripts/star test.svg"

    waypointsList = svg_to_coordinates(SVGfile, 30) #Parse the SVGfile file with 50 points PER SUBPATH

    print(f"\nExtracted {len(waypointsList)} coordinates from the file {SVGfile}: \n")

    for waypoint in waypointsList:
        print(waypoint)

    print(f"The print size is {svg_size(SVGfile)}")