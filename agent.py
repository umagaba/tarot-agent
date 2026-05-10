"""
agent.py  --  Tarot Agent Orchestrator

Maintains the shared state dictionary and executes all five steps in order.
Each step reads from and writes to state.

State schema after full execution:
{
    "user_question":        str,          # raw input
    "spread":               dict,         # Step 1 output
    "drawn_cards":          list[dict],   # Step 2 output
    "card_interpretations": list[dict],   # Step 3 output
    "narrative":            str,          # Step 4 output
    "final_report":         str,          # Step 5 output
}
"""

import os
import time
from datetime import datetime

import steps.Step_1 as step1
import steps.Step_2 as step2
import steps.Step_3 as step3
import steps.Step_4 as step4
import steps.Step_5 as step5


TOTAL_STEPS = 5

def _save_report(report_text, output_dir="outputs"):
    """Write the final Markdown report to a timestamped file."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tarot_reading_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    return filepath


def run(question):
    """
    Execute the full five-step tarot agent pipeline.

    Parameters
    question : str
        The querent's question or situation description.

    Returns
    dict
        The final state object containing all intermediate and final outputs.
    """
    state = {"user_question": question}

    print(f"\n  [ Step 1 of {TOTAL_STEPS} ] Deciding the Spread   (LLM)")
    print("  Reading your question and choosing a spread...")

    try:
        state = step1.run(state)
    except Exception as exc:
        print(f"\n  [ERROR] Step 1 failed: {exc}")
        raise

    spread = state["spread"]
    print(f"\n  Theme    : {spread['core_theme']}")
    print(f"  Spread   : {spread['spread_name']}")
    for pos in spread["positions"]:
        print(f"    Position {pos['position']} - {pos['label']}: {pos['focus']}")   
   
    input("\n  Press Enter to draw the cards...")
    print(f"\n  [ Step 2 of {TOTAL_STEPS} ]  Draw random cards  (TOOL call)")
    print("  Fetching deck and drawing cards...")

    try:
        state = step2.run(state)
    except Exception as exc:
        print(f"\n  [ERROR] Step 2 failed: {exc}")
        raise

    print("\n  Cards drawn:")
    for card in state["drawn_cards"]:
        print(f"    {card['position']}. {card['name']} ({card['orientation']})  |  {', '.join(card['keywords'][:3])}")

    input("\n  Press Enter to begin the reading...")

    print(f"\n  [ Step 3 of {TOTAL_STEPS} ]  Interpretation of the Context  (LLM call)")
    print("  Interpreting each card in its position...")

    try:
        state = step3.run(state)
    except Exception as exc:
        print(f"\n  [ERROR] Step 3 failed: {exc}")
        raise

    print("\n  Card by Card:")
    for interp in state["card_interpretations"]:
        print(f"\n    {interp.get('label', '')}  --  {interp.get('card', '')} ({interp.get('orientation', '')})")
        print(f"    {interp.get('interpretation', '')}")

    
    print(f"\n  [ Step 4 of {TOTAL_STEPS} ]  Building a Narrative   (LLM)")
    print("  Weaving the cards into a single narrative...")

    try:
        state = step4.run(state)
    except Exception as exc:
        print(f"\n  [ERROR] Step 4 failed: {exc}")
        raise

    print(f"\n  [ Step 5 of {TOTAL_STEPS} ]  Final Answer  (LLM)")
    print("  Composing the final report...")
    
    try:
        state = step5.run(state)
    except Exception as exc:
        print(f"\n  [ERROR] Step 5 failed: {exc}")
        raise

    print("  YOUR TAROT READING")
    print(state["final_report"])

    filepath = _save_report(state["final_report"])
    print(f"\n  Report saved to: {filepath}\n")
    
    return state
