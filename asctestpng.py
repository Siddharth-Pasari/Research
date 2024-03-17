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
num=0

print("-----------------------------------------------------------------------")

def update_excel_with_data(data_measurements, file_path):
    """
    Inserts a list of data measurements into an Excel sheet.

    Parameters:
    - data_measurements: A list of tuples containing (area, mean, std_dev, min_val, max_val)
    - file_path: Path to the Excel file where the data is to be inserted
    """

    # Convert the list of tuples to a pandas DataFrame
    df = pd.DataFrame(data_measurements, columns=['Num','Top','Bottom'])
    
    # Open the Excel file and append the DataFrame
    with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
        # Get the last row with data in the existing sheet
        # If the file or sheet does not exist yet, it will start from the beginning
        try:
            startrow = writer.sheets['Sheet1'].max_row
        except KeyError:
            startrow = 0
        
        # If starting on a new sheet, write headers, otherwise skip them
        if startrow == 0:
            headers = True
        else:
            headers = False
        
        # Write the DataFrame to the Excel file
        df.to_excel(writer, sheet_name='Sheet1', startrow=startrow, index=False, header=headers)

# to convert from weird ASC values to microns
def convertToMicrons(value):
    microns = value - lowest_asc # adjusts for negative numbers
    microns = microns * (height_uM / (highest_asc - lowest_asc))
    return microns

def open_file():
    if not plt.fignum_exists:
        file_path = filedialog.askopenfilename(filetypes=[("ASC files", "*.ASC")])
        if file_path:
            process_file(file_path)
    else:
        print("Close current plot before opening a new one!")

def process_file(file_path):

    global num

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

    dr = dragrectangle.DragRectangle(ax, x_values, y_values, data)
    dr.connect()
    
    num=num+1

    top="ANTHONY FILL"

    bottom="ANTHONY FILL"

    path="ANTHONY FILL"

    data_measurements=(num, top, bottom)

    update_excel_with_data(data_measurements, path)

    # open plot
    plt.show()

    print(f"Plotted numpy array as image with colormap and scale")

# Create the GUI
root = tk.Tk()
root.title("ASC File Processor")

btn_open = tk.Button(root, text="Open ASC File", command=open_file)
btn_open.pack()

root.mainloop()
print("Closing application...")