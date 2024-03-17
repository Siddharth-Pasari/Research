import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import openpyxl

num=0

def update_excel_with_data(data_measurements, file_path):
    """
    Inserts a list of data measurements into an Excel sheet.

    Parameters:
    - data_measurements: A list of tuples containing (area, mean, std_dev, min_val, max_val)
    - file_path: Path to the Excel file where the data is to be inserted
    """

    # Convert the list of tuples to a pandas DataFrame
    df = pd.DataFrame(data_measurements, columns=['Num','Area', 'Mean', 'StdDev', 'Min', 'Max'])
    
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

def convert_to_grayscale(image):
    # Ensure image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    pixels = image.load()
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            r, g, b = pixels[x, y]
            gray = int((r+g+b)/3)
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
                                           filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))

def display_image(file_path):
    global img, tk_img, canvas  # Declare as global to access outside of the function
    img = Image.open(file_path)
    tk_img = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor='nw', image=tk_img)  # Display the image on the canvas
    canvas.config(scrollregion=canvas.bbox(tk.ALL)) # Update the scroll region to encompass the image

def print_coords1(event):

    global num
    # Open the image
    pil_image = Image.open(file_path)

    # Convert the image to grayscale
    grayscale_image = convert_to_grayscale(pil_image)

    # Analyze the grayscale square region
    area, mean, std_dev, min_val, max_val = analyze_square(grayscale_image, x, y)
    
    num=num+1

    # Print the results
    print("Num:", num)
    print("Area:", area)
    print("Mean:", mean)
    print("Standard Deviation:", std_dev)
    print("Minimum Value:", min_val)
    print("Maximum Value:", max_val)

    # List of data points (area, mean, std_dev, min_val, max_val)
    data_measurements = [(num,area, mean, std_dev, min_val, max_val)]

    update_excel_with_data(data_measurements, excel_path)


def print_coords(event):
    global square, canvas, file_path,x,y
    x, y = event.x, event.y
    half_width = 52 / 2
    half_height = 47 / 2
    x0, y0 = x - half_width, y - half_height
    x1, y1 = x + half_width, y + half_height
    if square:
        canvas.delete(square)  # Delete previous square
    square = canvas.create_rectangle(x0, y0, x1, y1, outline='#FFFF00', fill='')  # Draw new square
    print(f'X: {x}, Y: {y}')  # Print coordinates

    

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


square = None  # Variable to hold square object



root.mainloop()