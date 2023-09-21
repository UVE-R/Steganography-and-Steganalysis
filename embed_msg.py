from primes import generatePrime
import os
from LSBClass import LSBRandom, LSBSimple, LSBMatching

def interact():

    chan = 0                # Choose which colour channel to modify
    delim = "<END>"         # Signify end of message
    seed_bits = 32          # Number of bits in the RNG seed
    output_file = "output.png"
    changes_file = "changes.png"
 

    # Get input file
    input_file = input("Enter the image file name with extension: ")
    while not os.path.exists(input_file):
        input_file = input("Invalid File Name \n Re-enter the file name with extension: ")
    
    # Choose between encoding and decoding
    choice = input("\nChoose options: \n 1. Encode image file \n 2. Decode the image file \n Enter Option: ")
    while choice != "1" and choice != "2":
       choice = input("Invalid Choice \nRe-enter option: ")    

    # Choose LSB method
    method = input("\nChoose method: \n 1. Simple LSB  \n 2. Randomised LSB  \n 3. LSB Matching \n Enter Option: ")
    while method != "1" and method != "2" and method != "3":
       method = input("Invalid method \nRe-enter option: ")    

    # Get message for encoding
    if choice == "1":
        payload = input("\nEnter message to encode in the image: ")

    # Get seed for decoding random LSB
    if method == "2" and choice == "2":
        while True:
            try:
                seed = int(input("\nEnter seed for decoding "))
            except ValueError:
                print("Invalid Seed")
            break

    # Get both seeds for decoding LSB matching
    if method == "3" and choice == "2":
        while True:
            try:
                seed1 = int(input("\nEnter first seed for decoding "))
            except ValueError:
                print("Invalid First Seed")
            break
        while True:
            try:
                seed2 = int(input("\nEnter second seed for decoding "))
            except ValueError:
                print("Invalid Second Seed")
            break


    # Carry out encoding/decoding
    if choice == "1":
        if method == "1":                     # Encode using simple LSB
            lsb_obj = LSBSimple(input_file, delim, chan)            
        elif method == "2":                   # Encode using random LSB
            seed = generatePrime(seed_bits)
            print("\nSeed used:", seed)
            lsb_obj = LSBRandom(input_file, seed, delim, chan)
        else:                                 # Encode using LSB matching
            seed1 = generatePrime(seed_bits)
            print("\nFirst Seed used:", seed1)
            seed2 = generatePrime(seed_bits)
            print("\nSecond Seed used:", seed2)
            lsb_obj = LSBMatching(input_file, seed1, seed2, delim, chan)

        lsb_obj.hide_data(payload, output_file)
        print("\nMessage encoded in", output_file)

    else:
        if method == "1":                       # Decode using simple LSB
            lsb_obj2 = LSBSimple(input_file, delim, chan)
        elif method == "2":                     # Decode using random LSB
            lsb_obj2 = LSBRandom(input_file, seed, delim, chan)
        else:                                   # Decode using LSB matching
            lsb_obj2 = LSBMatching(input_file, seed1, seed2, delim, chan)

        extracted_text = lsb_obj2.extract_payload()
        print("\nDecoded text is:\n", extracted_text)


    # Ask user if they want to show changes between cover and stego
    if choice == "1":
        changes = input("\nDo you want to highlight changes: \n 1. Yes  \n 2. No \n Enter choice: ")
        while changes != "1" and changes != "2":
            changes = input("Invalid choice \nRe-enter choice: ") 

        if changes == "1":
            lsb_obj.highlight_changes(input_file, changes_file)
            print("\nImage showing changes in", changes_file)
 

interact()



