######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines functions to clean/extract a card image's monster_type through best-match scenario
#######################################################################################################################

import re
from utils.constants import COMMON_FIXES, KNOWN_TYPES

#######################################################################################################################
# Function used to analyze the extracted text for a card's monster_type for it's best match in KNOWN_TYPES
# Parameters: raw monster_type text extracted by ORC
# Returns: the best match for monster_type and the extracted text
#######################################################################################################################
def match_monster_type(type_raw):
    # return a cleaned up version. If nothing is return by this process, return an empty string
    cleaned = clean_raw_type(type_raw)
    if not cleaned:
        return ""

    # convert cleaned text into a set of characters for inspection
    cleaned_set = set(cleaned)

    # if the cleaned text are common misreads for "Dragon", return "DRAGON"
    if cleaned in ("TD", "FD", "RD", "ID", "DD", "D"):
        return "DRAGON"

    # initialize variables for storing the best monster_type match as a string and the best similarity score
    best = None
    best_score = -999

    #
    for t in KNOWN_TYPES:
        # remove any dashes or empty spaces from KNOWN_TYPE and convert result to a set of characters
        t_clean = t.replace("-", "").replace(" ", "")
        t_set = set(t_clean)

        # Calculate the similarity score by dividing the number of characters shared by the known type's length
        score = len(cleaned_set & t_set) / len(t_clean)

        # if the current iteration's score is higher, it's a better match.
        # Replace that with best_score, as assign the corresponding known type to be returned
        if score > best_score:
            best_score = score
            best = t

    # if match is extremely weak, return raw OCR
    if best_score < 0.2:
        return cleaned

    return best

#######################################################################################################################
# Function that cleans the raw string data extracted from a card's monster_type data into a usable form
# Parameters: the text extracted regarding the card's monster_type information
# Returns: extracted text that's been sanitized, and formatted
#######################################################################################################################
def clean_raw_type(text):
    """Normalize raw OCR output before matching."""
    # if the string came up empty, return an empty string
    if not text:
        return ""
    # strip whitespace and cast to uppercase
    text_cleaned = text.upper().strip()
    # Loop through every character in the string and replace with a corrected character if it's considered a common fix
    # otherwise return the character unchanged. Join all the characters back into a new string
    text_cleaned = "".join(COMMON_FIXES.get(c, c) for c in text_cleaned)
    # Remove anything not A–Z, space, bracket, or dash
    text_cleaned = re.sub(r"[^A-Z\[\]\- ]", "", text_cleaned)
    # Remove brackets for to make matching the text to an entry in KNOWN_TYPES easier
    text_cleaned = text_cleaned.replace("[", "").replace("]", "").strip()
    return text_cleaned