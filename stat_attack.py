import os

from SPA import SPA 
from RS import RS


def interact():

    input_file = input("Enter the image file name with extension: ")
    while not os.path.exists(input_file):
        input_file = input("Invalid File Name \n Re-enter the file name with extension: ")


    choice = input("\nChoose options: \n 1. SPA Attack \n 2. RS Attack \n Enter Option: ")
    while choice != "1" and choice != "2":
       choice = input("Invalid Choice \nRe-enter option: ")  


    if choice == "1":
        print("Executing SPA Attack:")
        res, p_vals = SPA(input_file)
    else:
        print("Executing RS Attack:")
        res, p_vals = RS(input_file)


    match = ["R", "G", "B"]

    for chan in range(3):
        p = p_vals[chan]
        print("Results for channel:", match[chan])

        print("     Payload estimate is:", abs(p))

        # Specify a threshold
        threshold = 0.03

        if(p > threshold):
            print("     Stego Detected")            
        else:
            print("     Cover Detected")
    
    
interact()