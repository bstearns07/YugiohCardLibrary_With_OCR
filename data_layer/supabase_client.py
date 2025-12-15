# supabase_client.py

from dotenv import load_dotenv
from supabase import create_client, Client
import os

# Load .env variables into environment
load_dotenv()

# Read variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Optional: test connection
if SUPABASE_URL and SUPABASE_KEY:
    print("Supabase connection loaded successfully.")
else:
    print("Missing Supabase credentials!")
