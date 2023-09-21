# SPA attack for LSB embedding
# Using paper: https://ieeexplore.ieee.org/document/1206706

import cv2
from cmath import sqrt


# Load the image and calculate P for a specific channel
def gen_P(file_name, chan):    

    im = cv2.imread(file_name)
    signal = im[:,:,chan].tolist()
    rows, cols, _ = im.shape

    res = []

    # Pairs of pixels horizontally adjacent
    for row in range(rows):
        for col in range(cols - 1):
            res.append((signal[row][col], signal[row][col + 1]))

    
    # Pairs of pixels vertically adjacent
    for col in range(cols):
        for row in range(rows - 1):        
            res.append((signal[row][col], signal[row + 1][col]))
    

    return res


# Run the SPA attack on a given file
def SPA(file_name):    

    match = ["R", "G", "B"]
    stego_detected = False
    p_vals = []       # Holds p values calculated for each channel

    j = 30              # May need changing

    for chan in range(3):

        # Generate the multiset P, containing the sample tuples
        P_multiset = gen_P(file_name, chan)

        C_0 = 0         # Number of sample pairs whose values which which differ by 0 in the most significant 7 bits
        C_alpha = 0     # Number of sample pairs whose values which which differ by (j+1) in the most significant 7 bits
        D_0 = 0         # Number of sample pairs whose values which differ by 0
        D_alpha = 0     # Number of sample pairs whose values which differ by 2j + 2
        X_beta = 0      # Number of sample pairs of the form: (2k - 2m - 1, 2k) or (2k, 2k - 2m - 1), for each 0 <= m <= j
        Y_beta = 0      # Number of sample pairs of the form: (2k + 1, 2k - 2m) or (2k - 2m, 2k + 1), for each 0 <= m <= j
        
        for (u, v) in P_multiset:
            # Calculate cardinality for the C sets
            if((u >> 1) == (v >> 1)):
                C_0 += 1
            elif (abs((u >> 1) - (v >> 1)) == j+1):
                C_alpha += 1

            # Calculate cardinality for the D sets
            if(u == v):
                D_0 += 1
            elif (abs(u - v) == 2*j + 2):
                D_alpha += 1

            # Calculate cardinality for X and Y
            for m in range(j + 1):
                if(abs(u - v) == 2*m + 1):
                    if (v % 2 == 0 and u < v) or (v % 2 == 1 and u > v):
                        X_beta += 1
                    elif (v % 2 == 0 and u > v) or (v % 2 == 1 and u < v):
                        Y_beta += 1

        # Using the formula (18) from the paper
        a = 2*C_0 - C_alpha
        b = -2 * (2*D_0 - D_alpha + 2*(Y_beta - X_beta))
        c = 4 * (Y_beta - X_beta)

        root_1 = (-b + sqrt(b**2 - 4*a*c)) / (2*a)
        root_2 = (-b - sqrt(b**2 - 4*a*c)) / (2*a)

        # p is the smallest root
        p = min(root_1.real, root_2.real)

        p_vals.append(p)

        # Specify a threshold
        threshold = 0.05
        if(p > threshold):
            stego_detected = True    

    return (stego_detected, p_vals)

