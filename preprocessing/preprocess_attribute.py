######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines functions that prepares a cropped image of a card's atk/def for OCR and matching
#######################################################################################################################

from PIL import ImageFilter, ImageEnhance, ImageOps, Image

#######################################################################################################################
# Function used to prepare a card's cropped attribute icon and a known icon for equal match comparison
# Parameters: the original cropped image of the card's attribute icon and a known one in the "attributes" folder
# Returns: a processed version of the image supplied
#######################################################################################################################
def preprocess_attr_for_match(img):
    gray = img.convert("L") # convert to grayscale
    gray = gray.resize((64 * 4, 64 * 4), Image.LANCZOS) # resize images to predefined size
    gray = gray.filter(ImageFilter.MedianFilter(3)) # remove noise by replacing each pixel with the median of neighbor
    gray = ImageEnhance.Contrast(gray).enhance(1.4) # increase contrast to make elements stand out
    gray = ImageEnhance.Brightness(gray).enhance(0.9) # increase brightness
    gray = gray.filter(ImageFilter.EDGE_ENHANCE_MORE) # sharpens the edges of elements like text
    gray = ImageOps.autocontrast(gray) # perform auto-contrast to stretch image and remove washed out values in graph
    return gray

#######################################################################################################################
# Function used to prepare a card's cropped attribute icon for OCR
# Parameters: the original cropped image of the card's attribute icon
# Returns: a processed version of the image supplied
#######################################################################################################################
def preprocess_attribute(img):
    """
    Prepares the cropped image of a card's attribute icon for OCR
    """
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS) # increase image size
    img = img.filter(ImageFilter.MedianFilter(size=3))# remove noise by replacing each pixel with the median of neighbor
    img = ImageOps.autocontrast(img, cutoff=4) # Increase all pixel's contrast except the more extreme black/whites

    return img