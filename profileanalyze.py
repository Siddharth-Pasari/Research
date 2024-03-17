import numpy as np

import numpy as np

# Skip the first few lines of the file until the data starts
with open('p2.ASC', 'r') as file:
    lines = file.readlines()
    for i, line in enumerate(lines):
        if line.startswith("RAW_DATA\t3\t2400400\t"):
            start_index = i + 1
            break

# Load the data using genfromtxt and skip the header lines
data = np.genfromtxt('p2.ASC', skip_header=start_index)

# Rest of the code remains the same...

# Assuming the peaks are arranged in a 2x2 array of 4x4 peaks
num_peaks = 64
peak_heights = []

# Iterate over the peaks and extract them
for i in range(num_peaks):
    # Determine the coordinates of the peak in the 2x2 array
    row = i // 4
    col = i % 4
    
    # Extract the peak data from the corresponding region in the data array
    peak_data = data[row * 100:(row + 1) * 100, col * 1500:(col + 1) * 1500]
    
    # Check if peak_data is not empty before computing the maximum value
    if peak_data.size > 0:
        # Analyze the peak data (e.g., compute peak height, area, etc.)
        peak_height = np.max(peak_data)
        peak_heights.append(peak_height)

# Analyze the peak heights
if peak_heights:
    avg_peak_height = np.mean(peak_heights)
    max_peak_height = np.max(peak_heights)
    min_peak_height = np.min(peak_heights)
else:
    print("No valid peaks found in the data.")

print(avg_peak_height, max_peak_height, min_peak_height)