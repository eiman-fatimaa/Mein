import os

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

# Signup/login go through the anon-keyed client, matching how a real
# client app would authenticate -- the service-role client in
# db_services.py is for server-side reads/writes, not credential checks.
supabase_anon: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def sign_up(email: str, password: str):
    return supabase_anon.auth.sign_up({"email": email, "password": password})


def sign_in(email: str, password: str):
    return supabase_anon.auth.sign_in_with_password({"email": email, "password": password})
