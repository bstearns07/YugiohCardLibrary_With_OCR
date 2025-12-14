######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines functions for extracting a card's attribute through best-match scenario
#######################################################################################################################

import os
import numpy as np
from PIL import Image
from preprocessing.preprocess_attribute import preprocess_attr_for_match


#######################################################################################################################
# Function that attempts to match a scanned card's attribute with base images in the "attributes" folder
# Parameters: the cropped attribute image and directory containing template images to compare
# Returns: the best match found
#######################################################################################################################
def classify_attribute(cropped_attr_img, template_dir="attributes"):
    """Classify attribute icon using normalized correlation instead of histogram distance."""
    # Preprocess the cropped icon exactly like the templates for better matching
    img = preprocess_attr_for_match(cropped_attr_img)

    # convert the image to a numpy array for mathematical operations can be applied to it, ensuring consistent fp format
    img_arr = np.array(img, dtype=np.float32)

    # standardize the image. New value = (pixel - mean_of_image) / standard_deviation
    # removes differences in lighting, brightness, and contrast to make the image more comparable
    img_arr = (img_arr - img_arr.mean()) / (img_arr.std() + 1e-6)

    # define variables to store the best matching label and matching score found
    best_match = None
    best_score = -1.0

    for filename in os.listdir(template_dir):
        # safety code in case an unknown file extension is inside the directory of samples
        if not filename.lower().endswith(".png"):
            continue

        label = filename.split(".")[0].upper() # get the attribute label from filename

        # open sample image, preprocess, convert to numpy array, and standardize
        template = Image.open(os.path.join(template_dir, filename))
        template = preprocess_attr_for_match(template)
        template_arr = np.array(template, dtype=np.float32)
        template_arr = (template_arr - template_arr.mean()) / (template_arr.std() + 1e-6)

        # calculate similarity score by multiplying the image arrays pixel by pixel and calculating the average
        # since arrays are same size after processing, this creates a similarity map of the pixels
        score = np.mean(img_arr * template_arr)

        # if the similarity score is higher than the last iteration, replace the high score and winning label
        if score > best_score:
            best_score = score
            best_match = label

    return best_match