"""
Step 5: Advisor (LLM call)

This is the final step in the chain. It looks at everything the agent has
accumulated and produces the structured output: a formatted Markdown report
the clientt can save, print, or act on.

The report contains:
  - The question and spread name
  - Each drawn card with its position and keywords
  - The narrative reading
  - Concrete, actionable takeaways grounded in the cards

The reason this is a separate step rather than appending to Step 4 is that
Step 4 is purely interpretive narrative (voice and insight), while Step 5 is
structural formatting (layout, action extraction, and presentation). Combining
them would produce a prompt that is trying to do two different cognitive tasks
at once, which reliably degrades output quality.

INPUT  (read from state): entire state object
OUTPUT (written to state): state["final_report"]  (Markdown string)
"""

from grok_client import call_llm

SYSTEM_PROMPT = """You are a tarot reading assistant responsible for producing
the final written report of a session.

You will receive all the information gathered during the reading: the question,
the spread, each drawn card with its orientation, the narrative, and the
individual interpretations. Assemble this into a clean, structured Markdown
report.

The report must follow this exact structure:

# Tarot Reading Report

## Your Question
<the client's question, verbatim>

## The Spread: <spread name>
<one sentence describing what this spread reveals>

## The Cards

For each card:
### Position <N>: <Position Label>
**<Card Name>** (<Orientation>)
Focus: <position focus>
Keywords: <comma-separated keywords>

<the per-card interpretation from the reading>

## The Reading
<the full narrative, unchanged, as it was written>

## Actionable Takeaways
Each takeaway must be a concrete real-world action or mindset shift grounded
directly in one of the cards. Be specific, not generic (can be one or multiple).

Do not add any closing disclaimers. Do not use hyphens as bullet points.
Use only the markdown formatting shown above.
"""


def _build_user_prompt(state):
    question = state["user_question"]
    spread = state["spread"]
    drawn = state.get("drawn_cards", [])
    interpretations = state.get("card_interpretations", [])
    narrative = state.get("narrative", "")

    cards_block = []
    for card in drawn:
        kw_str = ", ".join(card["keywords"])
        # Find matching interpretation
        interp = ""
        for item in interpretations:
            if item.get("position") == card["position"]:
                interp = item.get("interpretation", "")
                break
        cards_block.append(
            f"Position {card['position']} | {card['label']} | Focus: {card['focus']}\n"
            f"Card: {card['name']} ({card['orientation']})\n"
            f"Keywords: {kw_str}\n"
            f"Interpretation: {interp}"
        )

    cards_text = "\n\n".join(cards_block)

    return (
        f"Question: {question}\n"
        f"Spread name: {spread['spread_name']}\n"
        f"Core theme: {spread['core_theme']}\n\n"
        f"Cards:\n\n{cards_text}\n\n"
        f"Narrative:\n{narrative}"
    )


def run(state):
    """
    Reads: entire state (all previous step outputs)
    Writes: state["final_report"]
    Returns: updated state
    """
    for key in ("user_question", "spread", "drawn_cards",
                "card_interpretations", "narrative"):
        if not state.get(key):
            raise RuntimeError(
                f"Step 5 requires state['{key}']. "
                "Ensure all previous steps completed successfully."
            )

    user_prompt = _build_user_prompt(state)
    final_report = call_llm(SYSTEM_PROMPT, user_prompt, temperature=0.5)

    state["final_report"] = final_report
    return state
