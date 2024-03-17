import numpy as np

slicelist = [384.740997, 384.99588, 386.031158, 387.253784, 388.972321, 390.790375, 393.529938, 397.190125, 401.60376, 406.131714, 410.81781, 414.911011, 419.970184, 426.036469, 430.842621, 436.208954, 444.807465, 456.128784, 469.902771, 485.005402, 503.055054, 524.841736, 550.66687, 578.690918, 608.264099, 636.946899, 665.3797, 692.31842, 716.369019, 735.706482, 752.741577, 768.346558, 782.516235, 796.313782]

# Convert list to numpy array for easier manipulation
slicearr = np.array(slicelist)

# Calculate differences between consecutive values
differences = np.diff(slicearr)

# Find the index where the difference exceeds the threshold
threshold = 5  # Adjust the threshold as needed
bottom_index = np.argmax(differences > threshold)

# Get the value at the "bottom" index
bottom_value = slicearr[bottom_index]

print("Bottom value:", bottom_value)
