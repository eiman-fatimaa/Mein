"""Manual prompt-testing script, not an automated test suite.

Run against real outfit photo URLs to sanity-check the analysis prompt
before wiring it into the app (see roadmap Phase 1/3: "test the prompt
with real photos until results feel accurate").

Usage:
    python tests/test_prompt.py <image_url> [<image_url> ...]
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gemini_services import analyse_outfit


async def main(image_urls: list[str]) -> None:
    for url in image_urls:
        print(f"\n=== {url} ===")
        try:
            result = await analyse_outfit(url)
        except Exception as e:
            print(f"FAILED: {e}")
            continue

        print("pieces:", result.get("pieces"))
        for vibe in result.get("vibes", []):
            print(f"  vibe: {vibe['name']} | tags: {vibe['tags']} | color: {vibe['color_hint']}")


if __name__ == "__main__":
    urls = sys.argv[1:]
    if not urls:
        print("Usage: python tests/test_prompt.py <image_url> [<image_url> ...]")
        sys.exit(1)
    asyncio.run(main(urls))
