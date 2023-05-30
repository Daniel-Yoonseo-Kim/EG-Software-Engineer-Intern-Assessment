import json
import numpy as np
import pandas as pd

# A class to define a point
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# A class to define a line
class Line:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

# A helper function to find the maximum x value from a group of points
def find_max_x_value(points):
    return max(points, key=lambda item:item.x).x

# A helper function to determine if a point is on a line
def onLine(line, point):
    if (point.x <= max(line.point1.x, line.point2.x) and point.x <= min(line.point1.x, line.point2.x)
        and (point.y <= max(line.point1.y, line.point2.y)and point.y <= min(line.point1.y, line.point2.y))):
        return True
    return False

# A helper function to determine the direction of three points
def direction(a, b, c):
    value = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y)
    # Case Collinear
    if value == 0:
        return 0
    # Case Clockwise
    elif value > 0:
        return 1
    # Case Counter-Clockwise
    else:
        return 2

# A helper function to determine if two lines intersect each other
def intersect(line1, line2):
    dir1 = direction(line1.point1, line1.point2, line2.point1)
    dir2 = direction(line1.point1, line1.point2, line2.point2)
    dir3 = direction(line2.point1, line2.point2, line1.point1)
    dir4 = direction(line2.point1, line2.point2, line1.point2)

    # Case Regular Intersection
    if dir1 != dir2 and dir3 != dir4:
        return True
    
    # Case Point1 of Line1 is on Line2
    if dir4 == 0 and onLine(line2, line1.point2):
        return True

    # Case Point1 of Line2 is on Line1
    if dir2 == 0 and onLine(line1, line2.point2):
        return True

    # Case Point2 of Line1 is on Line2
    if dir3 == 0 and onLine(line2, line1.point1):
        return True

    # Case Point2 of Line2 is on Line1
    if dir1 == 0 and onLine(line1, line2.point1):
        return True

    # Case No cases satisfied
    return False

# A helper function to determine if a point is within a boundary of points
# This function implements ray tracing to determine if a point falls within a boundary
def checkInside(boundary, point):
    # Function fails when there are less than 3 boundary points
    n = len(boundary)
    if n < 3:
        return False

    # Find the maximum x value of all the boundary points
    max_x = find_max_x_value(boundary)

    # Create a point at maximum x plus one, and same y as point to draw a line through
    line = Line(point, Point(max_x + 1, point.y))
    count = 0
    i = 0
    
    while True:
        # Checks if each boundary line intersects with the ray tracing line
        side = Line(boundary[i], boundary[(i + 1) % n])
        if intersect(side, line):
            if (direction(side.point1, point, side.point2) == 0):
                return onLine(side, point)
            count += 1

        i = (i + 1) % n
        # Break when iterated through all boundary lines
        if i is 0:
            break

    # If odd number of intersections, the point is within the boundary
    return (count % 2)

def setBoundaries():
    return [Point(-1735, 250), Point(-2024, 398), Point(-2806, 742), Point(-2472, 1233), Point(-1565, 580)]

class ProcessGameState:
    def __init__(self, file_path):
        self.data = self.load_data(file_path)
        self.site_boundaries = None
        self.data_size = self.data_length()

    @staticmethod
    def load_data(file_path):
        return pd.read_parquet(file_path)

    def data_length(self):
        return self.data.shape[0]

    def setBoundaries(self, points):
        self.site_boundaries = points

    def isSite(self, point):
        if self.site_boundaries is not None:
            return checkInside(self.site_boundaries, point)

    def extract_weapon_classes(self):
        # Extract weapon classes from the inventory json column
        weapon_classes = []
        for _, row in self.data.iterrows():
            if row['inventory'] is None:
                weapon_classes.append('None')
            else:
                inventory_dump = json.dumps(row['inventory'].tolist())
                inventory = json.loads(inventory_dump)
                weapon_class = []
                for item in inventory:
                    weapon_class.append(item['weapon_class'])
                weapon_classes.append(weapon_class)
                weapon_class = []
        return weapon_classes

    def find_weapon_class(self, weapon):
        weapon_classes = self.extract_weapon_classes()
        return next(x for x in weapon_classes if weapon in x)

    def calculate_avg_entry_time(self, site_name, weapon_types, min_players, team):
        # Calculate the average timer for entering a bombsite with the given weapon types
        filtered_data = self.data[(self.data['site'] == site_name) &
                                  (self.data['team'] == team) &
                                  (self.data['players'] >= min_players)]

        filtered_data['timestamp'] = pd.to_datetime(filtered_data['timestamp'])
        filtered_data = filtered_data.sort_values(by='timestamp')

        avg_entry_time = filtered_data.groupby('round')['timestamp'].diff().mean()
        return avg_entry_time
