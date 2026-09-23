import httpx
import json
import os
import asyncio
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

from prompts.analysis_prompt import ANALYSIS_PROMPT
from prompts.suggestions_prompt import build_suggestions_prompt
from cache.analysis_cache import get_cached_analysis, set_cached_analysis
from utils.json_utils import clean_json_response

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"

ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# 1. Define the exact structural schema using Pydantic
class VibeItem(BaseModel):
    name: str = Field(description="The aesthetic name of the vibe, e.g., 'Casual Desi', 'Streetwear'")
    tags: List[str] = Field(description="Exactly 3 descriptive style tags")
    color_hint: str = Field(description="A hex code matching the main color scheme of this vibe")


class OutfitAnalysisSchema(BaseModel):
    pieces: List[str] = Field(description="List of each clothing item seen with descriptive details")
    vibes: List[VibeItem] = Field(description="List of exactly 3 distinct aesthetic vibes")


class SwapItem(BaseModel):
    item: str = Field(description="The current item to replace")
    replace_with: str = Field(description="The specific replacement item")


class SuggestionsSchema(BaseModel):
    advice: str = Field(description="One paragraph of direct, conversational styling advice")
    keep: List[str] = Field(description="Items from the outfit worth keeping")
    swap: List[SwapItem] = Field(description="Items to swap and what to replace them with")
    add: List[str] = Field(description="New pieces to complete the look")
    tags: List[str] = Field(description="5-7 descriptive tags for this look")


async def _fetch_image(image_url: str) -> tuple[bytes, str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        response.raise_for_status()
        return response.content, response.headers.get("content-type", "image/jpeg")


async def analyse_outfit(image_url: str) -> dict:
    cached = get_cached_analysis(image_url)
    if cached is not None:
        return cached

    image_bytes, content_type = await _fetch_image(image_url)

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: ai.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=content_type),
                ANALYSIS_PROMPT,
            ],
            # This configuration forces Gemini to return valid, raw JSON stripped of markdown
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=OutfitAnalysisSchema,
            ),
        ),
    )

    parsed = clean_json_response(result.text)
    set_cached_analysis(image_url, parsed)
    return parsed


async def get_suggestions(image_url: str, pieces: list[str], vibe: str, tags: list[str]) -> dict:
    image_bytes, content_type = await _fetch_image(image_url)
    prompt = build_suggestions_prompt(pieces, vibe, tags)

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: ai.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=content_type),
                prompt,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SuggestionsSchema,
            ),
        ),
    )

    return clean_json_response(result.text)