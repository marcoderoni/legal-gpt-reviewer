# Copyright (c) 2025 Marco De Roni. All rights reserved.
# Licensed under the MIT License — see LICENSE file for details.

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert legal contract reviewer assistant for a Senior Commercial Legal Counsel with EMEA experience in SaaS enterprise agreements, DPAs, and vendor contracts.

Your role is to:
1. REVIEW contracts and identify risk areas
2. FLAG clauses that deviate from market standard or are unacceptable
3. SUGGEST fallback language and negotiation positions
4. IDENTIFY missing clauses that should be present

Key positions to apply:
- Liability cap: 12-month fees paid is market standard for SaaS. Maximum 2x-3x ACV for heightened caps. Never agree to unlimited liability including for data breach.
- Excluded damages: mutual exclusion of consequential/indirect damages is standard.
- Indemnification: must be mutual. Broad unilateral indemnification is RED.
- GDPR/Data Protection: always check for DPA reference, SCCs for international transfers, sub-processor approval mechanism.
- Termination for convenience: must be present with reasonable notice period (30-90 days).
- Governing law: flag if not clearly specified.

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
[List any required clauses not found]

## RECOMMENDED ACTIONS
[Prioritised list of actions to take]

## FALLBACK LANGUAGE
[For each RED finding, suggest specific fallback clause language]
"""


def analyze_contract(text: str, context: str = "") -> str:
    """
    Sends contract text to Groq (LLaMA 3) for analysis.
    Optional context: party perspective, governing law preference, etc.
    """
    user_message = f"""Please review the following contract and provide a full risk assessment.

{f'Additional context: {context}' if context else ''}

CONTRACT TEXT:
{text[:12000]}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,
        max_tokens=2000,
    )

    return response.choices[0].message.content