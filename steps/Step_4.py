"""
Step 4: Building a Narrative  (LLM call)

This step takes the isolated per-card interpretations from Step 3 and builds
them into a single, cohesive narrative.

INPUT  (read from state):
    state["card_interpretations"]  from Step 3
    state["spread"]                from Step 1 (for context)
    state["user_question"]         

OUTPUT (written to state): state["narrative"]   (plain text block)
"""

from grok_client import call_llm

SYSTEM_PROMPT = """You are a experienced tarot reader delivering a reading.
You have already interpreted each card individually. Now you must build a narrative around the interpretations of the cards in such a way that it fits the original question of the client.

Your narrative must:
  1. Open by acknowledging what the spread as a whole seems to be saying.
  2. Note any significant patterns: all Major Arcana, mixed suits, dominant
     elements (Wands=Fire, Cups=Water, Swords=Air, Pentacles=Earth), or
     thematic similarities across positions.
  3. Describe how the cards speak to each other.
  4. Close with a sentence that answers the core question
     as directly as the cards allow. Acknowledge it if you are unsure, do not force connections. 

Write in the second person (you, your). Do not use bullet points.
Write 3 to 5 paragraphs. Do not use markdown headers.
Do not pad with disclaimers about tarot being for entertainment.
Speak as a skilled, honest reader who takes the work seriously, and is not afraid to say I don't know.
"""


def _build_user_prompt(state):
    question = state["user_question"]
    spread = state["spread"]
    interpretations = state["card_interpretations"]

    drawn = state.get("drawn_cards", [])
    arcana_counts = {"Major": 0, "Minor": 0}
    suits = []
    for card in drawn:
        arcana_counts[card["arcana"]] += 1
        if card["suit"]:
            suits.append(card["suit"])

    interp_block = []
    for item in interpretations:
        interp_block.append(
            f"Position {item['position']} ({item['label']}): "
            f"{item['card']} ({item['orientation']})\n"
            f"{item['interpretation']}"
        )
    interp_text = "\n\n".join(interp_block)

    suit_summary = ", ".join(suits) if suits else "none"

    return (
        f"The client asks: {question}\n"
        f"Core theme: {spread['core_theme']}\n"
        f"Spread: {spread['spread_name']}\n\n"
        f"Arcana balance: {arcana_counts['Major']} Major, {arcana_counts['Minor']} Minor\n"
        f"Suits present: {suit_summary}\n\n"
        f"Individual card interpretations:\n\n{interp_text}"
    )


def run(state):
    """
    Reads:   state["card_interpretations"], state["spread"], state["user_question"],
             state["drawn_cards"]
    Writes:  state["narrative"]
    Returns: updated state
    """
    for key in ("card_interpretations", "spread", "user_question"):
        if not state.get(key):
            raise RuntimeError(f"Step 4 requires state['{key}'] to be populated.")

    user_prompt = _build_user_prompt(state)
    narrative = call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.75)
                         

    state["narrative"] = narrative
    return state
