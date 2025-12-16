#####################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: This file defines the route functionality and main entrypoint for launching the application
#####################################################################################################################

# imports
import os                                                                               # for file operations
from werkzeug.utils import secure_filename                                              # to sanitizing filenames
from flask import Flask, session, render_template, request, redirect, flash, url_for    # for webapp functionality
import webbrowser                                                                       # for launching the app

from data_layer.supabase_client import supabase
from utils.constants import KNOWN_ATTRIBUTES                                            # for populating SELECT element
from utils.convert_int_to_none import to_int_or_none
from utils.install_tesseract import ensure_tesseract                                    # to ensure tesseract installed
from tesseract import process_yugioh_card                                               # for ocr image processing
from supabase import create_client, Client                                              # for db connections/queries
from supabase.client import Client                                                      # import supabase_client Client
from utils import convert_int_to_none

# main program variables
app = Flask(__name__)                               # defines main app object associated with code's current namespace
app.secret_key = "supercalifragilistic"             # defines a key for encrypting session data. Required for Flask
UPLOAD_FOLDER = "static/images/cards"               # defines the fil path to the folder for storing uploaded images
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}  # defines what images extensions are allowed to be uploaded
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER         # stores the upload folder path as a Flask configuration for use

#######################################################################################################################
# Function: checks whether an uploaded filename has an allowed file extension
# Returns.: true if the image has an allowed extension. Otherwise returns false
#######################################################################################################################
def allowed_file(filename):
    # check if filename has a . and if splitting the filename by . only once and casting to lower is in ALLOW_EXTENSIONS
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

#######################################################################################################################
# Function: retrieves all cards in the database and storing in session
# Returns.: session data for all cards in the database
#######################################################################################################################
def retrieve_library():
    # If cards are already cached in session, return that session data instead of querying the database
    if "cards" in session:
        return session["cards"]

    # otherwise, query supabase, store results in session, then return results
    response = supabase.table("cards").select("*").order("name").execute()
    cards = response.data
    session["cards"] = cards
    return cards

#######################################################################################################################
# Function: route that handles get requests for the home page
# Returns.: index.html
#######################################################################################################################
@app.get("/")
def index():
    # renders the index.html template with required data
    return render_template(
        "index.html",
        title="Yugioh Card Library") # the title used in the head element for the page

#######################################################################################################################
# Function: handles get requests to view all cards in the database
# Returns.: library.html
#######################################################################################################################
@app.get("/library")
def library():
    cards = retrieve_library()
    return render_template(
        "library.html",
        title="Your Library",
        cards=cards # the session data for all cards in the database
    )

#######################################################################################################################
# Function   : handles get requests to view a single card's full information
# Parameters : the card's database id
# Returns    : view_card.html
#######################################################################################################################
@app.get("/view/<int:card_id>")
def view_card(card_id):
    # query the db for the card's url id, return error if not found, otherwise render view with the query results
    response = supabase.table("cards").select("*").eq("id", card_id).single().execute()
    if not response.data:
        return "Card not found", 404
    return render_template(
        "view_card.html",
        title="View Card",
        card=response.data
    )

