import os
import time

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def create_upload_path(user_id: str, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    return f"outfits/{user_id}/{int(time.time())}.{ext}"


def public_url_for(path: str) -> str:
    return f"{SUPABASE_URL}/storage/v1/object/public/{path}"


def save_outfit(user_id: str, image_url: str) -> str:
    result = supabase.table("outfits").insert({
        "user_id": user_id,
        "image_url": image_url,
    }).execute()
    return result.data[0]["id"]


def save_analysis(outfit_id: str, pieces: list, vibes: list) -> str:
    result = supabase.table("analyses").insert({
        "outfit_id": outfit_id,
        "pieces_json": pieces,
        "vibes_json": vibes,
    }).execute()
    return result.data[0]["id"]


def get_analysis(analysis_id: str) -> dict:
    result = supabase.table("analyses").select("*").eq("id", analysis_id).single().execute()
    return result.data


def get_outfit(outfit_id: str) -> dict:
    result = supabase.table("outfits").select("*").eq("id", outfit_id).single().execute()
    return result.data


def save_suggestion(analysis_id: str, selected_vibe: str, suggestions: dict) -> str:
    result = supabase.table("suggestions").insert({
        "analysis_id": analysis_id,
        "selected_vibe": selected_vibe,
        "advice_text": suggestions["advice"],
        "keep_json": suggestions["keep"],
        "swap_json": suggestions["swap"],
        "add_json": suggestions["add"],
        "tags_json": suggestions["tags"],
    }).execute()
    return result.data[0]["id"]


def get_outfit_history(user_id: str) -> list:
    result = (
        supabase.table("outfits")
        .select("*, analyses(*)")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data
