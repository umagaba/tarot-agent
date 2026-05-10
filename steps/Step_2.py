"""
Step 2: Draw random cards  (TOOL call)

This step is the external tool
in the pipeline. It does not call the LLM.
It fetches the full 78-card tarot deck from the tarotapi.dev public API,
then draws cards using Python's random module, simulating the physical act
of shuffling and drawing from a deck.
The API (https://tarotapi.dev/api/v1/cards) serves as the external knowledge
source the LLM cannot produce reliably from training alone: exact card names,
authoritative keywords, and random draws that are truly unpredictable.

INPUT  (read from state):  state["spread"]["positions"]  (to know how many cards)
OUTPUT (written to state): state["drawn_cards"]
    [
        {
            "position": int,
            "label": str,
            "focus": str,
            "name": str,
            "arcana": str,
            "suit": str or None,
            "orientation": "Upright" or "Reversed",
            "keywords": [str, ...]   # orientation-appropriate keywords
        },
        ...
    ]
Error handling: if the API call fails or the dataset is empty, raises
RuntimeError with a descriptive message rather than allowing silent failure
downstream.
"""

import random
import requests

TAROT_API_URL = "https://tarotapi.dev/api/v1/cards"
ORIENTATIONS = ["Upright", "Reversed"]
# Slight bias toward upright, as in traditional tarot reading practice
ORIENTATION_WEIGHTS = [0.65, 0.35]


def fetch_deck():
    """
    Fetch all 78 tarot cards from the tarotapi.dev public API.

    Returns a list of card dicts with name, arcana, suit, keywords,
    and meanings fields.
    """
    try:
        response = requests.get(TAROT_API_URL, timeout=50)
        response.raise_for_status()
        return response.json()["cards"]
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Failed to fetch tarot card data from {TAROT_API_URL}: {exc}"
        )


def draw_cards(num_cards):
    """
    Randomly draw num_cards unique cards from the online deck.

    Parameters
    num_cards : int
        Number of cards to draw.

    Returns
    list of dict
        Each dict contains card fields plus 'orientation' and 'keywords'.
    """
    deck = fetch_deck()

    if not deck:
        raise RuntimeError(
            "The tarot card dataset is empty. "
            "Check that the tarotapi.dev API is reachable."
        )
    if num_cards > len(deck):
        raise RuntimeError(
            f"Requested {num_cards} cards but the deck only has {len(deck)}."
        )

    selected = random.sample(deck, num_cards)
    results = []
    for card in selected:
        orientation = random.choices(ORIENTATIONS, weights=ORIENTATION_WEIGHTS, k=1)[0]
        # API provides 'keywords' for upright and 'meanings.shadow' for reversed
        if orientation == "Upright":
            keywords = card.get("keywords", [])[:5]
        else:
            keywords = card.get("meanings", {}).get("shadow", [])[:5]
        results.append({
            "name":        card["name"],
            "arcana":      "Major" if "Major" in card.get("arcana", "") else "Minor",
            "suit":        card.get("suit"),
            "number":      card.get("number"),
            "orientation": orientation,
            "keywords":    keywords,
        })
    return results


def run(state):
    """
    Reads:   state["spread"]["positions"]
    Writes:  state["drawn_cards"]
    Returns: updated state
    """
    spread = state.get("spread")
    if not spread or "positions" not in spread:
        raise RuntimeError(
            "Step 2 requires state['spread']['positions'] from Step 1."
        )

    positions = spread["positions"]
    num_cards = len(positions)

    raw_cards = draw_cards(num_cards)

    # Attach position metadata to each drawn card
    drawn_cards = []
    for pos, card in zip(positions, raw_cards):
        drawn_cards.append({
            "position":    pos["position"],
            "label":       pos["label"],
            "focus":       pos["focus"],
            "name":        card["name"],
            "arcana":      card["arcana"],
            "suit":        card["suit"],
            "number":      card["number"],
            "orientation": card["orientation"],
            "keywords":    card["keywords"],
        })

    state["drawn_cards"] = drawn_cards
    return state
