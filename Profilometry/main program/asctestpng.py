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

# Set the size of the image to build the sheet more accurately and convert these weird numbers to actual height data
height_uM = 9.899 # found on profilmonline
data_x = 6001 # found on ASC file
x_uM = 3960 # found on profilmonline
data_y = 100 # found on ASC file
y_uM = 3051 # found on profilmonline

print("-----------------------------------------------------------------------")

# to convert from weird ASC values to microns
def convertToMicrons(value):
    #convert value to microns
    if value < 0: # adjusts for negative numbers
        value = 0
    value = value * (height_uM / highest_asc)
    
    return value

def level(list):
    # calculates slope
    first_point = list[-1][0]
    last_point = list[-1][-1]
    print(first_point, last_point)
    slope = (last_point - first_point) / len(list)

    # Divide all rows by the slope
    leveled_table = [[value / slope for value in row] for row in list]

    return leveled_table

def submit_values():
    global path, x_uM, y_uM, height_uM
    x_uM = int(x_um_entry.get())
    y_uM = int(y_um_entry.get())
    height_uM = float(height_um_entry.get())
    
def open_file():
    global file_path
    if not plt.fignum_exists(1):
        file_path = filedialog.askopenfilename(filetypes=[("OPDX files", "*.opdx"), ("ASC files", "*.ASC")])
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
    return x, y, z.T, metadata # z transposed simply to match ASC format

def process_file(file_path):

    def format_coord(x,y):
        # properly print some coordinates and other useful info
        return f'{x:.2f},{y:.2f}, raw={data[math.floor(x), math.floor(y)]:0.4f}' #, uM={data_transpose[round(y), round(x)]:0.4f}'

    '''# Check if any plots are already open
    if plt.get_fignums():
        print("Clearing existing plot...")
        plt.close()
    else:
        print("No plot to clear.")'''

    global data_x, data_y
    
    if '.asc' in file_path.lower():
        # Load the ASC file and skips the rows before the actual data
        with open(file_path, 'r') as file:
            lines = file.readlines()
            start_index = 8 # not 9!

            # pulls the pixels of the image straight from the ASC file
            data_y = line_2_numbers = int(re.search(r'\d+', lines[1]).group())
            data_x = int(re.search(r'\d+', lines[2]).group())

        # Process the data and format into a table
        data_raw = np.loadtxt(file_path, skiprows=start_index)

        global highest_asc, lowest_asc
        highest_asc = np.max(data_raw)
        lowest_asc = np.min(data_raw)

        data = np.vectorize(convertToMicrons)(data_raw)

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

        table = level(table)
    else:
        # opdx file
        _, _, data_raw, _ = read_opdx(file_path)

        minimum = data_raw.min()
        data = ((data_raw - minimum) * 1e6) # now in microns instead of meters
        data_y, data_x = data_raw.shape

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
root.title("ASC File Processor")

btn_open = tk.Button(root, text="Open ASC or opdx File", command=open_file)
btn_open.pack()

file_path_label = tk.Button(root, text="Open Excel File", command=open_file2)
file_path_label.pack()

x_um_label = tk.Label(root, text="X uM (ProfilmOnline):")
x_um_label.pack()

x_um_entry = tk.Entry(root)
x_um_entry.pack()

y_um_label = tk.Label(root, text="Y uM (ProfilmOnline):")
y_um_label.pack()

y_um_entry = tk.Entry(root)
y_um_entry.pack()

height_um_label = tk.Label(root, text="Height uM (ProfilmOnline):")
height_um_label.pack()

height_um_entry = tk.Entry(root)
height_um_entry.pack()

submit_button = tk.Button(root, text="Submit", command=submit_values)
submit_button.pack()

info = tk.Label(root, text = "Fill in text boxes, then click submit. After that, choose an ASC file. \n Before loading a new file, manually X out of the current one.")
info.pack()

# Start the Tkinter event loop
root.mainloop()

root.mainloop()
print("Closing application...")
