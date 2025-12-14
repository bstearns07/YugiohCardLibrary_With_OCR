######################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: defines functions that processes a Yugioh card into data that can be saved to the database
#######################################################################################################################

# imports from python library
from PIL import Image, ImageOps, ImageFilter, ImageEnhance  # for image manipulation
import pytesseract                              # for ocular recognition functionality
import re                                       # for pattern matching text extracted from cards
import os

# imports from various other modules of the program
from extractors.atkdef_extractor import fix_atkdef_labels, extract_atk_def_numbers
from extractors.attribute_classifier import classify_attribute
from extractors.name_extractor import correct_chars_for_name
from extractors.ocr_helpers import ocr_data, ocr_text_from_data
from extractors.type_extractor import match_monster_type
from preprocessing.cropping import crop_regions
from preprocessing.preprocess_atkdef import preprocess_atkdef
from preprocessing.preprocess_attribute import preprocess_attribute
from preprocessing.preprocess_description import preprocess_desc
from preprocessing.preprocess_name import preprocess_name
from preprocessing.preprocess_type import preprocess_type
from utils.debug import debug_show_crops


#######################################################################################################################
# Function used to process an entire card image and extract its individual data
# Parameters: the filepath to the image to analyze
# Returns: a dictionary representing the card's information
#######################################################################################################################
def process_yugioh_card(image_path):
    # open the image, crop into each region of the card that has the data we need, and save each crop for debugging
    original = Image.open(image_path)
    regions = crop_regions(original)
    debug_show_crops(regions)

    # ---------- Preprocess each cropped region ----------
    name_img = preprocess_name(regions["name"])
    attribute_img = preprocess_attribute(regions["attribute"])
    type_img = preprocess_type(regions["type"])
    desc_img = preprocess_desc(regions["description"])
    atkdef_img = preprocess_atkdef(regions["atkdef"])

    # ---------- Extract name data ----------
    name_data = ocr_data(name_img, config="--psm 7") # perform ocr. --psm7 treats are a single line of text
    raw_name = ocr_text_from_data(name_data, min_conf=50) # parse ocr data into raw text
    name_clean = correct_chars_for_name(raw_name) # clean up the raw text

    # ---------- Attribute ----------
    attribute = classify_attribute(attribute_img) # match the attribute image to its best match in "attribute" folder

    # ---------- Monster Type ----------
    # perform ocr and only recognize the supplied list of characters
    type_data = ocr_data(type_img, config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ[]")
    type_raw = ocr_text_from_data(type_data, min_conf=45) # keep only words with a certain confidence level
    type_clean = match_monster_type(type_raw) # find the raw text's best match in KNOWN_TYPES

    # ---------- DESCRIPTION ----------
    desc_data = ocr_data(desc_img, config="--psm 6") # perform ocr as a block of text using page segmentation mode 6
    description_raw = ocr_text_from_data(desc_data, min_conf=45) # keeps only data that meets confidence requirements
    description = re.sub(r'\b[A-Z]{1,2}\b', '', description_raw) # only keep non-isolated A-Z.
    description = re.sub(r'[\|\=\>\<\&]', '', description) # remove symbols
    description = re.sub(r'\s{2,}', ' ', description).strip() # normalize spacing

    # ---------- ATK/DEF ----------
    atkdef_raw = pytesseract.image_to_string(atkdef_img, config="--psm 7").strip() # extract raw ATK/DEF data
    atkdef_fixed_labels = fix_atkdef_labels(atkdef_raw)
    atk, defn = extract_atk_def_numbers(atkdef_fixed_labels)

    # ----------IMAGE FILEPATH -----
    filename = os.path.basename(image_path) # only keep non-nested base name

    # ---------- CARD TYPE ----------
    # if the card has an attack value, it's type is a monster. otherwise match its type with its attribute
    if atk is not None:
        card_type = "Monster"
    elif attribute == "SPELL":
        card_type = "Spell"
    elif attribute == "TRAP":
        card_type = "Trap"
    else:
        card_type = "Unknown"

    # return final result as a dictionary
    return {
        "name": name_clean,
        "attribute": attribute,
        "monster_type": type_clean,
        "description": description,
        "attack": atk,
        "defense": defn,
        "card_type": card_type,
        "image_filename": filename
    }
