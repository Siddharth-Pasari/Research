import numpy as np

from scipy.signal import find_peaks

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
'''# Assuming the peaks are arranged in a 2x2 array of 4x4 peaks
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
        peak_heights.append(peak_height)'''


# Find peaks in the data
peaks, _ = find_peaks(data.flatten(), prominence=3000)  # Adjust prominence threshold as needed

# Get heights of each peak
peak_heights = []
peak_indices = []

# Iterate over detected peaks
for peak_index in peaks:
    # Extract peak height
    peak_height = data.flatten()[peak_index]
    
    # Check if peak_index is close to any previously recorded peak
    is_close = False
    for prev_peak_index in peak_indices:
        if abs(peak_index - prev_peak_index) < 750:  # Adjust proximity threshold as needed
            is_close = True
            # If the current peak is higher than the previously recorded one, replace it
            if peak_height > peak_heights[-1]:
                peak_heights[-1] = peak_height
                peak_indices[-1] = peak_index
            break
    
    # If peak is not close to any previously recorded peak, add it
    if not is_close:
        peak_heights.append(peak_height)
        peak_indices.append(peak_index)

# Print the heights of each peak
print("Heights of each peak:")
print(peak_heights)