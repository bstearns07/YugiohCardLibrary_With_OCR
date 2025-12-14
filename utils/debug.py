######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines a function that prints and optionally shows all regions cropped from a card
#######################################################################################################################

import re

#######################################################################################################################
# Function saves each image produced by cropping the original card image by saving the images for viewing/debugging
# Parameters: the regions used for cropping
# Returns: void
#######################################################################################################################
def debug_show_crops(regions):
    # loop through every key in the regions dictionary and the img associated with that region
    for key, img in regions.items():
        # make a safe filename by replacing anything not a letter, number, underscore or hyphen with an underscore
        safe_key = re.sub(r'[^a-zA-Z0-9_-]', '_', key)
        img.save(f"processed_pics/{safe_key}.png") # save the image for viewing what the cropped image looks like
        # img.show(title=key) # only uncomment if you wish to display all cropped images