#######################################################################################################################
# Function   : handles get and post requests to update a card's information in the database
# Parameters : the card's database id
# Returns    : add_edit.html
#######################################################################################################################
@app.route("/edit/<int:card_id>", methods=["GET", "POST"])
def edit_card(card_id):

    if request.method == "GET":
        cards = retrieve_library()
        card = next((c for c in cards if c["id"] == card_id), None)

        if card is None:
            return "Card not found", 404

        # Normalize None → empty string for form display
        card["attack"] = "" if card["attack"] is None else card["attack"]
        card["defense"] = "" if card["defense"] is None else card["defense"]

        return render_template(
            "add_edit.html",
            title="Edit Card",
            KNOWN_ATTRIBUTES=KNOWN_ATTRIBUTES,
            card=card
        )

    # POST request
    # POST request
    form = request.form

    card = {
        "name": form["name"],
        "card_type": form["card_type"],
        "monster_type": form.get("monster_type"),
        "description": form["description"],
        "attack": to_int_or_none(form.get("attack")),
        "defense": to_int_or_none(form.get("defense")),
        "attribute": form.get("attribute"),
    }

    # Fetch existing image filename
    existing = supabase.table("cards") \
        .select("image_filename") \
        .eq("id", card_id) \
        .single() \
        .execute()

    old_filename = existing.data.get("image_filename")
    new_filename = old_filename

    file = request.files.get("card_image")

    if file and file.filename:
        if not allowed_file(file.filename):
            flash("Unsupported file type.", "danger")
            card["image_filename"] = old_filename
            return render_template(
                "add_edit.html",
                title="Edit Card",
                KNOWN_ATTRIBUTES=KNOWN_ATTRIBUTES,
                card=card
            )

        new_filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], new_filename))

        # Remove old image safely
        if old_filename:
            old_path = os.path.join(app.config["UPLOAD_FOLDER"], old_filename)
            if os.path.exists(old_path):
                os.remove(old_path)

    card["image_filename"] = new_filename

    try:
        supabase.table("cards").update(card).eq("id", card_id).execute()

    except Exception as e:
        message = str(e).lower()

        if "duplicate key" in message or "unique" in message:
            flash("A card with that name already exists.", "danger")
        else:
            flash(f"An unexpected database error occurred: {e}", "danger")

        card["id"] = card_id
        card["attack"] = "" if card["attack"] is None else card["attack"]
        card["defense"] = "" if card["defense"] is None else card["defense"]

        return render_template(
            "add_edit.html",
            title="Edit Card",
            KNOWN_ATTRIBUTES=KNOWN_ATTRIBUTES,
            card=card
        )

    session.pop("cards", None)
    flash("Card successfully updated!", "success")
    return redirect(url_for("library"))


#######################################################################################################################
# Function   : handles get and post requests for adding a new card to the database
# Returns    : add_edit.html
#######################################################################################################################
@app.route("/add", methods=["GET", "POST"])
def add_card():
    # for POST requests, parse form data into a card dictionary
    if request.method == "POST":
        name = request.form["name"]
        card_type = request.form["card_type"]
        description = request.form["description"]
        monster_type = request.form.get("monster_type")
        attack = request.form.get("attack")
        defense = request.form.get("defense")
        attribute = request.form.get("attribute")

        # convert any empty strings for integers to None as required by PostgreSQL
        if card_type is not "Monster":
            attack = to_int_or_none(request.form.get("attack"))
            defense = to_int_or_none(request.form.get("defense"))

        card = {
            "name": name,
            "card_type": card_type,
            "description": description,
            "monster_type": monster_type,
            "attack": attack,
            "defense": defense,
            "attribute": attribute,
        }

        # get the image file uploaded by user if they supplied one. only accepts valid file extensions
        file = request.files.get("card_image")
        if file and not allowed_file(file.filename):
            flash("Unsupported file type.", "danger")
            return render_template("add_edit.html", title="Add Card", KNOWN_ATTRIBUTES=KNOWN_ATTRIBUTES, card=card)

        # if file is a valid extension, sanitize the filename and save it. otherwise return nothing
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = None
        card["image_filename"] = filename

        # SUPABASE INSERT
        try:
            # Insert into Supabase
            supabase.table("cards").insert(card).execute()

        except Exception as e:
            message = str(e).lower()

            if "duplicate key" in message or "unique" in message:
                flash("A card with that name already exists.", "danger")
            else:
                flash(f"An unexpected database error occurred: {e}", "danger")

            return render_template(
                "add_edit.html",
                title="Add Card",
                KNOWN_ATTRIBUTES=KNOWN_ATTRIBUTES,
                card=card
            )

        session.pop("cards", None)
        flash("Card successfully added!", "success")
        return redirect(url_for("index"))

    return render_template(
        "add_edit.html",
        title="Add Card",
        KNOWN_ATTRIBUTES=KNOWN_ATTRIBUTES,
        card=None
    )

#######################################################################################################################
# Function   : handles get requests to delete a card from the database
# Parameters : the card's database id
# Returns    : view_card.html
#######################################################################################################################
@app.get("/delete/<int:card_id>")
def confirm_delete(card_id):
    response = supabase.table("cards").select("id, name, image_filename").eq("id", card_id).single().execute()

    if not response.data:
        return redirect("/library")

    return render_template("confirm_delete.html", title="Confirm Delete", card=response.data)

