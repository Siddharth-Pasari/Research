import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import math
import pandas as pd
import openpyxl
from openpyxl.styles import Font

title="TITLE"
def update_excel_with_data(data_measurements, file_path, num):
    print(data_measurements, num)

    # Create a DataFrame with specified column names
    df = pd.DataFrame(data_measurements, columns=['Num', 'Top', 'Bottom', 'Difference'])

    with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
        try:
            startrow = writer.sheets['Sheet1'].max_row
        except KeyError:
            startrow = 0

        if (num-1) % ftnumber == 0 and startrow != 0:  # Assuming ftnumber is defined somewhere else
            startrow += 1

        if num == 1:
            # Write the title above the headers if this is the first set of measurements
            ws = writer.sheets['Sheet1']    
            ws.insert_rows(startrow, amount=1)  # Insert a blank row above the title
            ws.cell(row=startrow+1, column=1, value=title).font = Font(bold=True)  # Write the title and make it bold
            headers = ['Num', 'Top', 'Bottom', 'Difference']
            # Increment startrow so headers will be below the title
            startrow += 1

        else:
            headers = False
        
        # Write the DataFrame to the sheet at the updated starting row
        df.to_excel(writer, sheet_name='Sheet1', startrow=startrow, index=False, header=headers)

def plot_2d_slice(height_values, max_val, excel_path):
    
    """
    Plots a 2D representation of a data slice given height values.
    A vertical line and the y coordinate of the line associated with the current x-coordinate
    of the mouse are displayed as the mouse moves. Clicking records the y-value.

    Parameters:
    - height_values: 1D array of height values
    """
    x_values = np.arange(len(height_values))

    fig, ax = plt.subplots()
    ax.plot(x_values, height_values, 'o-')

    # Set labels and title
    ax.set(xlabel='X', ylabel='Height',
           title='2D Representation of Data Slice')
    ax.grid()

    # Marker and line which will follow the mouse
    marker, = ax.plot([0], [height_values[0]], marker='o', color="red", zorder=5)
    cursor_line = ax.axvline(x=0, color='red', linestyle='--', lw=1)

    # Text annotation for displaying the y-value
    y_value_annotation = ax.annotate('', xy=(0, 0), xytext=(10, 10),
                          
           textcoords="offset points",
                                     bbox=dict(boxstyle="round4", fc="cyan", ec="black", lw=1))

    # Variable to hold the y-value
    bottom_val = None

    def on_move(event):
        if not event.inaxes:
            return
        x, y = event.xdata, event.ydata
        nearest_x_index = np.clip(np.searchsorted(x_values, x), 1, len(x_values) - 1)
        x0, x1 = x_values[nearest_x_index - 1], x_values[nearest_x_index]
        y0, y1 = height_values[nearest_x_index - 1], height_values[nearest_x_index]
        distance_to_x0 = abs(x - x0)
        distance_to_x1 = abs(x - x1)
        index = nearest_x_index - 1 if distance_to_x0 < distance_to_x1 else nearest_x_index

        # Update the position of the marker and the vertical line
        marker.set_data([x_values[index]], [height_values[index]])
        cursor_line.set_xdata(x_values[index])

        # Update the annotation text and position
        y_value_annotation.set_text(f'({x_values[index]:.2f}, {height_values[index]:.2f})')
        y_value_annotation.xy = (x_values[index], height_values[index])

        plt.draw()

    def on_click(event):
        global number
        number=number+1
        if not event.inaxes:
            return
        nonlocal bottom_val
        bottom_val = height_values[np.clip(np.searchsorted(x_values, event.xdata), 1, len(x_values) - 1) - 1]

        difference = max_val - bottom_val

        data_measurements = [(number, max_val, bottom_val, difference)]

        update_excel_with_data(data_measurements, excel_path, number)

        plt.close()

    fig.canvas.mpl_connect('motion_notify_event', on_move)
    fig.canvas.mpl_connect('button_press_event', on_click)

    ax.autoscale_view()  # Auto rescale the view after adding the marker
    plt.show()


class DragRectangle:

    def __init__(self, ax, x_values, y_values, data, path, num, ftnum, titlet):
        global number, ftnumber, title
        self.ax = ax
        self.x_values = x_values
        self.y_values = y_values
        self.data = data
        self.path = path
        self.num = num
        number=num
        self.ftnum=ftnum
        ftnumber=ftnum
        title=titlet
        self.rect = Rectangle((0, 0), 0, 0, linewidth=1, edgecolor='r', facecolor='none')
        self.is_dragging = False
        self.press_event = None
        self.selected_indices = []

    def connect(self):
        self.cidpress = self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.ax:
            return

        if event.button == 3:  # Right-click event
            self.on_right_click(event)
            return

        self.press_event = event
        self.rect.set_width(0)
        self.rect.set_height(0)
        self.rect.set_xy((event.xdata, event.ydata))
        self.ax.add_patch(self.rect)
        self.is_dragging = True

    def on_right_click(self, event):
        global number
        number=number+1
        data_measurements = [(self.num, "N/A", "N/A", "N/A")]

        update_excel_with_data(data_measurements, self.path, number)

    def on_motion(self, event):
        if not self.is_dragging or event.inaxes != self.ax:
            return

        width = event.xdata - self.press_event.xdata
        height = event.ydata - self.press_event.ydata

        self.rect.set_width(width)
        self.rect.set_height(height)
        self.ax.figure.canvas.draw()

    def on_release(self, event):
        if not self.is_dragging or event.inaxes != self.ax:
            return

        self.is_dragging = False
        self.ax.figure.canvas.draw()

        # Get indices of selected area
        x0, y0 = self.press_event.xdata, self.press_event.ydata
        x1, y1 = event.xdata, event.ydata

        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0

        x_indices = [int(i) for i in range(math.ceil(x0), math.floor(x1))]
        y_indices = [int(i) for i in range(math.ceil(y0), math.floor(y1))]

        # Get values within selected area
        self.selected_indices = []
        for j in x_indices:
            row_values = [self.data[j, i] for i in y_indices]
            self.selected_indices.append(row_values)

        slicelist=[]
        
        self.findImportantValues()

    def findImportantValues(self):
        if not self.selected_indices:
            return np.nan, np.nan  # Return NaN values if selected_indices is empty

        # finds the row containing the peak
        max_value = float('-inf')
        max_list = None
        for sublist in self.selected_indices:
            sublist_max = max(sublist)
            if sublist_max > max_value:
                max_value = sublist_max
                max_list = sublist
        
        if max_list is None:
            return np.nan, np.nan  # Return NaN values if max_list is None

        max_index = np.argmax(max_list)
        
        '''# Convert list to numpy array for easier manipulation and finds bottom based on a slope threshold
        slicearr = np.array(max_list)
        differences = np.diff(slicearr)
        threshold = 0.005  # Adjust the threshold as needed

        if np.any(differences > threshold):
            bottom_index = np.argmax(differences > threshold)
            bottom_value = slicearr[bottom_index]
        else:
            bottom_value = np.nan'''
        

        plot_2d_slice(max_list, max_value, self.path)
