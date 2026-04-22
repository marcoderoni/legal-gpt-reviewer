# Copyright (c) 2026 Marco De Roni. All rights reserved.
# Licensed under the MIT License — see LICENSE file for details.

import os
import json
import hashlib
from datetime import datetime

AUDIT_LOG_PATH = "audit_log.jsonl"


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def log_analysis(
    contract_name: str,
    overall_risk: str,
    provider: str,
    mode: str,
    pii_entities: int = 0
):
    """Append an audit entry to the log file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "contract": contract_name,
        "overall_risk": overall_risk,
        "provider": provider,
        "mode": mode,
        "pii_entities_redacted": pii_entities,
    }
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = compute_hash(entry_str)

    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry