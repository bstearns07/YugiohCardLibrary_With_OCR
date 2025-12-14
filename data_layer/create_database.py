#####################################################################################################################
# Project...............: Yugioh Card Library
# Author................: Ben Stearns
# Date..................: 12-4-25
# Project Description...: This application creates a digital database library for storing and managing Yugioh cards
# File Description......: Running this file recreates the database with seed data if needed
#####################################################################################################################

import os
from Yugioh_Card import YugiohCard
import DBcm

BASE_DIR = os.path.dirname(__file__)  # folder where create_database.py lives
db_details = os.path.join(BASE_DIR, "Cards.sqlite3")

# --- NEW: Delete existing database first ---
if os.path.exists(db_details):
    os.remove(db_details)
    print("Old Cards.sqlite3 deleted. Rebuilding database...\n")

insert_SQL = """
    INSERT INTO cards (name, card_type, monster_type, description, attack, defense, attribute, image_filename)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

with DBcm.UseDatabase(db_details) as db:
    SQL = """create table if not exists cards (
            id integer not null primary key autoincrement,
            name varchar(32) not null unique,
            card_type varchar(32) not null,
            monster_type varchar(32),  
            description varchar(500) not null,  
            attack integer,
            defense integer,
            attribute varchar(32),
            image_filename varchar(500)
        )"""
    db.execute(SQL)

    blue_eyes = YugiohCard(
        name="Blue-Eyes White Dragon",
        card_type="Monster",
        monster_type="Dragon",
        description="This legendary dragon is a powerful engine of destruction.",
        attack=3000,
        defense=2500,
        attribute="Light",
        image_filename="blue_eyes.png"
    )

    dark_magician = YugiohCard(
        name="Dark Magician",
        card_type="Monster",
        monster_type="Spellcaster",
        description="The ultimate wizard in terms of attack and defense.",
        attack=2500,
        defense=2000,
        attribute="Dark",
        image_filename="dark_magician.png"
    )

    raigeki = YugiohCard(
        name="Raigeki",
        card_type="Spell",
        monster_type="-",
        description="Destroy all Monsters your opponent controls.",
        attack="-",
        defense="-",
        attribute="-",
        image_filename="raigeki.png"
    )

    mirror_force = YugiohCard(
        name="Mirror Force",
        card_type="Trap",
        monster_type="-",
        description="When an opponent's monster declares an attack: Destroy all your opponent's Attack Position monsters.",
        attack="-",
        defense="-",
        attribute="-",
        image_filename="mirror_force.png"
    )

    # Insert sample cards
    for card in (blue_eyes, dark_magician, raigeki, mirror_force):
        db.execute(insert_SQL, (
            card.name,
            card.card_type,
            card.monster_type,
            card.description,
            card.attack,
            card.defense,
            card.attribute,
            card.image_filename
        ))

    # Show results
    print("Database successfully created\n")
    db.execute("SELECT * FROM cards")
    print(f"Cards in table: {db.fetchall()}")
