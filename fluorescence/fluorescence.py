import tkinter as tk
from tkinter import filedialog

import sys
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
from openpyxl.styles import Font

num = 0
box_x = 0
box_y = 0
step = 1
title = ""
ftnum=16

def update_excel_with_data(data_measurements, file_path, num):
    print(data_measurements, num)

    # Create a DataFrame with specified column names
    df = pd.DataFrame(data_measurements, columns=['Num', 'Area', 'Mean', 'StdDev', 'Min', 'Max'])

    with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
        try:
            startrow = writer.sheets['Sheet1'].max_row
        except KeyError:
            startrow = 0

        if (num-1) % ftnum == 0 and startrow != 0:  # Assuming ftnumber is defined somewhere else
            startrow += 1

        if num == 1:
            # Write the title above the headers if this is the first set of measurements
            ws = writer.sheets['Sheet1']    
            ws.insert_rows(startrow, amount=1)  # Insert a blank row above the title
            ws.cell(row=startrow+1, column=1, value=title).font = Font(bold=True)  # Write the title and make it bold
            headers = ['Num', 'Area', 'Mean', 'StdDev', 'Min', 'Max']
            # Increment startrow so headers will be below the title
            startrow += 1

        else:
            headers = False
        
        # Write the DataFrame to the sheet at the updated starting row
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
    global file_path, ftnum, num, title
    file_path = filedialog.askopenfilename(initialdir="/", title="Select file",
                                           filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))
    if file_path:  # Check if a file was selected
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
                num = int(startnum.get())
            except:
                num=0
        else:
            num=0
        title = str(titlet.get())

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


def nafunc(event):
    global num
   
    num += 1

    # List of data points (area, mean, std_dev, min_val, max_val)
    data_measurements = [(num,  "NoVal",  "NoVal",  "NoVal",  "NoVal",  "NoVal")]

    update_excel_with_data(data_measurements, excel_path, num)


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
    try:
        canvas.coords(square, x0, y0, x1, y1)
    except:
        pass


def print_coords(event):
    global square, canvas, file_path, box_x, box_y
    box_x, box_y = event.x, event.y
    print(box_x, box_y)
    half_width = 52 / 2
    half_height = 47 / 2
    x0, y0 = box_x - half_width, box_y - half_height
    x1, y1 = box_x + half_width, box_y + half_height
    if square:
        canvas.delete(square)  # Delete previous square
    square = canvas.create_rectangle(x0, y0, x1, y1, outline='#FFFF00', fill='')  # Draw new square


def main():
    global startnum
    global ftnumt
    global titlet
    global level_var
    global canvas
    global square

    root = tk.Tk()
    root.title('Image Viewer')

    canvas = tk.Canvas(root, width=3840, height=2060)  # You might want to adjust the size to fit your image properly
    canvas.pack()

    window=tk.Toplevel()
    window.title('Info')
    window.geometry('300x400')

    startnum = tk.Entry(window)
    startnum.insert(0, "last number recorded (0)")
    startnum.pack()

    ftnumt= tk.Entry(window)
    ftnumt.insert(0, "# of features (16)")
    ftnumt.pack()

    titlet= tk.Entry(window)
    titlet.insert(0, "name of file (only if starting new)")
    titlet.pack()

    level_var = tk.IntVar()

    file_path_label = tk.Button(window, text="Open Excel File", command=get_file_path2)
    file_path_label.pack()

    btn_open1 = tk.Button(window, text="Open Image  File", command=get_file_path)
    btn_open1.pack()

    btn_open = tk.Button(window, text="Exit Program", command=sys.exit)
    btn_open.pack()

    canvas.bind("<Button-1>", print_coords)  # Bind the button click to the canvas, not a label

    canvas.bind("<Button-2>", nafunc)  # Bind the button click to the canvas, not a label

    canvas.bind("<Button-3>", print_coords1)  # Bind the button click to the canvas, not a label

    canvas.focus_set()  # Set focus to the canvas so it can receive key events
    canvas.bind("<Key>", move_box)  #

    square = None  # Variable to hold square object

    root.mainloop()

    print("Closing application...")


if __name__ == "__main__":
    main()