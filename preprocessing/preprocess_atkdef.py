######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines a function that prepares a cropped image of a card's atk/def for OCR
#######################################################################################################################

#######################################################################################################################
# Function that prepares a cropped image of a card's attack and defense for tesseract
# Parameters: the original cropped image
# Returns: the preprocessed version of the image
#######################################################################################################################
from PIL import ImageOps, ImageFilter, Image

def preprocess_atkdef(img):
    gray = img.convert("L") # converts the image to greyscale using Pillow's 'L' mode
    gray = ImageOps.autocontrast(gray) # removes color information, leaving only brightness levels for OCR
    gray = gray.resize((gray.width * 3, gray.height * 3), Image.LANCZOS) # increase the size of the image

    # make edges of image cripser with a sharp mask
    # radius=1 is how far around each pixel to look
    # percent = how strong the sharpening effect is
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1, percent=150))
    return gray