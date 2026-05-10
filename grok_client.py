"""
Grok API client wrapper.

Wraps calls to the xAI Grok API (OpenAI-compatible endpoint).
All LLM steps in the agent call through this module.
"""

import os
import json
import re
import time

try:
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "The 'openai' package is required. Run: pip install openai"
    )

DEFAULT_MODEL = "grok-beta"
BASE_URL = "https://api.x.ai/v1"
MAX_RETRIES = 3
RETRY_DELAY = 2.0


def _get_client():
    api_key = os.environ.get("GROK_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROK_API_KEY environment variable is not set. "
            "Export your xAI API key before running the agent."
        )
    return OpenAI(api_key=api_key, base_url=BASE_URL)


def call_llm(system_prompt, user_prompt, temperature=0.7, max_tokens=1500):
    """
    Make a single call to the Grok LLM.

    Returns the raw text content of the assistant reply.
    Raises RuntimeError after MAX_RETRIES failed attempts.
    """
    client = _get_client()
    model = os.environ.get("GROK_MODEL", DEFAULT_MODEL)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"Grok API call failed after {MAX_RETRIES} attempts: {exc}"
                )
            time.sleep(RETRY_DELAY)


def call_llm_json(system_prompt, user_prompt, temperature=0.3, max_tokens=1500):
    """
    Call the Grok LLM and parse the response as JSON.

    The system prompt must instruct the model to respond ONLY with valid JSON.
    Returns a parsed Python dict or list.
    Raises ValueError if JSON cannot be extracted.
    """
    raw = call_llm(system_prompt, user_prompt, temperature=temperature,
                   max_tokens=max_tokens)
    return _parse_json(raw)


def _parse_json(text):
    """
    Attempt to extract and parse JSON from a model response.
    Handles raw JSON, markdown code fences, and embedded JSON objects/arrays.
    """
    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip markdown code fences
    fence_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Find first JSON object
    obj_match = re.search(r"\{[\s\S]+\}", text)
    if obj_match:
        try:
            return json.loads(obj_match.group(0))
        except json.JSONDecodeError:
            pass

    # Find first JSON array
    arr_match = re.search(r"\[[\s\S]+\]", text)
    if arr_match:
        try:
            return json.loads(arr_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(
        f"Could not parse valid JSON from model response.\n"
        f"Raw response was:\n{text[:500]}"
    )
