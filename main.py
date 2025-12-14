#####################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: This file defines the route functionality and main entrypoint for launching the application
#####################################################################################################################

# imports
import os                                                                               # for file operations
import sqlite3                                                                          # for sql error handling
from werkzeug.utils import secure_filename                                              # to sanitizing filenames
from flask import Flask, session, render_template, request, redirect, flash, url_for    # for webapp functionality
import webbrowser                                                                       # for launching the app
import DBcm                                                                             # for database functionality
from utils.constants import KNOWN_ATTRIBUTES                        # for populating SELECT element
from utils.install_tesseract import ensure_tesseract                # to ensure tesseract installed
from tesseract import process_yugioh_card                                               # for ocr image processing

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
    db_details = "data_layer/Cards.sqlite3"

    # If session has no cache or the card with the highest id isn't the same as the last fetch, refresh cache
    if "cards" not in session:
        with DBcm.UseDatabase(db_details) as db:
            sql = """
                SELECT id, name, card_type, monster_type, description, attack, defense, attribute, image_filename
                FROM cards
                ORDER BY name
            """
            db.execute(sql)
            results = db.fetchall()

        # Convert tuples to list of dictionaries for easier Jinja display
        cards = []
        for row in results:
            cards.append({
                "id": row[0],
                "name": row[1],
                "card_type": row[2],
                "monster_type": row[3],
                "description": row[4],
                "attack": row[5],
                "defense": row[6],
                "attribute": row[7],
                "image_filename": row[8],
            })

        # Save new cache + new database state
        session["cards"] = cards

    return session["cards"]

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
    db_details = "data_layer/Cards.sqlite3"

    # query the database to select the chosen card's id number
    with DBcm.UseDatabase(db_details) as db:
        query = "SELECT id, name, card_type, monster_type, description, attack, defense, attribute, image_filename FROM cards WHERE id = ?"
        db.execute(query, (card_id,))
        row = db.fetchone()

    # if the card isn't found, return an error
    if not row:
        return "Card not found", 404

    # Convert tuple to dictionary
    card = {
        "id": row[0],
        "name": row[1],
        "card_type": row[2],
        "monster_type": row[3],
        "description": row[4],
        "attack": row[5],
        "defense": row[6],
        "attribute": row[7],
        "image_filename": row[8] if len(row) > 8 else None
    }

    return render_template("view_card.html", title="View Card", card=card)

#######################################################################################################################
# Function   : handles get and post requests to update a card's information in the database
# Parameters : the card's database id
# Returns    : add_edit.html
#######################################################################################################################
@app.route("/edit/<int:card_id>", methods=["GET", "POST"])
def edit_card(card_id):
    db_details = "data_layer/Cards.sqlite3"

    # GET load the form with card data
    if request.method == "GET":
        cards = retrieve_library()
        # looks through every card retrieved and returns the matching id
        # stop the loop once found using the next() function
        card = next((c for c in cards if c["id"] == card_id), None)

        # if card isn't found, return a 404 error
        if card is None:
            return "Card not found", 404

        # otherwise, return add_edit.html with the retrieved card
        return render_template(
            "add_edit.html",
            title="Edit Card",
            KNOWN_ATTRIBUTES=KNOWN_ATTRIBUTES,
            card=card
        )

    # POST and save the updated card
    form = request.form
    with DBcm.UseDatabase(db_details) as db:
        sql = """
            UPDATE cards
            SET name=?, card_type=?, monster_type=?, description=?, attack=?, defense=?, attribute=?
            WHERE id=?
        """
        db.execute(sql, (
            form["name"],
            form["card_type"],
            form["monster_type"],
            form["description"],
            form["attack"],
            form["defense"],
            form["attribute"],
            card_id
        ))

    # Clear the cached library so it refreshes
    session.pop("cards", None)

    flash("Card successfully updated!", "success")

    return redirect(url_for("library"))

