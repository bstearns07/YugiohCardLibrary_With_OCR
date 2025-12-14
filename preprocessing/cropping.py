######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines a function for cropping a single card image in regions containing info to process
#######################################################################################################################

#######################################################################################################################
# Function that crops a Yugioh card image into 5 regions containing the information we need
# Parameters: the original card image
# Returns: a dictionary of the cropped image sections
#######################################################################################################################
def crop_regions(img):
    """Crops the 5 major text zones of a YuGiOh card."""
    w, h = img.size # retrieve the width and height of the image

    # define the coordinates for Pillow's crop() function (left, upper, right, lower)
    # ex for name_box: starting bit = 7% from left, next bit = 5% from top, last = 80% from right and 13% from bottom
    name_box = (int(0.07*w), int(0.05*h), int(0.80*w), int(0.13*h))
    attribute_box = (int(0.80*w), int(0.07*h), int(0.91*w), int(0.15*h))
    type_box = (int(0.08 * w),int(0.73 * h),(0.70 * w),int(0.78 * h))
    desc_box = (int(0.07*w), int(0.68*h), int(0.93*w), int(0.87*h))
    atk_def_box = (int(0.50*w), int(0.89*h), int(0.89*w), int(0.93*h))
    return {
        "name": img.crop(name_box),
        "attribute": img.crop(attribute_box),
        "type": img.crop(type_box),
        "description": img.crop(desc_box),
        "atkdef": img.crop(atk_def_box)
    }