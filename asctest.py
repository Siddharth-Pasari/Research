import os
import numpy as np
import openpyxl

# Set the size of the image to build the sheet more accurately and convert these weird numbers to actual height data
height_uM = 9.899
data_x = 6001
x_uM = 3960
data_y = 100
y_uM = 3051

# Load the ASC file and skips the rows before the actual data
with open('p2.ASC', 'r') as file:
    lines = file.readlines()
    start_index = lines.index("RAW_DATA\t3\t2400400\t\n") + 1

# Process the data and format into a table
data = np.loadtxt('p2.ASC', skiprows=start_index)

table = []
row = []
for row_values in data:
    for value in row_values:
        if len(row) < 6001: # According to the ASC file, the width is 6001
            row.append(value)
        else:
            table.append(row)
            row = [value]

if row:
    table.append(row) # for the last row

# Build XLSX file and replace if it already exists
xlsx_file_name = 'p2_visualizer.xlsx'

if os.path.exists(xlsx_file_name):
    os.remove(xlsx_file_name)

workbook = openpyxl.Workbook()
sheet = workbook.active

# Formatting stuff (colors of cells, size of cells) solely for visualization purposes
data_min = np.min(data)
data_max = np.max(data)

for row_idx, row_data in enumerate(table, start=1):
    for col_idx, cell_data in enumerate(row_data, start=1):
        cell = sheet.cell(row=row_idx, column=col_idx, value=cell_data)

        # Calculate the grayscale value based on the cell's value and applies that to the XLSX file
        grayscale_value = ((cell_data - data_min) / (data_max - data_min))

        rgb_value = int(grayscale_value * 255)

        fill_color = f"{rgb_value:02X}{rgb_value:02X}{rgb_value:02X}"
        cell.fill = openpyxl.styles.PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

        # sets size of spreadsheet columns to match the appropriate proportions (x10 because minimum column width is around 0.1)
        sheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = 10 * (x_uM / y_uM) / (data_x/data_y)

        # sets size of spreadsheet rows also because minimum column width but proportions need to be right
        # kind of slows it down a bit but i cant think of a better way rn. if you go below like 0.l or smthn it dosent show the column at all
        for row_num in range(1, data_y + 1):
            sheet.row_dimensions[row_num].height = 10

# save the XLSX file!!
workbook.save(xlsx_file_name)

print(f"Formatted table with grayscale gradient fill colors and square cells written to '{xlsx_file_name}'")
