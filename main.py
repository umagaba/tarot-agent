"""
main.py  --  Tarot Agent Entry Point

Usage:
    python main.py
    python main.py "Will I succeed in my new business venture?"
    python main.py --question "What does this relationship hold for me?"

The agent accepts an optional question via command-line argument or
prompts interactively if none is supplied.
"""

import sys
import os
import argparse

# Make imports work from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import run


def main():
    parser = argparse.ArgumentParser(
        description="Tarot Agent: a multi-step LLM tarot reading pipeline."
    )
    parser.add_argument(
        "question",
        nargs="?",
        default=None,
        help="Your tarot question (optional; prompted interactively if omitted).",
    )
    parser.add_argument(
        "--question",
        dest="question_flag",
        default=None,
        metavar="QUESTION",
        help="Alternate way to supply the question.",
    )
    args = parser.parse_args()

    print("\n  TAROT AGENT  --  A multi-step AI tarot reading pipeline\n")

    # Resolve question source
    question = args.question or args.question_flag

    if not question:
        print("  What question would you like the cards to illuminate?")
        question = input("\n  Your question: ").strip()

    if not question.strip():
        question = "What should I focus on in this period of my life?"
        print(f"  No input detected. Using default: '{question}'")

    try:
        run(question)
    except EnvironmentError as exc:
        print(f"\n  [SETUP ERROR] {exc}")
        print("  Set your Grok API key:  export GROK_API_KEY=your_key_here")
        sys.exit(1)
    except RuntimeError as exc:
        print(f"\n  [RUNTIME ERROR] {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n  Reading interrupted. Farewell.")
        sys.exit(0)


if __name__ == "__main__":
    main()
