import os
import numpy as np
import matplotlib.pyplot as plt
import mplcursors
from matplotlib import ticker

# Set the size of the image to build the sheet more accurately and convert these weird numbers to actual height data
height_uM = 9.899 # found on profilmonline
data_x = 6001 # found on ASC file
x_uM = 3960 # found on profilmonline
data_y = 100 # found on ASC file
y_uM = 3051 # found on profilmonline

# Load the ASC file and skips the rows before the actual data
with open('p2.ASC', 'r') as file:
    lines = file.readlines()
    start_index = lines.index("RAW_DATA\t3\t2400400\t\n") + 1

# Process the data and format into a table
data = np.loadtxt('p2.ASC', skiprows=start_index)

table = []
row = []
for row_values in data:
    for value in row_values:
        if len(row) < data_x: # According to the ASC file, the width is 6001
            row.append(value)
        else:
            table.append(row)
            row = [value]

if row:
    table.append(row) # for the last row

print(data.shape)
print(int(data_x / data_y))

# Plotting the data with a hot colormap
plt.imshow(data.T, cmap='hot')
plt.gca().set_aspect((data_y/data_x) * (y_uM/x_uM))
plt.colorbar()  # Add a color bar for reference

plt.xlabel('X-Distance (µM)')
plt.ylabel('Y-Distance (µM)')

# interactivify the plot
# mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(f"Value: {data[sel.target.index]}"))

plt.show()

print(f"Plotted numpy array as image with colormap and scale")
