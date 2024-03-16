import os
import numpy as np
import openpyxl

# Load the ASC file and skip rows until "RAW_DATA 3 2400400"
with open('p2.ASC', 'r') as file:
    lines = file.readlines()
    start_index = lines.index("RAW_DATA\t3\t2400400\t\n") + 1

# Process the data and format into a table
data = np.loadtxt('p2.ASC', skiprows=start_index)

# Create a table with a new cell in the row for each space or row in the ASC file
table = []
row = []
for row_values in data:
    for value in row_values:
        if len(row) < 6001:
            row.append(value)
        else:
            table.append(row)
            row = [value]

# Add the last row to the table
if row:
    table.append(row)

# Specify the file name for the XLSX file
xlsx_file_name = 'p2_formatted.xlsx'

# Check if the XLSX file already exists
if os.path.exists(xlsx_file_name):
    os.remove(xlsx_file_name)  # Delete the existing file

# Create a new Excel workbook
workbook = openpyxl.Workbook()
sheet = workbook.active

# Determine the min and max values in the dataset
data_min = np.min(data)
data_max = np.max(data)

# Define cell size (in points) for square cells
base_cell_size = 10  # Adjust as needed

# Write the formatted table to the Excel sheet with grayscale gradient fill colors and resized cells
for row_idx, row_data in enumerate(table, start=1):
    for col_idx, cell_data in enumerate(row_data, start=1):
        cell = sheet.cell(row=row_idx, column=col_idx, value=cell_data)

        # Calculate the grayscale value based on the cell's value
        grayscale_value = ((cell_data - data_min) / (data_max - data_min))

        # Convert grayscale value to RGB format
        rgb_value = int(grayscale_value * 255)

        # Set RGB values to create a grayscale gradient from black to white
        fill_color = f"{rgb_value:02X}{rgb_value:02X}{rgb_value:02X}"
        cell.fill = openpyxl.styles.PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

        # Adjust column width to make the cell smaller
        sheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = base_cell_size / 60

# Save the Excel workbook to a file
workbook.save(xlsx_file_name)

print(f"Formatted table with grayscale gradient fill colors and square cells written to '{xlsx_file_name}'")
