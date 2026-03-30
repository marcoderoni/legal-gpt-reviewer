# Legal GPT Reviewer

**Copyright (c) 2026 Marco De Roni. All rights reserved.**  
Licensed under the [MIT License](LICENSE).

---

## Overview

Legal GPT Reviewer is a provider-agnostic AI contract review tool built in Python.  
Upload a PDF or DOCX contract and get an instant risk assessment — scored as  
🔴 Red / 🟡 Yellow / 🟢 Green — with fallback language suggestions, missing clause  
detection, and professional Word + PDF reports.

Supports **Groq (free)** and **OpenAI GPT-4o (paid)** — switch provider with one  
line in the config file. No code changes needed.

Features a **multi-agent architecture**: specialist AI agents review each clause  
category independently (LOL, Indemnification, Data Protection, Termination),  
then a coordinator agent synthesises the findings into a single report.

Built by a Senior Commercial Legal Counsel with EMEA experience in SaaS  
enterprise contracting, GDPR compliance, and risk assessment.

---

## Features

- 🤖 **Provider-agnostic** — works with Groq (LLaMA 3.3, free) or OpenAI (GPT-4o)
- 🧠 **Multi-agent architecture** — specialist agents per clause type + coordinator
- 📄 **Multi-format input** — reads PDF and DOCX contracts
- 🔴🟡🟢 **Risk scoring** — Red/Yellow/Green assessment per clause category
- 📋 **Missing clause detection** — flags required clauses not found
- ⚪ **Playbook gap detection** — flags clauses with no guidance in your playbook
- 💬 **Fallback language** — suggests specific negotiation language for RED findings
- ⚙️ **Customisable playbook** — define your own positions in YAML, no code changes
- 📝 **Dual output** — generates Word + PDF report automatically
- 🌍 **Multilingual** — responds in the same language as the user prompt

---

## Multi-Agent Architecture

In multi-agent mode, the contract is reviewed by 5 specialist agents in parallel,  
then a coordinator synthesises all findings:
```
Contract
    ↓
┌─────────────────────────────────────────┐
│           Specialist Agents             │
├──────────┬──────────────┬───────────────┤
│ LOL      │ Indemnif.    │ Data Protect. │
│ Agent    │ Agent        │ Agent         │
├──────────┴──────┬───────┴───────────────┤
│ Termination     │ General Agent         │
│ Agent           │ (all other clauses)   │
└─────────────────┴───────────────────────┘
    ↓
Coordinator Agent (synthesises all findings)
    ↓
Final Report (Word + PDF)
```

Switch between single and multi-agent mode in `config/settings.yaml`:
```yaml
multi_agent: true   # specialist agents (more accurate, slower)
multi_agent: false  # single agent (faster)
```

---

## Project Structure
```
legal-gpt-reviewer/
├── config/
│   ├── playbook.example.yaml   # Template playbook — copy and customise
│   ├── playbook.yaml           # Your playbook (excluded from git)
│   ├── settings.example.yaml  # Template settings — copy and customise
│   └── settings.yaml          # Your settings (excluded from git)
├── contracts/                  # Drop your PDF/DOCX files here (excluded from git)
├── output/                     # Generated Word + PDF reports (excluded from git)
├── reviewer/
│   ├── extractor.py            # PDF and DOCX text extraction
│   ├── analyzer.py             # AI analysis — multi-provider support
│   ├── agents.py               # Multi-agent architecture
│   └── reporter.py             # Word and PDF report generation
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── .env.example                # API key template
├── LICENSE                     # MIT License
└── README.md
```

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/marcoderoni/legal-gpt-reviewer.git
cd legal-gpt-reviewer
```

### 2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API key
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
# For Groq (free): https://console.groq.com
GROQ_API_KEY=your-groq-key-here

# For OpenAI (paid): https://platform.openai.com
OPENAI_API_KEY=your-openai-key-here
```

### 5. Configure settings and playbook
```bash
cp config/settings.example.yaml config/settings.yaml
cp config/playbook.example.yaml config/playbook.yaml
```

Edit `config/settings.yaml`:
```yaml
provider: "groq"       # "groq" (free) or "openai" (paid)
output_format: "both"  # "docx", "pdf", or "both"
multi_agent: true      # true = specialist agents | false = single agent
```

Edit `config/playbook.yaml` to define your own negotiation positions.  
Both files are excluded from git — your configuration stays private.

### 6. Add contracts

Drop one or more `.pdf` or `.docx` files into the `contracts/` folder.

### 7. Run
```bash
python3 main.py
```

---

## Example Terminal Output
```
=== Legal GPT Reviewer | Provider: GROQ | Mode: MULTI-AGENT ===

📂 1 contratto/i trovato/i

📄 Analisi: MSA_VendorX.pdf
   → Estrazione testo...
   → 45,231 caratteri estratti
   → Avvio modalità MULTI-AGENT (GROQ)...
      → LOL Agent...
      → Indemnification Agent...
      → Data Protection Agent...
      → Termination Agent...
      → General Agent...
      → Coordinator Agent...
   ## OVERALL RISK: RED

   ✓ DOCX: output/report_MSA_VendorX.pdf.docx
   ✓ PDF:  output/report_MSA_VendorX.pdf.pdf

✅ 1 contratto/i analizzato/i.
```

---

## Switching Providers
```yaml
# Free — LLaMA 3.3 70B via Groq
provider: "groq"

# Paid — GPT-4o via OpenAI
provider: "openai"
```

---

## Privacy & Security

- `contracts/` excluded from git — documents never leave your machine
- `config/playbook.yaml` excluded from git — positions stay private
- `.env` excluded from git — API keys stay private
- All processing via API call to chosen provider (Groq or OpenAI)

---

## Requirements

- Python 3.9+
- groq · openai · pdfplumber · python-docx · pyyaml · python-dotenv · colorama · docx2pdf

---

## Related Projects

- **[Legal AI Toolkit](https://github.com/marcoderoni/Legal-AI-Toolkit)** — Claude Code agent
- **[Contract Scanner](https://github.com/marcoderoni/Contract-Scanner)** — rule-based single contract reviewer
- **[Contract Bulk Analyzer](https://github.com/marcoderoni/contract-bulk-analyzer)** — bulk analysis across multiple contracts
- **[Legal Contract Reviewer GPT](https://chatgpt.com/g/g-69c27871fb5081918e728d75d9a74fcf-legal-contract-reviewer)** — Custom GPT version

---

## Author

**Marco De Roni**  
Senior Commercial Legal Counsel | EMEA  
[LinkedIn](https://linkedin.com/in/marcoderoni) · [GitHub](https://github.com/marcoderoni)

---

## License

MIT License — see [LICENSE](LICENSE) for details.