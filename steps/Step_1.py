"""
Step 1: Deciding the Spread  (LLM call)

INPUT  (read from state):  state["user_question"]
OUTPUT (written to state): state["spread"]
    {
        "core_theme": str,
        "spread_name": str,
        "positions": [
            {"position": int, "label": str, "focus": str},
            
        ]
    }

The LLM reads the user's raw question and decides:
  1. The core theme in a few words.
  2. The most fitting card spread for that theme.
  3. What each position in the spread should focus on.

This output is essential for Step 3 (Contextual Interpreter), which uses
the position labels and focus descriptions to shape each card's meaning.
"""

from grok_client import call_llm_json

SYSTEM_PROMPT = """You are an experienced tarot reader.
Your role is to read a client's question or situation and choose the most
appropriate tarot card spread for it, out of the common ones already available.

You must respond ONLY with a valid JSON object. No explanation, output raw JSON only.

The JSON must have exactly this structure:
{
  "core_theme": "<5 to 10 word summary of the central question>",
  "spread_name": "<name of the card spread chosen>",
  "positions": [
    {"position": 1, "label": "<position name>", "focus": "<what this position tells us>"},
    ...
  ]
}

Choose the spread that best fits the question's nature.

The position focus must be a short phrase describing what the card in that
slot will address, for example: "What led you here", "The hidden force at work",
"Where this path leads if followed".
"""


def run(state):
    """
    Reads:   state["user_question"]
    Writes:  state["spread"]
    Returns: updated state
    """
    question = state.get("user_question", "")
    if not question.strip():
        raise ValueError("Step 1 requires a non-empty 'user_question' in state.")

    user_prompt = f"The client asks: {question}"

    spread = call_llm_json(SYSTEM_PROMPT, user_prompt, temperature=0.5)

    # Validate structure
    required_keys = {"core_theme", "spread_name", "positions"}
    if not required_keys.issubset(spread.keys()):
        raise ValueError(
            f"Step 1 output is missing required keys. Got: {list(spread.keys())}"
        )

    state["spread"] = spread
    return state
