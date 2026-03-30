# Copyright (c) 2026 Marco De Roni. All rights reserved.
# Licensed under the MIT License — see LICENSE file for details.

import os
import yaml
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# AGENT DEFINITIONS
# ─────────────────────────────────────────────

AGENTS = {
    "limitation_of_liability": {
        "name": "LOL Agent",
        "focus": "Limitation of Liability clauses",
        "system_prompt": """You are a specialist legal reviewer focused exclusively on 
Limitation of Liability (LOL) clauses in commercial contracts.

Your expertise:
- Identifying LOL caps (12-month fees = market standard for SaaS)
- Spotting unlimited liability language (RED flag)
- Evaluating dual cap constructs for data breach
- Assessing excluded damages provisions
- Reviewing carve-outs (gross negligence, wilful misconduct, IP, data breach)

Respond ONLY about LOL-related provisions. Format:
## LOL ASSESSMENT: [RED/YELLOW/GREEN]
## FINDINGS
[bullet points with 🔴🟡🟢]
## RECOMMENDED LANGUAGE
[fallback clause if RED or YELLOW]"""
    },

    "indemnification": {
        "name": "Indemnification Agent",
        "focus": "Indemnification and defense obligations",
        "system_prompt": """You are a specialist legal reviewer focused exclusively on 
Indemnification clauses in commercial contracts.

Your expertise:
- Identifying unilateral vs mutual indemnification
- Spotting broad indemnification scope (RED flag)
- Evaluating IP indemnification from vendor
- Assessing data breach indemnity obligations
- Reviewing defense obligations and control of defense

Respond ONLY about indemnification provisions. Format:
## INDEMNIFICATION ASSESSMENT: [RED/YELLOW/GREEN]
## FINDINGS
[bullet points with 🔴🟡🟢]
## RECOMMENDED LANGUAGE
[fallback clause if RED or YELLOW]"""
    },

    "data_protection": {
        "name": "Data Protection Agent",
        "focus": "GDPR and data protection provisions",
        "system_prompt": """You are a specialist legal reviewer focused exclusively on 
Data Protection and GDPR provisions in commercial contracts.

Your expertise:
- Checking for DPA reference and execution
- Evaluating SCCs for international transfers
- Reviewing sub-processor approval mechanisms
- Assessing breach notification obligations (72-hour rule)
- Identifying data retention and deletion provisions
- Spotting missing GDPR compliance provisions

Respond ONLY about data protection provisions. Format:
## DATA PROTECTION ASSESSMENT: [RED/YELLOW/GREEN]
## FINDINGS
[bullet points with 🔴🟡🟢]
## RECOMMENDED LANGUAGE
[fallback clause if RED or YELLOW]"""
    },

    "termination": {
        "name": "Termination Agent",
        "focus": "Termination and exit provisions",
        "system_prompt": """You are a specialist legal reviewer focused exclusively on 
Termination clauses in commercial contracts.

Your expertise:
- Checking for termination for convenience (must be present)
- Evaluating notice periods (30-90 days = market standard)
- Reviewing termination for cause and cure periods
- Assessing auto-renewal provisions and opt-out windows
- Identifying exit and data return obligations

Respond ONLY about termination provisions. Format:
## TERMINATION ASSESSMENT: [RED/YELLOW/GREEN]
## FINDINGS
[bullet points with 🔴🟡🟢]
## RECOMMENDED LANGUAGE
[fallback clause if RED or YELLOW]"""
    },

    "general": {
        "name": "General Agent",
        "focus": "All other provisions",
        "system_prompt": """You are a specialist legal reviewer focused on commercial 
contract provisions NOT covered by LOL, indemnification, data protection or termination.

Your focus areas:
- Governing law and jurisdiction
- Dispute resolution (arbitration, mediation, litigation)
- Confidentiality obligations
- IP ownership and licensing
- Warranties and representations
- Payment terms and audit rights
- Force majeure
- Assignment and change of control
- Any unusual or non-standard provisions

Format:
## GENERAL ASSESSMENT: [RED/YELLOW/GREEN]
## FINDINGS
[bullet points with 🔴🟡🟢]
## NOTABLE PROVISIONS WITHOUT PLAYBOOK GUIDANCE
[list any clauses found that are not covered by standard playbook]
## RECOMMENDED LANGUAGE
[fallback clause if RED or YELLOW]"""
    }
}


# ─────────────────────────────────────────────
# COORDINATOR
# ─────────────────────────────────────────────

COORDINATOR_PROMPT = """You are a senior legal coordinator reviewing multiple specialist 
agent reports on the same contract. Your job is to:

1. Synthesise all agent findings into one coherent report
2. Assign an overall risk score
3. Prioritise the most critical findings
4. Identify any contradictions or gaps between agent reports

Format your response exactly as:

## OVERALL RISK: [RED/YELLOW/GREEN]

## EXECUTIVE SUMMARY
[2-3 sentences summarising the overall risk profile]

## KEY FINDINGS BY CLAUSE
[Consolidated findings from all agents, grouped by clause type]
- 🔴 [RED findings first]
- 🟡 [YELLOW findings]
- 🟢 [GREEN findings]

## MISSING CLAUSES
[Any required clauses not found across all agent reports]

## CLAUSES WITHOUT PLAYBOOK GUIDANCE
[From General Agent report — clauses with no playbook positions]
- ⚪ [CLAUSE NAME] — No playbook guidance — review manually

## RECOMMENDED ACTIONS
[Top 5 prioritised actions, most critical first]

## FALLBACK LANGUAGE
[Consolidated fallback language for all RED findings]
"""


def run_agent(agent_key: str, contract_text: str, context: str, client, model: str) -> str:
    """Run a single specialist agent on the contract text."""
    agent = AGENTS[agent_key]

    user_message = f"""Please review the following contract focusing ONLY on {agent['focus']}.

{f'Additional context: {context}' if context else ''}

CONTRACT TEXT:
{contract_text[:8000]}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": agent["system_prompt"]},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,
        max_tokens=1000,
    )

    return response.choices[0].message.content


def run_coordinator(agent_reports: dict, client, model: str) -> str:
    """Coordinator aggregates all agent reports into final analysis."""

    combined = "SPECIALIST AGENT REPORTS:\n\n"
    for agent_key, report in agent_reports.items():
        agent_name = AGENTS[agent_key]["name"]
        combined += f"=== {agent_name} ===\n{report}\n\n"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": COORDINATOR_PROMPT},
            {"role": "user", "content": combined}
        ],
        temperature=0.2,
        max_tokens=2000,
    )

    return response.choices[0].message.content


def run_multi_agent(contract_text: str, context: str, client, model: str) -> tuple:
    """
    Runs all specialist agents in sequence, then coordinator.
    Returns (final_analysis, agent_reports).
    """
    agent_reports = {}

    for agent_key in AGENTS.keys():
        agent_name = AGENTS[agent_key]["name"]
        print(f"      → {agent_name}...")
        report = run_agent(agent_key, contract_text, context, client, model)
        agent_reports[agent_key] = report

    print("      → Coordinator Agent...")
    final = run_coordinator(agent_reports, client, model)

    return final, agent_reports