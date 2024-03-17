import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import math

class DragRectangle:
    def __init__(self, ax, x_values, y_values, data):
        self.ax = ax
        self.x_values = x_values
        self.y_values = y_values
        self.data = data
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

        # finds the row containing the peak
        max_value = float('-inf')
        max_list = None
        for sublist in self.selected_indices:
            sublist_max = max(sublist)
            if sublist_max > max_value:
                max_value = sublist_max
                max_list = sublist
        
        max_index = np.argmax(max_list)
        
        # Convert list to numpy array for easier manipulation and finds bottom based on a slope threshold
        slicearr = np.array(max_list)
        differences = np.diff(slicearr)
        threshold = 0.03  # Adjust the threshold as needed

        if np.any(differences > threshold):
            bottom_index = np.argmax(differences > threshold)
            bottom_value = slicearr[bottom_index]
        else:
            bottom_value = np.nan

        return max_value, bottom_value