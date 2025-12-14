######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines a function that prepares a cropped image of a card's name for OCR
#######################################################################################################################

#######################################################################################################################
# Function that prepares an image of a card's name for OCR
# Parameters: the original cropped image
# Returns: the preprocessed version of the image
#######################################################################################################################
from PIL import ImageOps, ImageFilter, Image

def preprocess_name(img):
    """Used to prepare a cropped card name image for ocr"""
    gray = img.convert("L") # convert image to grayscale
    gray = ImageOps.autocontrast(gray) # increase the contrast for better recondition
    # remove noise by replacing each pixel with the median of its neighbor
    gray = gray.filter(ImageFilter.MedianFilter(3))
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1, percent=150)) # sharpen the edges of card text etc.
    return gray.resize((gray.width * 3, gray.height * 3), Image.LANCZOS) # enlarge image with LANCZOS filter