#######################################################################################################################
# Function   : handles get requests to delete a card from the database
# Parameters : the card's database id
# Returns    : view_card.html
#######################################################################################################################
@app.post("/delete/<int:card_id>")
def delete_card(card_id):

    # fetch card (for image delete)
    existing = supabase.table("cards").select("image_filename").eq("id", card_id).single().execute()

    # delete from supabase
    supabase.table("cards").delete().eq("id", card_id).execute()

    session.pop("cards", None)

    # delete local file
    if existing.data and existing.data["image_filename"]:
        filepath = os.path.join("static", "images", "cards", existing.data["image_filename"])
        if os.path.exists(filepath):
            os.remove(filepath)

    flash("Card successfully deleted", "danger")
    return redirect(url_for("library"))

#######################################################################################################################
# Function   : handles get and post requests for scanning a card image to add to the database
# Parameters : none
# Returns    : confirm_scan.html
#######################################################################################################################
@app.route("/scan", methods=["GET", "POST"])
def scan():
    if request.method == "GET":
        # attempt to retrieve the filepath to the host machine's installed tesseract program
        tesseract_path = ensure_tesseract()

        # if tesseract is found, pass True to the page rendered. Otherwise, pass False to the page
        if tesseract_path:
            tesseract_exists = True
        else:
            tesseract_exists = False

        return render_template("scan.html", title="Scan Image", tesseract_exists=tesseract_exists)

    # POST → handle uploaded image
    file = request.files.get("card_image")

    if not file or file.filename == "":
        flash("No file selected", "danger")
        return redirect(url_for("scan"))

    if not allowed_file(file.filename):
        # Save the uploaded file
        flash("Unsupported file type. Please use one of the following extensions: png, jpg, jpeg, gif", "danger")
        return redirect(url_for("scan"))

    # Save the uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Run OCR on the uploaded image
    try:
        card_data = process_yugioh_card(filepath)
    except Exception as e:
        flash("Error processing image. Check logs.", "danger")
        print("OCR ERROR:", e)
        return redirect(url_for("scan"))

    # Include the saved image file for preview
    card_data["image_filename"] = filename

    return render_template("confirm_scan.html",title="Confirm Scan", card=card_data)

#######################################################################################################################
# Function   : handles post requests for confirming a scanned cards ocr data for saving to the db
# Parameters : none
# Returns    : index.html
#######################################################################################################################
@app.post("/confirm_scan")
def confirm_scan():
    # store form data posted by the user
    name = request.form["name"]
    card_type = request.form["card_type"]
    description = request.form["description"]
    monster_type = request.form.get("monster_type")
    attack = request.form.get("attack")
    defense = request.form.get("defense")
    attribute = request.form.get("attribute")

    # Retrieve uploaded file (if any)
    file = request.files.get("card_image")
    existing_filename = request.form.get("image_filename")

    # If user uploaded a new file, save it. Otherwise, use existing file
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    else:
        filename = existing_filename

    # define dictionary for returning to template on error
    card = {
        "name": name,
        "card_type": card_type,
        "description": description,
        "monster_type": monster_type,
        "attack": attack,
        "defense": defense,
        "attribute": attribute,
        "image_filename": filename
    }

    # SUPABASE INSERT
    try:
        supabase.table("cards").insert(card).execute()

    except Exception as e:
        # Supabase unique constraint violation looks like:
        #  "duplicate key value violates unique constraint "cards_name_key""
        message = str(e).lower()

        if "duplicate key" in message or "unique" in message:
            flash("A card with that name already exists.", "danger")
        else:
            flash(f"An unexpected database error occurred: {e}", "danger")

        # return user to confirmation page with their data intact
        tesseract_exists = ensure_tesseract() is not None
        return render_template(
            "confirm_scan.html",
            title="Scan Card",
            tesseract_exists=tesseract_exists,
            card=card
        )

    # Success → Clear cache and redirect
    session.pop("cards", None)
    flash("Card successfully added!", "success")
    return redirect(url_for("index"))


# if the program is run directly, open the app in a web browser and run the app
if __name__ == "__main__":
    # run Flask's built-in web server and pass the web app code to it
    # run in debugging mode: Flask watches to saved changes in code and restarts the app automatically
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true": # sets the Flash environment variable to detect only the 1st run
        webbrowser.open("http://127.0.0.1:8000") # open the app in the browser
    app.run(debug=True, port=8000)