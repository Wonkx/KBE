from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import numpy as np
import math

#initial polygon
LENGTH = 50
WIDTH = 50
HEIGHT = 20
ROTATION = np.pi/3
SUNANGLE = np.pi/10

#rotating building
building = [(0,0), (LENGTH,0),  (LENGTH, WIDTH), (0,WIDTH)]
rot = np.array([[np.cos(ROTATION), -np.sin(ROTATION)], [np.sin(ROTATION), np.cos(ROTATION)]])
rotated = [np.dot(rot, building[i]) for i in range(len(building))]

#finding a the outlines of the shaded area
shaded_length = HEIGHT / math.tan(SUNANGLE)
shaded = [(x, y + shaded_length) for x, y in rotated]

#finding the bottom left corner of the shaded area and removing it from the shaded list because it is not part of the shaded area. 
min_y = float('inf')
min_index = None
for i, tpl in enumerate(shaded):
    y = tpl[1]
    if y < min_y:
        min_y = y
        min_index = i
del shaded[min_index]
del rotated[min_index]
rotated.reverse()
shaded_poly = rotated + shaded

#ploting
polygon = Polygon(shaded_poly, facecolor='green', alpha=0.5)
fig, ax = plt.subplots(1,1)
ax.add_patch(polygon)
plt.axis('equal')

# get the x and y coordinates of the vertices as separate lists
x, y = polygon.get_xy().T
# calculate the area using the Shoelace formula
area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
print("Area of shade of building:", area, " m^2")