#######################################################################################################################
# Function   : handles get and post requests for adding a new card to the database
# Returns    : add_edit.html
#######################################################################################################################
@app.route("/add", methods=["GET", "POST"])
def add_card():
    db_details = "data_layer/Cards.sqlite3"

    # if a post is made, parse the form's data into variables
    if request.method == "POST":
        name = request.form["name"]
        card_type = request.form["card_type"]
        description = request.form["description"]
        monster_type = request.form.get("monster_type")
        attack = request.form.get("attack")
        defense = request.form.get("defense")
        attribute = request.form.get("attribute")

        card = {
            "name": name,
            "card_type": card_type,
            "description": description,
            "monster_type": monster_type,
            "attack": attack,
            "defense": defense,
            "attribute": attribute
        }

        # Retrieve the card image uploaded by the user if they supplied one
        file = request.files.get("card_image")

        if file and not allowed_file(file.filename):
            # Save the uploaded file
            flash("Unsupported file type. Please use one of the following extensions: png, jpg, jpeg, gif", "danger")
            return render_template(
                "add_edit.html",
                title="Add Card",
                KNOWN_ATTRIBUTES=KNOWN_ATTRIBUTES,
                card=card
            )

        # if the file exists and is an allowed extension, sanitize the filename and save to the upload folder
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = None

        # Save all data to the database
        with DBcm.UseDatabase(db_details) as db:
            # placeholder query
            sql = """
            INSERT INTO cards (name, card_type, monster_type, description, attack, defense, attribute, image_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            db.execute(sql, (
                name,
                card_type,
                monster_type,
                description,
                attack,
                defense,
                attribute,
                filename
            ))

        #Clear session cache so the app is forced to refresh it next time. Prevent errors in no cache by that key exists
        session.pop("cards", None)

        # send a confirmation flash message back the return page and redirect back to home page
        flash("Card successfully added!", "success")
        return redirect(url_for("index"))

    # otherwise, handle a simple get request that returns a blank add/edit page
    return render_template(
        "add_edit.html",
        title="Add Card",
        KNOWN_ATTRIBUTES=KNOWN_ATTRIBUTES,
        card=None  # no card = adding mode
    )

#######################################################################################################################
# Function   : handles get requests to delete a card from the database
# Parameters : the card's database id
# Returns    : view_card.html
#######################################################################################################################
@app.get("/delete/<int:card_id>")
def confirm_delete(card_id):
    db_details = "data_layer/Cards.sqlite3"

    # retrieve the card to be deleted from the database to display to the user for confirmation
    with DBcm.UseDatabase(db_details) as db:
        sql = "SELECT id, name, image_filename FROM cards WHERE id = ?"
        db.execute(sql, (card_id,))
        card = db.fetchone()

    # if the card doesn't exist in the database, just redirect back to the library page to prevent crashes
    if not card:
        return redirect("/library")

    # parse only required data from the card to return back to confirm.html as a dictionary
    card_obj = {
        "id": card[0],
        "name": card[1],
        "image_filename": card[2]
    }

    return render_template("confirm_delete.html",title="Confirm Delete", card=card_obj)

#######################################################################################################################
# Function   : handles get requests to delete a card from the database
# Parameters : the card's database id
# Returns    : view_card.html
#######################################################################################################################
@app.post("/delete/<int:card_id>")
def delete_card(card_id):
    db_details = "data_layer/Cards.sqlite3"

    # perform the database operation for selecting the chosen card from the database and actually deleting it
    with DBcm.UseDatabase(db_details) as db:
        sql = "SELECT image_filename FROM cards WHERE id = ?"
        db.execute(sql, (card_id,))
        row = db.fetchone()

        sql = "DELETE FROM cards WHERE id = ?"
        db.execute(sql, (card_id,))

    # Clear cached session list
    session.pop("cards", None)

    # Delete image file if present
    if row and row[0]:
        filepath = os.path.join("static", "images", "cards", row[0])
        if os.path.exists(filepath):
            os.remove(filepath)

    flash("Card successfully deleted", "danger")
    return redirect(url_for("library"))

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

    # If user uploaded a new image, save it. Otherwise, keep the original filename
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    else:
        filename = existing_filename

    # define a dictionary from all data obtained for the card
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

    # Save data to database
    db_details = "data_layer/Cards.sqlite3"
    with DBcm.UseDatabase(db_details) as db:
        sql = """
            INSERT INTO cards (name, card_type, monster_type, description, attack, defense, attribute, image_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            db.execute(sql, (
                name,
                card_type,
                monster_type,
                description,
                attack,
                defense,
                attribute,
                filename
            ))
        # handle any unique constraint errors
        except sqlite3.IntegrityError as e:
            flash("A card with that name already exists.", "danger")
            # attempt to retrieve the filepath to the host machine's installed tesseract program
            tesseract_path = ensure_tesseract()

            # if tesseract is found, pass True to the page rendered. Otherwise, pass False to the page
            if tesseract_path:
                tesseract_exists = True
            else:
                tesseract_exists = False
            return render_template(
                "confirm_scan.html",
                title="Scan Card",
                tesseract_exists=tesseract_exists,
                card=card)
        except Exception as e:
            # This catches all OTHER errors
            flash(f"An unexpected database error occurred: {e}", "danger")
            return render_template("confirm_scan.html", card=card)

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