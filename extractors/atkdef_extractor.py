######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines functions for extracting ATK/DEF card data and cleaning up the results
#######################################################################################################################

# imports
import re

#######################################################################################################################
# Function that replaces text misreads by OCR with fixed version in a consistent format
# Parameters: the text that needs fixed
# Returns: the corrected version of the text
#######################################################################################################################
def fix_atkdef_labels(text):
    t = text.upper()
    # fix common misreads
    t = t.replace("ALK", "ATK")
    t = t.replace("DFF", "DEF")
    t = t.replace("DE8", "DEF")
    t = t.replace("DEF/", "DEF:")
    t = t.replace("ATK/", "ATK:")
    t = t.replace(" ", "")          # remove spaces that break regex
    t = t.replace("DEF:", " DEF:")  # ensures a separator
    return t

#######################################################################################################################
# Function that takes text extracted by OCR, uses pattern matching for parse ATK/DEF data, and returns cleaned results
# Parameters: the text extracted by OCR
# Returns: only the data regarding ATL/DEF information for the card
#######################################################################################################################
def extract_atk_def_numbers(text):
    # define pattern to use for matching
    patterns = [
        r'ATK[:]?(\d{2,5})\D+DEF[:]?(\d{2,5})',  # allow non-digits between numbers
        r'(\d{2,5})/(\d{2,5})',
        r'(\d{2,5})\s+(\d{2,5})'
    ]
    # loop through every pattern and attempt to match with the given text
    for pat in patterns:
        match = re.search(pat, text)
        # if a match is found, normalize the data and return it. Otherwise, return nothing for ATK and DEF
        if match:
            # Normalize digits inside numbers only
            DIGIT_FIX = {'O':'0', 'I':'1', 'L':'1', 'S':'5', 'B':'8'}
            atk = int("".join(DIGIT_FIX.get(ch, ch) for ch in match.group(1)))
            defe = int("".join(DIGIT_FIX.get(ch, ch) for ch in match.group(2)))
            return atk, defe
    return None, None