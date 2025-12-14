#######################################################################################################################
# Function that cleans up and fixes common character misreads by ocr for a card's name
# Parameters: the raw string for the card's name
# Returns: a cleaned and standard format for the name as a string
#######################################################################################################################
import re

def correct_chars_for_name(raw):
    cleaned_string = raw.upper()  # first, uppercase everything

    # define a dictionary representing common character misreads by ocr and their proper replacement characters
    char_fixes = {'0': 'O','1': 'I','5': 'S','6': 'G','8': 'B','|': 'I','¢': 'C'}

    # iterate through each character in the original string
    # if character exists in CHAR_PIXES, replace it with the dictionary value. otherwise keep it unchanged
    cleaned_string = "".join(char_fixes.get(ch, ch) for ch in cleaned_string)

    cleaned_string = re.sub(r"[^A-Z0-9\s\-]", "", cleaned_string) # allow letters, numbers, spaces, hyphens
    cleaned_string = re.sub(r"\s{2,}", " ", cleaned_string).strip() # collapse multiple spaces
    cleaned_string = " ".join(w.capitalize() for w in cleaned_string.split()) # capitalize each word
    return cleaned_string