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

def level(heightmap):
    # Calculate the slope on the x-axis using the lower height of the left and right columns
    left_column_min = np.min(heightmap[:, 0])
    right_column_min = np.min(heightmap[:, -1])
    x_slope = (right_column_min - left_column_min) / heightmap.shape[1]

    # Divide each column by the x-axis slope
    for col_index in range(heightmap.shape[1]):
        heightmap[:, col_index] -= left_column_min + col_index * x_slope

    # Calculate the slope on the y-axis using the lower height of the top and bottom rows
    top_row_min = np.min(heightmap[0, :])
    bottom_row_min = np.min(heightmap[-1, :])
    y_slope = (bottom_row_min - top_row_min) / heightmap.shape[0]

    # Divide each row by the y-axis slope
    for row_index in range(heightmap.shape[0]):
        heightmap[row_index, :] -= top_row_min + row_index * y_slope

    return heightmap
    
def open_file():
    global file_path
    if not plt.fignum_exists(1):
        file_path = filedialog.askopenfilename(filetypes=[("OPDX files", "*.opdx")])
        if file_path:
            ftnum=16
            is_empty = not ftnumt.get()
            if not is_empty:
                try:
                    ftnum = int(ftnumt.get())
                except:
                    pass
            is_empty = not startnum.get()
            if not is_empty:
                try:
                    process_file(file_path, int(startnum.get()), ftnum)
                except:
                    process_file(file_path,0,ftnum)
            else:
                process_file(file_path,0,ftnum)
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

def process_file(file_path,num=0,ftnum=16):

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

    if level_var.get() == 1:
        data = level(data)

    data_transpose = data.T

    # yes i only wrote this to look like the profilmonline colormap since i think it looks cool
    image = cv2.imread(r"Profilometry\Colormap.png")
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

    dr = dragrectangle.DragRectangle(ax, x_values, y_values, data, path, num, ftnum, str(titlet.get()))
    dr.connect()

    # open plot
    plt.show()

    print(f"Plotted numpy array as image with colormap and scale")

root = tk.Tk()
root.title("OPDX File Processor")

startnum = tk.Entry(root)
startnum.insert(0, "last number recorded (0)")
startnum.pack()

ftnumt= tk.Entry(root)
ftnumt.insert(0, "# of features (16)")
ftnumt.pack()

titlet= tk.Entry(root)
titlet.insert(0, "name of file (only if starting new)")
titlet.pack()

level_var = tk.IntVar()

level_check = tk.Checkbutton(root, text="Levelling", variable=level_var, onvalue=1, offvalue=0)
level_check.pack()

file_path_label = tk.Button(root, text="Open Excel File", command=open_file2)
file_path_label.pack()

btn_open1 = tk.Button(root, text="Open OPDX File", command=open_file)
btn_open1.pack()

btn_open = tk.Button(root, text="Exit Program", command=exit)
btn_open.pack()

info = tk.Label(root, text = "\n1. Open an excel file to log data to using the button\n\n2. Choose the OPDX file given to you by the DektakXT profilometer to plot\n\n3. Drag a rectangle around a feature, and then click the feature's bottom\n value as seen on the 2d graph. This will log both the top, bottom\nand net height of the feature to the provided excel sheet\n(see documentation video)\n\n4. To log an 'N/A' value to the provided excel sheet, right click")
info.pack()

# Start the Tkinter event loop
root.mainloop()

print("Closing application...")