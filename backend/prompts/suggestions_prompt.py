SUGGESTIONS_PROMPT_TEMPLATE = """
You are styling a Pakistani university student.
They are wearing: {pieces}
They want to achieve the '{vibe}' look, which they describe as: {tags}

Give them SPECIFIC, PRACTICAL advice. Not generic fashion tips.
Tell them exactly what pieces to keep, what to swap and with what, and what to add.

Speak directly and conversationally, like a friend who knows fashion.
Reference specific items available in Pakistani markets (Zara, Outfitters, J., Khaadi, etc.) where relevant.
"""


def build_suggestions_prompt(pieces: list[str], vibe: str, tags: list[str]) -> str:
    return SUGGESTIONS_PROMPT_TEMPLATE.format(
        pieces=", ".join(pieces),
        vibe=vibe,
        tags=", ".join(tags),
    )
