######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines a function that prepares a cropped image of a card's monster_type for OCR
#######################################################################################################################

#######################################################################################################################
# Function used to prepare and image of a card's card_type for OCR
# Parameters: the original cropped image
# Returns: a processed version of the image supplied
#######################################################################################################################
from PIL import ImageOps, ImageFilter, ImageEnhance, Image

def preprocess_type(img):
    """Used to prepare a cropped card_type image for ocr"""
    gray = img.convert("L") # convert to grayscale
    gray = ImageOps.autocontrast(gray) # perform auto-contrast enhancement
    gray = gray.resize((gray.width * 6, gray.height * 6), Image.LANCZOS) # enlarge
    gray = gray.filter(ImageFilter.MedianFilter(3)) # remove noise
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1, percent=250)) # sharpen edges of text etc.
    gray = ImageEnhance.Contrast(gray).enhance(1.5) # increase contrast some more
    return gray