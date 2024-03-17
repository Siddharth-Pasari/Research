import tkinter as tk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import cv2
import dragrectangle
import pandas as pd

# Set the size of the image to build the sheet more accurately and convert these weird numbers to actual height data
height_uM = 9.899 # found on profilmonline
data_x = 6001 # found on ASC file
x_uM = 3960 # found on profilmonline
data_y = 100 # found on ASC file
y_uM = 3051 # found on profilmonline
y_res = y_uM / data_y

print("-----------------------------------------------------------------------")


# to convert from weird ASC values to microns
def convertToMicrons(value):
    microns = value - lowest_asc # adjusts for negative numbers
    microns = microns * (height_uM / (highest_asc - lowest_asc))
    return microns

def submit_values():
    global path, x_uM, y_uM, height_uM, y_res
    path = file_path_entry.get()
    x_uM = int(x_um_entry.get())
    y_uM = int(y_um_entry.get())
    height_uM = float(height_um_entry.get())
    y_res = y_uM / data_y
    
def open_file():
    if not plt.fignum_exists(1):
        file_path = filedialog.askopenfilename(filetypes=[("ASC files", "*.ASC")])
        if file_path:
            process_file(file_path)
    else:
        print("Close current plot before opening a new one!")

def process_file(file_path):

    '''# Check if any plots are already open
    if plt.get_fignums():
        print("Clearing existing plot...")
        plt.close()
    else:
        print("No plot to clear.")'''

    # Load the ASC file and skips the rows before the actual data
    with open(file_path, 'r') as file:
        lines = file.readlines()
        start_index = lines.index("RAW_DATA\t3\t2400400\t\n") + 1

    # Process the data and format into a table
    data = np.loadtxt(file_path, skiprows=start_index)

    global highest_asc, lowest_asc
    highest_asc = np.max(data)
    lowest_asc = np.min(data)

    data = np.vectorize(convertToMicrons)(data)

    table = []
    row = []
    for row_values in data:
        for value in row_values:
            if len(row) < data_x:
                row.append(value)
            else:
                table.append(row)
                row = [value]

    if row:
        table.append(row) # for the last row

    # yes i only wrote this to look like the profilmonline colormap since i think it looks cool
    image = cv2.imread('Colormap.png')
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    colors = []
    for row in reversed(image_rgb):
        for color in row:
            colors.append(color / 255.0)  # Normalize the colors to range [0, 1]
    custom_cmap = LinearSegmentedColormap.from_list('custom_colormap', colors)

    # Plotting the data with a jet colormap
    plt.imshow(data.T, cmap=custom_cmap, aspect=(data_y/data_x) * (y_uM/x_uM)) # rotate
    plt.colorbar()  # Add a color bar for reference

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

    dr = dragrectangle.DragRectangle(ax, x_values, y_values, data, path)
    dr.connect()

    # open plot
    plt.show()

    print(f"Plotted numpy array as image with colormap and scale")

root = tk.Tk()
root.title("ASC File Processor")

btn_open = tk.Button(root, text="Open ASC File", command=open_file)
btn_open.pack()

file_path_label = tk.Label(root, text="File Path:")
file_path_label.pack()

file_path_entry = tk.Entry(root)
file_path_entry.pack()

x_um_label = tk.Label(root, text="X uM:")
x_um_label.pack()

x_um_entry = tk.Entry(root)
x_um_entry.pack()

y_um_label = tk.Label(root, text="Y uM:")
y_um_label.pack()

y_um_entry = tk.Entry(root)
y_um_entry.pack()

height_um_label = tk.Label(root, text="Height uM:")
height_um_label.pack()

height_um_entry = tk.Entry(root)
height_um_entry.pack()

submit_button = tk.Button(root, text="Submit", command=submit_values)
submit_button.pack()

# Start the Tkinter event loop
root.mainloop()

root.mainloop()
print("Closing application...")