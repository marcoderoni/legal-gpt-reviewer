# Copyright (c) 2026 Marco De Roni. All rights reserved.
# Licensed under the MIT License — see LICENSE file for details.

import os
import yaml
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT_BASE = """You are an expert legal contract reviewer assistant for a Senior Commercial Legal Counsel with EMEA experience in SaaS enterprise agreements, DPAs, and vendor contracts.

Your role is to:
1. REVIEW contracts and identify risk areas
2. FLAG clauses that deviate from market standard or are unacceptable
3. SUGGEST fallback language and negotiation positions
4. IDENTIFY missing clauses that should be present
5. FLAG clauses found in the contract that are NOT covered by the playbook positions

Always format your response exactly as follows:

## OVERALL RISK: [RED/YELLOW/GREEN]

## EXECUTIVE SUMMARY
[2-3 sentences summarising the main risk profile]

## KEY FINDINGS
[For each clause category, one bullet per finding with score]
- 🔴 [RED finding]
- 🟡 [YELLOW finding]
- 🟢 [GREEN finding]

## MISSING CLAUSES
[List any required clauses not found in the contract]

## CLAUSES WITHOUT PLAYBOOK GUIDANCE
IMPORTANT: You MUST include this section even if empty.
Scan the entire contract for clauses, provisions, or topics NOT covered
by the playbook positions listed below (e.g. payment terms, warranties,
audit rights, IP ownership, non-solicitation, etc.).
For each one found:
- ⚪ [CLAUSE NAME] — No playbook guidance — review manually and consider updating your playbook
If none found, write: "All major clauses covered by playbook."

## RECOMMENDED ACTIONS
[Prioritised list of actions to take]

## FALLBACK LANGUAGE
[For each RED finding, suggest specific fallback clause language]
"""


def load_settings(settings_path: str = "config/settings.yaml") -> dict:
    """Load settings from YAML file."""
    if not os.path.exists(settings_path):
        return {
            "provider": "groq",
            "groq_model": "llama-3.3-70b-versatile",
            "openai_model": "gpt-4o",
            "claude_model": "claude-sonnet-4-6",
            "max_chars": 12000,
            "output_format": "both",
            "multi_agent": False
        }
    with open(settings_path) as f:
        return yaml.safe_load(f)


def load_playbook(playbook_path: str = "config/playbook.yaml") -> str:
    """Load playbook positions and inject into system prompt."""
    if not os.path.exists(playbook_path):
        return ""

    with open(playbook_path) as f:
        playbook = yaml.safe_load(f)

    if not playbook:
        return ""

    positions = playbook.get("positions", {})
    required = playbook.get("required_clauses", [])

    prompt_addition = "\n\nKEY NEGOTIATION POSITIONS TO APPLY:\n"
    for clause, position in positions.items():
        prompt_addition += f"\n{clause.replace('_', ' ').upper()}:\n{position}\n"

    if required:
        prompt_addition += f"\nREQUIRED CLAUSES — flag if missing:\n"
        for clause in required:
            prompt_addition += f"- {clause}\n"

    prompt_addition += "\n\nAny clause found in the contract that is NOT listed above should be flagged under CLAUSES WITHOUT PLAYBOOK GUIDANCE."

    return prompt_addition


def get_playbook_clauses(playbook_path: str = "config/playbook.yaml") -> list:
    """Returns list of clause names covered in the playbook."""
    if not os.path.exists(playbook_path):
        return []
    with open(playbook_path) as f:
        playbook = yaml.safe_load(f)
    if not playbook:
        return []
    positions = playbook.get("positions", {})
    return [k.replace("_", " ") for k in positions.keys()]


def get_client(provider: str):
    """Return the appropriate AI client based on provider setting."""
    if provider == "groq":
        from groq import Groq
        return Groq(api_key=os.getenv("GROQ_API_KEY"))
    elif provider == "openai":
        from openai import OpenAI
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    elif provider == "claude":
        import anthropic
        return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    else:
        raise ValueError(f"Provider non supportato: {provider}")


def analyze_contract(text: str, context: str = "") -> tuple:
    """
    Analyzes contract using single agent or multi-agent mode.
    Returns (analysis_text, provider_used).
    """
    settings = load_settings()
    provider = settings.get("provider", "groq")
    max_chars = settings.get("max_chars", 12000)
    use_multi_agent = settings.get("multi_agent", False)

    # Select model
    if provider == "groq":
        model = settings.get("groq_model", "llama-3.3-70b-versatile")
    elif provider == "openai":
        model = settings.get("openai_model", "gpt-4o")
    elif provider == "claude":
        model = settings.get("claude_model", "claude-sonnet-4-6")
    else:
        model = settings.get("groq_model", "llama-3.3-70b-versatile")

    client = get_client(provider)

    if use_multi_agent:
        from reviewer.agents import run_multi_agent
        analysis, _ = run_multi_agent(text[:max_chars], context, client, model)
        return analysis, provider

    # Single agent mode
    playbook_context = load_playbook()
    system_prompt = SYSTEM_PROMPT_BASE + playbook_context

    # Sanitize PII before sending to API
    try:
        from reviewer.sanitizer import sanitize, desanitize
        sanitized_text, pii_mapping = sanitize(text[:max_chars])
        print(f"   → PII sanitizzato: {len(pii_mapping)} entità redatte")
    except Exception as e:
        print(f"   → PII sanitization skipped: {e}")
        sanitized_text = text[:max_chars]
        pii_mapping = {}

    # Build user message
    user_message = f"""Please review the following contract and provide a full risk assessment.

{f'Additional context: {context}' if context else ''}

Playbook clauses covered: {', '.join(get_playbook_clauses())}

CONTRACT TEXT:
{sanitized_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,
        max_tokens=2000,
    )

    result = response.choices[0].message.content
    if pii_mapping:
        from reviewer.sanitizer import desanitize
        result = desanitize(result, pii_mapping)
    return result, provider