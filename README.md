# Tarot Agent

A multi-step LLM agent that delivers a tarot card reading through a five-stage
pipeline. Each stage produces structured output that feeds directly into the next.
The agent uses the Grok API (xAI) for all LLM calls and the tarotapi.dev public
API as its external tool.

---

## What the Agent Does

The user supplies a question or situation. The agent:

1. Analyzes the question and selects the most appropriate card spread.
2. Fetches the 78-card deck from tarotapi.dev and draws cards with random orientations.
3. Interprets each card in context of its spread position and the user's theme.
4. Synthesizes the interpretations into a cohesive narrative.
5. Formats everything into a structured Markdown report with actionable takeaways.

The report is printed to the terminal and saved to the outputs/ directory.

---

## Chain Structure

Step | Type       | Reads from State               | Writes to State
-----|------------|--------------------------------|-----------------------
  1  | LLM        | user_question                  | spread
  2  | Tool       | spread.positions               | drawn_cards
  3  | LLM        | spread, drawn_cards            | card_interpretations
  4  | LLM        | card_interpretations, spread   | narrative
  5  | LLM        | all previous outputs           | final_report

No step can be removed without breaking the chain. Step 3 requires outputs
from both Step 1 and Step 2. Step 5 requires all prior steps.

---

## Prerequisites

Python 3.8 or higher is required. No other system software is needed.


### Install dependencies

    pip install -r requirements.txt

Two dependencies are required: openai (to talk to the Grok API) and requests
(to fetch the tarot card deck from tarotapi.dev).

## API Key Setup

You need a Grok API key from xAI. Obtain one at: https://console.x.ai

Set the key as an environment variable before running the agent.

On macOS or Linux:
    export GROK_API_KEY=your_key_here

On Windows (Command Prompt):
    set GROK_API_KEY=your_key_here

On Windows (PowerShell):
    $env:GROK_API_KEY="your_key_here"

The agent will raise a clear error if this variable is not set.

Optional: override the default model (grok-beta):
    export GROK_MODEL=grok-3


## Running the Agent

### Interactive mode

    python main.py

The agent will ask for your question, then run the full pipeline.

### Supply a question directly

    python main.py "Will I succeed in my new career path?"

    python main.py --question "What is blocking me from finding peace?"

### Handling unexpected inputs

If you press Enter without typing a question, the agent uses a default question.
If the API key is missing, the agent exits with a clear setup message.
If any LLM step fails after three retries, the agent exits with the error details.
If the tarotapi.dev fetch fails, Step 2 raises a RuntimeError with the reason.


## Output

The final Markdown report is printed to the terminal and saved to:

    outputs/tarot_reading_YYYYMMDD_HHMMSS.md

## Project Structure

    tarot_agent/
    |
    |-- main.py                          Entry point
    |-- agent.py                         Orchestrator: manages state, calls steps
    |-- requirements.txt
    |-- README.md
    |
    |-- steps/
    |   |-- step1_spread_architect.py    LLM: identifies theme and selects spread
    |   |-- step2_draw_engine.py         Tool: fetches deck from tarotapi.dev, draws cards
    |   |-- step3_contextual_interpreter.py  LLM: per-card interpretation
    |   |-- step4_narrative_synthesizer.py   LLM: cohesive narrative
    |   |-- step5_action_formatter.py    LLM: final Markdown report
    |
    |
    |-- grok_client.py               Grok API wrapper with retry and JSON parsing
    |
    |-- outputs/                         Reports written here after each run

---
