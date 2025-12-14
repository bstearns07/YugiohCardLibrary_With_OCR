######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines functions for beginning extraction of a card image's information and keeping only
#                         high confidence words
#######################################################################################################################

import pytesseract

#######################################################################################################################
# Function that performs ocr on an image and return the text extracted as a dictionary
# Parameters: the image to be scanned and optional configurations if desired
# Returns: the image's text information as a dictionary for more structured analysis (like skipping unsure words)
#######################################################################################################################
def ocr_data(img, config=""):
    """Return tesseract data as a dictionary to inspect word confidences."""
    # Use the default engine mode for tesseract since it's more accurate
    # append any optional configurations
    cfg = ("--oem 3 " + config).strip()

    # perform ocr to get each word detected, output as a dictionary instead of plain text, pass in configurations
    return pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=cfg)

#######################################################################################################################
# Function that takes data returned by ocr and only keeps words that pass a certain confidence level
# Parameters: the ocr data and the minimum confidence level for a word
# Returns: only a list of words that pass the confidence test
#######################################################################################################################
def ocr_text_from_data(data, min_conf=60):
    """Assembles the words detected by ocr while only keeping words with high confidence level"""
    words = [] # for storing words that pass confidence test

    # iterate through each word detected by tesseract and sanitize it for analysis
    for index, word in enumerate(data.get('text', [])):
        txt = word.strip()

        # if the resulting word is empty, continue to the next word
        if not txt:
            continue

        # attempt to extract the confidence level for the word by its corresponding index
        # sometimes tesseract returns level as a string, so wrap in try/except just in case and return -1 if fails
        # convert to decimal first in case a decimal is returned so a raise a ValueError exception doesn't raise
        try:
            conf = int(float(data['conf'][index]))
        except:
            conf = -1

        # only keep the word if it's above the minimum confidence level
        if conf >= min_conf:
            words.append(txt)

    # join the list together with a space separator
    return " ".join(words).strip()
