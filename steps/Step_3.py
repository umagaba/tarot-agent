"""
Step 3: Interpretation of the Context  (LLM call)

This step uses outputs from both Step 1 and Step 2. It cannot run without both.
The LLM receives the spread's theme and position meanings alongside each drawn
card and its keywords, then produces a specific interpretation for
each card in its assigned position.


INPUT  (read from state):
    state["spread"]       from Step 1
    state["drawn_cards"]  from Step 2

OUTPUT (written to state): state["card_interpretations"]
    [
        {
            "position":       int,
            "label":          str,
            "focus":          str,
            "card":           str,
            "orientation":    str,
            "interpretation": str
        },
        ...
    ]
"""

import json
from grok_client import call_llm_json

SYSTEM_PROMPT = """You are an experienced tarot reader.
You will receive a client's theme, a spread layout, and a set of drawn cards.
Your task is to write a specific interpretation for each card based strictly on:
  1. The card's name and orientation (upright or reversed).
  2. The position's label and focus (what that slot addresses in the spread).
  3. The client's core theme.
  4. The card's keywords provided.

Each interpretation must be 4 to 6 sentences. It must be about the specific position. Do not mix cards or discuss them in relation to each
other yet. Address the client directly, using "you" and "your".

Respond ONLY with a valid JSON array. No explanation.
The array must contain one object per card, in position order:
[
  {
    "position": <int>,
    "label": "<position label>",
    "focus": "<position focus>",
    "card": "<card name>",
    "orientation": "<Upright or Reversed>",
    "interpretation": "<4-6 sentence interpretation>"
  },
  ...
]
"""


def _build_user_prompt(spread, drawn_cards):
    core_theme = spread["core_theme"]
    spread_name = spread["spread_name"]

    cards_block = []
    for card in drawn_cards:
        kw_str = ", ".join(card["keywords"])
        cards_block.append(
            f"Position {card['position']} | {card['label']} | Focus: {card['focus']}\n"
            f"Card: {card['name']} ({card['orientation']})\n"
            f"Keywords: {kw_str}"
        )

    cards_text = "\n\n".join(cards_block)

    return (
        f"Core theme: {core_theme}\n"
        f"Spread: {spread_name}\n\n"
        f"Drawn cards:\n\n{cards_text}"
    )


def run(state):
    """
    Reads:   state["spread"], state["drawn_cards"]
    Writes:  state["card_interpretations"]
    Returns: updated state
    """
    spread = state.get("spread")
    drawn_cards = state.get("drawn_cards")

    if not spread:
        raise RuntimeError("Step 3 requires state['spread'] from Step 1.")
    if not drawn_cards:
        raise RuntimeError("Step 3 requires state['drawn_cards'] from Step 2.")

    user_prompt = _build_user_prompt(spread, drawn_cards)
    interpretations = call_llm_json(SYSTEM_PROMPT, user_prompt, temperature=0.6)                                 

    if not isinstance(interpretations, list):
        raise ValueError(
            "Step 3 expected a JSON array from the model. "
            f"Got type: {type(interpretations)}"
        )

    state["card_interpretations"] = interpretations
    return state
