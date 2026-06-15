import httpx
import json
import os
import asyncio
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

load_dotenv()

ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 1. Define the exact structural schema using Pydantic
class VibeItem(BaseModel):
    name: str = Field(description="The aesthetic name of the vibe, e.g., 'Casual Desi', 'Streetwear'")
    tags: List[str] = Field(description="Exactly 3 descriptive style tags")
    color_hint: str = Field(description="A hex code matching the main color scheme of this vibe")

class OutfitAnalysisSchema(BaseModel):
    pieces: List[str] = Field(description="List of each clothing item seen with descriptive details")
    vibes: List[VibeItem] = Field(description="List of exactly 3 distinct aesthetic vibes")

ANALYSIS_PROMPT = """
You are an expert fashion stylist specializing strictly in modern Pakistani university student style.
You understand the nuances of local campus dress codes and trends across universities like NUST, FAST, LUMS, GIKI, and IBA.

Analyze the outfit in this photo with deep cultural awareness. You must recognize traditional wear, western wear, and fusion styles.
Determine exactly 3 distinct aesthetic vibes this look belongs to.
"""

async def analyse_outfit(image_url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        image_bytes = response.content
        content_type = response.headers.get("content-type", "image/jpeg")

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: ai.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=content_type),
                ANALYSIS_PROMPT
            ],
            # This configuration forces Gemini to return valid, raw JSON stripped of markdown
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=OutfitAnalysisSchema,
            ),
        )
    )

    return json.loads(result.text)