import tkinter as tk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import cv2
import dragrectangle
import re
import math
from opdx_reader import DektakLoad

print("-----------------------------------------------------------------------")

'''# Set the size of the image to build the sheet more accurately and convert these weird numbers to actual height data
height_uM = 9.899 # found on profilmonline
data_x = 6001 # found on ASC file
x_uM = 3960 # found on profilmonline
data_y = 100 # found on ASC file
y_uM = 3051 # found on profilmonline'''

def level(list):
    # calculates slope
    first_point = list[-1][0]
    last_point = list[-1][-1]
    print(first_point, last_point)
    slope = (last_point - first_point) / len(list)

    # Divide all rows by the slope
    leveled_table = [[value / slope for value in row] for row in list]

    return leveled_table
    
def open_file():
    global file_path
    if not plt.fignum_exists(1):
        file_path = filedialog.askopenfilename(filetypes=[("OPDX files", "*.opdx")])
        if file_path:
            process_file(file_path)
    else:
        print("Close current plot before opening a new one!")

def open_file2():
    global path
    if not plt.fignum_exists(1):
        path = filedialog.askopenfilename(filetypes=[("excel files", "*.xlsx")])

def read_opdx(file_path):
    loader = DektakLoad(file_path)
    x, y, z = loader.get_data_2D()
    metadata = loader.get_metadata()
    return y, x, z.T, metadata # x and y swapped because of the TRANSPOSE

def process_file(file_path):

    def format_coord(x,y):
        # properly print some coordinates and other useful info
        return f'{x:.2f},{y:.2f}, raw={data[math.floor(x), math.floor(y)]:0.4f}' #, uM={data_transpose[round(y), round(x)]:0.4f}'

    global data_x, data_y

    # opdx file
    x, y, data_raw, metadata = read_opdx(file_path)
    minimum = data_raw.min()
    data = ((data_raw - minimum) * 1e6) # now in microns instead of meters
    data_y, data_x = data_raw.shape

    x_uM = x.max()
    y_uM = y.max()

    aspect_ratio = (data_y/data_x) * (y_uM/x_uM)
    data_transpose = data.T

    # yes i only wrote this to look like the profilmonline colormap since i think it looks cool
    image = cv2.imread('Profilometry\Colormap.png')
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    colors = []
    for row in reversed(image_rgb):
        for color in row:
            colors.append(color / 255.0)  # Normalize the colors to range [0, 1]
    custom_cmap = LinearSegmentedColormap.from_list('custom_colormap', colors)

    # Plotting the data with a custom colormap
    plt.imshow(data_transpose, cmap=custom_cmap, aspect=aspect_ratio) # rotate
    plt.colorbar()  # Add a color bar for reference
    #fig=plt.figure()

    # create custom tick values
    x_ticks = np.linspace(0, data_x, int(x_uM / 500)) 
    y_ticks = np.linspace(0, data_y, int(y_uM / 500)) 

    # create custom tick labels
    x_tick_labels = ['{:.0f}'.format(x * (y_uM / data_x)) for x in x_ticks]  # due to the transpose, switch x_uM and y_uM here
    y_tick_labels = ['{:.0f}'.format(y * (x_uM / data_y)) for y in y_ticks]  # due to the transpose, switch x_uM and y_uM here

    # set ticks
    plt.yticks(x_ticks, x_tick_labels)
    plt.xticks(y_ticks, y_tick_labels)

    # add labels to the axes
    plt.xlabel('X-Distance (µM)')
    plt.ylabel('Y-Distance (µM)')

    # interactivify the plot
    # mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(f"Value: {data[sel.target.index]}"))

    # Create the draggable rectangle
    ax = plt.gca()
    x_values = np.linspace(0, data_x, data_x + 1)
    y_values = np.linspace(0, data_y, data_y + 1)

    ax.format_coord=format_coord

    dr = dragrectangle.DragRectangle(ax, x_values, y_values, data, path)
    dr.connect()

    # open plot
    plt.show()

    print(f"Plotted numpy array as image with colormap and scale")

root = tk.Tk()
root.title("OPDX File Processor")

file_path_label = tk.Button(root, text="Open Excel File", command=open_file2)
file_path_label.pack()

btn_open = tk.Button(root, text="Open OPDX file", command=open_file)
btn_open.pack()

info = tk.Label(root, text = "Choose an excel file and then open an opdx file\nto plot it and gather data by dragging a rectangle.\nTo return N/A values, right click on the 3D PLOT\nand not the 2d graph.")
info.pack()

# Start the Tkinter event loop
root.mainloop()

root.mainloop()
print("Closing application...")