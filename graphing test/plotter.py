import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog
import pandas as pd

root = tk.Tk()
root.withdraw()

path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])

data_df = pd.read_excel(path)
data_nl = data_df.values.T.tolist()
sections = [(i + 1, data_nl[0][i - 1]) for i, value in enumerate(data_nl[0]) if value == "Num"]

root.deiconify()

selected_value = [sections[0]]  # Use a list to make it mutable

def update_selected_value(choice):
    matching_sections = [section for section in sections if section[1] == choice]
    selected_value[0] = matching_sections[0] if matching_sections else (None, None)

options = [section[1] for section in sections]

dropdown_menu = tk.OptionMenu(root, tk.StringVar(root, value=options[0]), *options, command=update_selected_value)
dropdown_menu.pack()

def get_section_differences():
    difference_list = [[]]
    val = selected_value[0][0]

    while data_nl[3][val] != "Difference" and val + 1 < len(data_nl[3]): # This would indicate the section ended

        if pd.isna(data_nl[3][val]):
            difference_list.append([])
        else:
            if (data_nl[3][val] == 'No Value'):
                difference_list[-1].append(0)
            else: difference_list[-1].append(data_nl[3][val])

        val += 1

    print(difference_list)

    return difference_list[:-2] # Remove the two blank entries

def generate_scatter_plot(difference_list):
    ftnum = len(difference_list[0]) # This is the number of features per repetition

    sums = [0] * ftnum
    counts = [0] * ftnum

    for sublist in difference_list:
        for index in range(len(sublist)):
            sums[index] += sublist[index]
            counts[index] += 1

    y_values = [sums[i] / counts[i] if counts[i] > 0 else float('nan') for i in range(ftnum)]
    x_values = np.arange(len(y_values))

    fig, axs = plt.subplots()
    axs.scatter(x_values, y_values, label='Data Points')

    for x in x_values:
        axs.axvline(x=x, color='gray', linestyle='--', linewidth=0.5)

    if len(x_values) > 1:
        coefficients = np.polyfit(x_values, y_values, 1)
        trend_line = np.poly1d(coefficients)
        axs.plot(x_values, trend_line(x_values), color='red', linestyle='-', linewidth=1, label='Trend Line')

    axs.set_xlabel('Feature Number')
    axs.set_ylabel('Average Height')
    axs.set_title('Scatter Plot of Logged Features')
    axs.legend()
    axs.yaxis.grid(True)

    plt.show()

def graph_data():
    difference_list = get_section_differences()
    generate_scatter_plot(difference_list)

tk.Button(root, text="Generate Scatter Plot", command=graph_data).pack()

root.mainloop()
