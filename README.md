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

Built by a Senior Commercial Legal Counsel with EMEA experience in SaaS  
enterprise contracting, GDPR compliance, and risk assessment.

---

## Features

- 🤖 **Provider-agnostic** — works with Groq (LLaMA 3.3, free) or OpenAI (GPT-4o)
- 📄 **Multi-format input** — reads PDF and DOCX contracts
- 🔴🟡🟢 **Risk scoring** — Red/Yellow/Green assessment per clause category
- 📋 **Missing clause detection** — flags required clauses not found
- 💬 **Fallback language** — suggests specific negotiation language for RED findings
- ⚙️ **Customisable playbook** — define your own positions in YAML, no code changes
- 📝 **Dual output** — generates Word + PDF report automatically
- 🌍 **Multilingual** — responds in the same language as the user prompt

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

Edit `config/settings.yaml` to choose your provider:
```yaml
provider: "groq"      # "groq" (free) or "openai" (paid)
output_format: "both" # "docx", "pdf", or "both"
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

## Switching Providers

Change one line in `config/settings.yaml`:
```yaml
# Free — uses LLaMA 3.3 70B via Groq
provider: "groq"

# Paid — uses GPT-4o via OpenAI
provider: "openai"
```

No other changes needed.

---

## Customising the Playbook

Define your negotiation positions in `config/playbook.yaml`:
```yaml
positions:
  limitation_of_liability: |
    Standard cap: 12 months fees paid.
    Maximum: 3x ACV — anything above requires escalation.
    Never accept unlimited liability.

  termination: |
    Termination for convenience must be present.
    Standard notice period: 30-90 days.

required_clauses:
  - "Limitation of Liability"
  - "Data Protection / GDPR"
  - "Termination"
```

---

## Example Output
```
=== Legal GPT Reviewer | Provider: GROQ ===

📂 1 contratto/i trovato/i

📄 Analisi: MSA_VendorX.pdf
   → Estrazione testo...
   → 45,231 caratteri estratti
   → Invio a GROQ...
   ## OVERALL RISK: RED
   ## EXECUTIVE SUMMARY
   The agreement contains several vendor-favorable provisions...

   ✓ DOCX: output/report_MSA_VendorX.pdf.docx
   ✓ PDF:  output/report_MSA_VendorX.pdf.pdf

✅ 1 contratto/i analizzato/i.
```

---

## Privacy & Security

- `contracts/` is excluded from git — your documents never leave your machine
- `config/playbook.yaml` is excluded from git — your positions stay private
- `.env` is excluded from git — your API keys stay private
- Groq option: data sent to Groq API (see their privacy policy)
- OpenAI option: data sent to OpenAI API (see their privacy policy)

---

## Requirements

- Python 3.9+
- groq
- openai
- pdfplumber
- python-docx
- pyyaml
- python-dotenv
- colorama
- docx2pdf

---

## Related Projects

- **[Legal AI Toolkit](https://github.com/marcoderoni/Legal-AI-Toolkit)** — Claude Code agent for contract review
- **[Contract Scanner](https://github.com/marcoderoni/Contract-Scanner)** — Python rule-based single contract reviewer
- **[Contract Bulk Analyzer](https://github.com/marcoderoni/contract-bulk-analyzer)** — Python bulk analysis across multiple contracts
- **[Legal Contract Reviewer GPT](https://chatgpt.com/g/g-69c27871fb5081918e728d75d9a74fcf-legal-contract-reviewer)** — Custom GPT version (no installation required)

---

## Author

**Marco De Roni**  
Senior Commercial Legal Counsel | EMEA  
[LinkedIn](https://linkedin.com/in/marcoderoni) · [GitHub](https://github.com/marcoderoni)

---

## License

MIT License — see [LICENSE](LICENSE) for details.