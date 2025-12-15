################################################################################
# Supabase Database Reset + Seed Script
# Mirrors old SQLite behavior but works for Supabase REST/Postgres
################################################################################

from supabase_client import supabase   # your connection file
from Yugioh_Card import YugiohCard
import time

print("Rebuilding Supabase 'cards' table...\n")

# ------------------------------------------------------------------------------
# 1. DROP TABLE IF EXISTS
# ------------------------------------------------------------------------------

supabase.rpc("exec_sql", {"sql": "DROP TABLE IF EXISTS cards CASCADE;"}).execute()
print("Dropped existing table (if existed).")

# ------------------------------------------------------------------------------
# 2. RECREATE TABLE
# ------------------------------------------------------------------------------

create_table_sql = """
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) UNIQUE NOT NULL,
    card_type VARCHAR(32) NOT NULL,
    monster_type VARCHAR(32),
    description VARCHAR(500) NOT NULL,
    attack INTEGER,
    defense INTEGER,
    attribute VARCHAR(32),
    image_filename VARCHAR(500)
);
"""

supabase.rpc("exec_sql", {"sql": create_table_sql}).execute()
print("Created new table 'cards'.")
print("Created new table 'cards'. Waiting for Supabase to refresh schema...")

time.sleep(3)   # small pause

# ------------------------------------------------------------------------------
# 3. SEED DATA
# ------------------------------------------------------------------------------

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
    attack=None,
    defense=None,
    attribute="-",
    image_filename="raigeki.png"
)

mirror_force = YugiohCard(
    name="Mirror Force",
    card_type="Trap",
    monster_type="-",
    description="When an opponent's monster declares an attack: Destroy all your opponent's Attack Position monsters.",
    attack=None,
    defense=None,
    attribute="-",
    image_filename="mirror_force.png"
)

sample_cards = [blue_eyes, dark_magician, raigeki, mirror_force]

# Insert each card into Supabase
for card in sample_cards:
    supabase.table("cards").insert({
        "name": card.name,
        "card_type": card.card_type,
        "monster_type": card.monster_type,
        "description": card.description,
        "attack": card.attack,
        "defense": card.defense,
        "attribute": card.attribute,
        "image_filename": card.image_filename
    }).execute()

print("\nSeed data inserted.")

# ------------------------------------------------------------------------------
# 4. QUERY AND PRINT RESULTS
# ------------------------------------------------------------------------------

result = supabase.table("cards").select("*").execute()
print("\nCards in Supabase table:")
for row in result.data:
    print(row)
