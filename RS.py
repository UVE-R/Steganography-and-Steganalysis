# RS attack for LSB embedding
# Using paper: https://ieeexplore.ieee.org/document/1206706

import cv2
from cmath import sqrt


# Load the image and extract consecutive n pixels horizontally and vertically into a group,
# returning 2 groups with one group having the LSB's flipped
def split_img(file_name, chan, n):    

    im = cv2.imread(file_name)
    signal = im[:,:,chan].tolist()
    rows, cols, _ = im.shape

    res = []
    res_flipped = []
    temp_pix = []

    # Pairs of pixels horizontally adjacent
    for row in range(rows):
        for col in range(cols - n + 1):
            temp_pix.append(signal[row][col])

            if(len(temp_pix) == n):
                res.append(temp_pix)
                res_flipped.append([(x^1) for x in temp_pix])
                temp_pix = []

    
    # Pairs of pixels vertically adjacent
    for col in range(cols):
        for row in range(rows - n + 1):        
            temp_pix.append(signal[row][col])

            if(len(temp_pix) == n):
                res.append(temp_pix)
                res_flipped.append([(x^1) for x in temp_pix])
                temp_pix = []
    
    return (res, res_flipped)


# Calculate discrimination function f for a given group
def f(arr):
    acc = 0

    for i in range(1, len(arr)):
        acc += abs(arr[i] - arr[i-1])

    return acc


# Apply a given mask M to a group G
def apply_mask(G, M):
    
    for i in range(len(G)):
        if(M[i] == 1):
            G[i] = G[i] ^ 1                 # Mask of 1 flips the LSB

        elif (M[i] == -1):
            G[i] = ((G[i] + 1) ^ 1) - 1     # Use formula given in paper for mask of -1

    return G
        

# Calculate the cardinalities of R and S for a given group and mask, returning |R| - |S|
def get_values(groups, M):
    R = 0; S = 0

    for G in groups:

        fG = f(G)
        fFmG = f(apply_mask(G, M))     

        if(fFmG > fG):
            R += 1
        elif (fFmG < fG):
            S += 1     

    return (R - S)
    

def RS(file_name):    

    match = ["R", "G", "B"]
    stego_detected = False
    p_vals = []       # Holds p values calculated for each channel

    M = [0, 1, 1, 0]
    M_neg = [(-1 * x) for x in M]

    for chan in range(3):    

        # Need 2 copies of the groups and groups with the LSB's flipped
        # Because get_values modifies the group passed in
        (groups1, groups_flipped1) = split_img(file_name, chan, len(M))
        (groups2, groups_flipped2) = split_img(file_name, chan, len(M))


        # Calculate values needed in the quadratic
        d0 = get_values(groups1, M)
        d0_neg = get_values(groups2, M_neg)
        d1 = get_values(groups_flipped1, M)
        d1_neg = get_values(groups_flipped2, M_neg)


        a = 2 * (d1 + d0)
        b = d0_neg - d1_neg - d1 - (3 * d0)
        c = d0 - d0_neg   

        # Avoid division by zero
        if(a == 0):
            a = 1

        root_1 = (-b + sqrt(b**2 - 4*a*c)) / (2*a)
        root_2 = (-b - sqrt(b**2 - 4*a*c)) / (2*a)


        # x is the root with the smallest absolute value
        if(abs(root_1.real) > abs(root_2.real)):
            x = root_2.real
        else:
            x = root_1.real

        p = x / (x - 0.5)

        p_vals.append(p)

        # Specify a threshold
        threshold = 0.03
        if(p > threshold):
            stego_detected = True        


    return (stego_detected, p_vals)
        
 
