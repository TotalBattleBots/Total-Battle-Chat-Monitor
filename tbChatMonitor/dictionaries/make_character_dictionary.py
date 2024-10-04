import sys
import os

unicode_ranges = [
    # Ascii and Extended (Turkish, etc)
    range(0x0001, 0x0180),
    # Korean 1
    range(0xAC00,0xD7AF + 1),
    # Korean 2
    range(0x1100,0x11FF+1),
    # Korean 3
    range(0x3130, 0x3188+1),
    # Russian 1
    range(0x0400, 0x052F + 1),
    # Russian 2
    range(0x2DE0, 0x2DFF + 1),
    # Russian 3
    range(0xa640, 0xA69F + 1),
#    # Russian 4, 
    range(0x1c80, 0x1c8f + 1),
    # Emoji
    range(0x1F300,0x1F6FF+1),

    # Hebrew 1
    range(0x0590,0x05FF+1),
    # Hebrew 2
    range(0xFB1D,0xFB4F+1),
    ]

if __name__ == '__main__':

    with open("single_char_dictionary.txt","w") as f:
        for one_range in unicode_ranges:
            for one_letter in one_range:
                letter = chr(one_letter)
                f.write(f"{letter}\n")

        for letter_one in range(0x0032,0x00ff):
            for letter_two in range(0x0032, 0x00ff):
                digraph = chr(letter_one) + chr(letter_two)
                f.write(f"{digraph}\n")
