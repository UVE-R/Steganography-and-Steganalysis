import cv2
import numpy as np


# LSB embedding by placing bits at the start of the file
class LSBSimple:

    def __init__(self, file, delim = "<END>", chan = 0):
        self.filename = file 
        self.im = cv2.imread(file)
        self.chan = chan        # Determine which channel in the image to insert to 
        self.delim = delim      # Signifies end of message
        self.width = self.im.shape[1]
        self.height = self.im.shape[0]   


    def str_to_bin(self, msg):
        return "".join(format(ord(char), '08b') for char in msg)


    def int_to_bin(self, num):
        return format(num, "b")


    # Save self.im
    def save_im(self, output_file):
        cv2.imwrite(output_file, self.im)


    # Compare the original image file to the current self.im by counting the number of differing pixels
    def compare_imgs(self):

        img_old = cv2.imread(self.filename)

        if img_old.shape != self.im.shape:
            raise Exception("Image Dimension Error")

        difs = 0 
        for row in range(self.height):
            for col in range(self.width):
                if not (img_old[row][col] == self.im[row][col]).all():
                    difs += 1
        

    # Display the changes between the current self.im and the image in the file by colouring the 
    # differing pixels red
    def highlight_changes(self, comparison_file, output_file):

        im_comp = cv2.imread(comparison_file) 

        if im_comp.shape != self.im.shape:
            raise Exception("Image Dimension Error")
        
        im_out = cv2.imread(self.filename)
        
        for row in range(self.height):
            for col in range(self.width):
                if not (im_comp[row][col] == self.im[row][col]).all():
                    im_out[row][col][0] = 0
                    im_out[row][col][1] = 0
                    im_out[row][col][2] = 255

        cv2.imwrite(output_file, im_out)


    # Encodes the message into self.im and saves the image in the output_file
    def hide_data(self, msg, output_file):

        msg_bin = self.str_to_bin(msg + self.delim)     # Add on delimiter to signify end of message

        if len(msg_bin) > self.height * self.width:
            raise ValueError("Payload too large")
               
        self.encode(msg_bin)

        self.save_im(output_file)


    def change_lsb(self, pixel, bit):
        return ((pixel >> 1) << 1) + int(bit)


    # Carry out LSB embedding
    def encode(self, msg_bin):
        row = 0; col = 0  

        for bit in msg_bin:
            self.im[row][col][self.chan] = self.change_lsb(self.im[row][col][self.chan], bit)     # Modify LSB    

            col += 1
            if col == self.width:       # Move to next row
                col = 0
                row += 1


    # Extract the encoded message from self.im
    def extract_payload(self):

        msg_buf = ""        # Store current decoded message
        str_buf = ""        # Stores current character's binary 

        for row in range(self.height):
            for col in range(self.width):
                str_buf = str_buf + self.int_to_bin(self.im[row][col][self.chan])[-1]       # Add on bit to character's binary

                if len(str_buf) == 8:       # Once we have the 8 bits for the character, we turn it back into the character
                    msg_buf = msg_buf + chr(int(str_buf, 2))
                    str_buf = ""

                # Check if we have reached the deliminator
                if len(msg_buf) >= len(self.delim) and self.delim == msg_buf[ -1 * len(self.delim) : ]:          
                    return "".join(msg_buf[ : -1 * len(self.delim)])     



# LSB embedding by randomly placing bits
class LSBRandom(LSBSimple):
    def __init__(self, file, seed, delim = "<END>", chan = 0):
        super().__init__(file, delim, chan) 
        self.seed = seed        # Seed for RNG


    # Carry out LSB insertion
    def encode(self, msg_bin):
        rng = np.random.RandomState(self.seed)

        # pix_lst[i][j] is 1 if the (i,j) pixel in the image has been used for the payload
        # Needed to stop modifying the same pixel more than once
        pix_lst = [[0 for _ in range(self.width)] for _ in range(self.height)]

        row = rng.randint(0, self.height)
        col = rng.randint(0, self.width)

        for bit in msg_bin:            
            # Find an unmodified pixel
            while pix_lst[row][col] == 1:
                row = rng.randint(0, self.height)
                col = rng.randint(0, self.width)
            pix_lst[row][col] = 1

            self.im[row][col][self.chan] = self.change_lsb(self.im[row][col][self.chan], bit)           # Modify LSB


    # Extract the encoded message from self.im
    # Same method for storing the string as in the super-class
    def extract_payload(self):
        rng = np.random.RandomState(self.seed)
        pix_lst = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        msg_buf = ""
        str_buf = ""

        for _ in range(self.height):
            for _ in range(self.width):

                row = rng.randint(0, self.height)
                col = rng.randint(0, self.width)
                while pix_lst[row][col] == 1:
                    row = rng.randint(0, self.height)
                    col = rng.randint(0, self.width)
                pix_lst[row][col] = 1

                str_buf = str_buf + self.int_to_bin(self.im[row][col][self.chan])[-1]

                if len(str_buf) == 8:
                    msg_buf = msg_buf + chr(int(str_buf, 2))
                    str_buf = ""

                if len(msg_buf) >= len(self.delim) and self.delim == msg_buf[ -1 * len(self.delim) : ]:
                    return "".join(msg_buf[ : -1 * len(self.delim)])  



# LSB matching by randomly placing bits
class LSBMatching(LSBRandom):

    def __init__(self, file, seed, embed_seed, delim = "<END>", chan = 0):
        super().__init__(file, seed, delim = "<END>", chan = 0)
        self.embed_rng = np.random.RandomState(embed_seed)  


    def change_lsb(self, pixel, bit):
        lsb = self.int_to_bin(pixel)[-1]
        change = 0
        if(lsb != bit):
            change = self.embed_rng.choice([-1, 1])      # Choose to randomly add 1 or -1

        return pixel + change
        
