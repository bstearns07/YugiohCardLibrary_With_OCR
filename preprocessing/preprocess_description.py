######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines a function that prepares a cropped image of a card's description for OCR
#######################################################################################################################

#######################################################################################################################
# Function used to prepare and image of a card's card_type for OCR
# Parameters: the original cropped image
# Returns: a processed version of the image supplied
#######################################################################################################################
from PIL import ImageFilter, Image

def preprocess_desc(img):
    """Used to prepare a cropped card description image for ocr"""
    gray = img.convert("L")
    gray = gray.resize((gray.width * 2, gray.height * 2), Image.LANCZOS)
    gray = gray.filter(ImageFilter.MedianFilter(3))
    return gray