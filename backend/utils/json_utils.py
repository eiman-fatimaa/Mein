import json
import re


def clean_json_response(text: str) -> dict:
    """Parse a JSON object out of a Gemini text response.

    Gemini sometimes wraps JSON in ```json ... ``` fences or adds stray
    whitespace even when response_mime_type="application/json" is set
    (e.g. on retries or older SDK paths), so this strips fences before
    parsing rather than assuming the text is already clean.
    """
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned.strip())
