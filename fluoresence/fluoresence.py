import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import openpyxl

num = 0
box_x = 0
box_y = 0
step = 1

def update_excel_with_data(data_measurements, file_path, num):
    print(data_measurements, num)

    # Create a DataFrame with specified column names
    df = pd.DataFrame(data_measurements, columns=['Num', 'Area', 'Mean', 'StdDev', 'Min', 'Max'])

    # Open the Excel file and append the DataFrame
    with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
        # Get the last row with data in the existing sheet
        try:
            startrow = writer.sheets['Sheet1'].max_row
        except KeyError:
            startrow = 0

        # Determine if a new blank row should be inserted
        if (num-1) % 16 == 0 and startrow != 0:
            startrow += 1  # Increment startrow to insert data after the new blank row

        # Determine if headers need to be written
        if num == 1:
            headers = ['Num', 'Area', 'Mean', 'StdDev', 'Min', 'Max']
        else:
            headers = False

        # Preserve any existing data in the file by using startrow accordingly
        df.to_excel(writer, sheet_name='Sheet1', startrow=startrow, index=False, header=headers)


def convert_to_grayscale(image):
    # Ensure image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    pixels = image.load()
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            r, g, b = pixels[x, y]
            gray = int((r + g + b) / 3)
            pixels[x, y] = (gray, gray, gray)

    return image.convert('L')

def analyze_square(image, x, y):
    # Define the size of the rectangle region
    rectangle_width = 52
    rectangle_height = 47

    # Calculate the coordinates of the rectangle region
    half_width = rectangle_width / 2
    half_height = rectangle_height / 2
    x_start = max(0, x - half_width)
    y_start = max(0, y - half_height)
    x_end = min(image.width, x + half_width)
    y_end = min(image.height, y + half_height)

    # Extract the pixel values within the square region
    square_pixels = np.array(image.crop((x_start, y_start, x_end, y_end)), dtype=np.float32)

    # Calculate statistics of the square region
    area = (x_end - x_start) * (y_end - y_start)
    mean = np.mean(square_pixels)
    std_dev = np.std(square_pixels)
    min_val = np.min(square_pixels)
    max_val = np.max(square_pixels)

    return area, mean, std_dev, min_val, max_val

def get_file_path():
    global file_path
    file_path = filedialog.askopenfilename(initialdir="/", title="Select file",
                                           filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))
    if file_path:  # Check if a file was selected
        display_image(file_path)

def get_file_path2():
    global excel_path
    excel_path = filedialog.askopenfilename(initialdir="/", title="Select file",
                                            filetypes=(("Excel files", "*.xlsx"), ("all files", "*.*")))

def display_image(file_path):
    global img, tk_img, canvas  # Declare as global to access outside of the function
    img = Image.open(file_path)
    tk_img = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor='nw', image=tk_img)  # Display the image on the canvas
    canvas.config(scrollregion=canvas.bbox(tk.ALL))  # Update the scroll region to encompass the image

def print_coords1(event):
    global num
    # Open the image
    pil_image = Image.open(file_path)

    # Convert the image to grayscale
    grayscale_image = convert_to_grayscale(pil_image)

    # Analyze the grayscale square region
    area, mean, std_dev, min_val, max_val = analyze_square(grayscale_image, box_x, box_y)

    num += 1

    # List of data points (area, mean, std_dev, min_val, max_val)
    data_measurements = [(num, area, mean, std_dev, min_val, max_val)]

    update_excel_with_data(data_measurements, excel_path, num)

def move_box(event):
    global box_x, box_y, square
    if event.keysym == 'Left':
        box_x -= step
    elif event.keysym == 'Right':
        box_x += step
    elif event.keysym == 'Up':
        box_y -= step
    elif event.keysym == 'Down':
        box_y += step
    half_width = 52 / 2
    half_height = 47 / 2
    x0, y0 = box_x - half_width, box_y - half_height
    x1, y1 = box_x + half_width, box_y + half_height
    canvas.coords(square, x0, y0, x1, y1)

def print_coords(event):
    global square, canvas, file_path, box_x, box_y
    box_x, box_y = event.x, event.y
    half_width = 52 / 2
    half_height = 47 / 2
    x0, y0 = box_x - half_width, box_y - half_height
    x1, y1 = box_x + half_width, box_y + half_height
    if square:
        canvas.delete(square)  # Delete previous square
    square = canvas.create_rectangle(x0, y0, x1, y1, outline='#FFFF00', fill='')  # Draw new square

root = tk.Tk()
root.title('Image Viewer')

btn_load = tk.Button(root, text="Load Image", command=get_file_path)
btn_load.pack()

btn_load = tk.Button(root, text="Load excel", command=get_file_path2)
btn_load.pack()

canvas = tk.Canvas(root, width=1920, height=1080)  # You might want to adjust the size to fit your image properly
canvas.pack()

canvas.bind("<Button-1>", print_coords)  # Bind the button click to the canvas, not a label

canvas.bind("<Button-3>", print_coords1)  # Bind the button click to the canvas, not a label

canvas.focus_set()  # Set focus to the canvas so it can receive key events
canvas.bind("<Key>", move_box)  #


square = None  # Variable to hold square object



root.mainloop()