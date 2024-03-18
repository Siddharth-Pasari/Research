import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import math
import pandas as pd
num=0


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


class DragRectangle:
    def __init__(self, ax, x_values, y_values, data, path):
        self.ax = ax
        self.x_values = x_values
        self.y_values = y_values
        self.data = data
        self.path = path
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

        self.press_event = event
        self.rect.set_width(0)
        self.rect.set_height(0)
        self.rect.set_xy((event.xdata, event.ydata))
        self.ax.add_patch(self.rect)
        self.is_dragging = True

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
        
        print("Max, Min:", self.findImportantValues())

    def findImportantValues(self):
        global num

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
        
        # Convert list to numpy array for easier manipulation and finds bottom based on a slope threshold
        slicearr = np.array(max_list)
        differences = np.diff(slicearr)
        threshold = 0.005  # Adjust the threshold as needed

        if np.any(differences > threshold):
            bottom_index = np.argmax(differences > threshold)
            bottom_value = slicearr[bottom_index]
        else:
            bottom_value = np.nan
        
        num=num+1

        data_measurements = [(num, max_value, bottom_value)]

        print(data_measurements)

        update_excel_with_data(data_measurements, self.path)

        return max_value, bottom_value
