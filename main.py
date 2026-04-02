# Copyright (c) 2026 Marco De Roni. All rights reserved.
# Licensed under the MIT License — see LICENSE file for details.

import os
from colorama import Fore, Style, init
from reviewer.extractor import extract_text
from reviewer.analyzer import analyze_contract, load_settings
from reviewer.reporter import generate_report

init(autoreset=True)

CONTRACTS_DIR = "contracts"
OUTPUT_DIR = "output"


def main():
    settings = load_settings()
    provider = settings.get("provider", "groq")
    output_format = settings.get("output_format", "both")
    multi_agent = settings.get("multi_agent", False)
    mode = "MULTI-AGENT" if multi_agent else "SINGLE AGENT"

    print(Fore.WHITE + Style.BRIGHT + f"\n=== Legal GPT Reviewer | Provider: {provider.upper()} | Mode: {mode} ===\n")

    contracts = [
        f for f in os.listdir(CONTRACTS_DIR)
        if f.lower().endswith((".pdf", ".docx"))
    ]

    if not contracts:
        print(Fore.YELLOW + f"⚠️  Nessun contratto trovato in '{CONTRACTS_DIR}/'")
        print("   Metti uno o più file PDF o DOCX nella cartella contracts/ e riprova.")
        return

    print(Fore.CYAN + f"📂 {len(contracts)} contratto/i trovato/i\n")

    print(Fore.WHITE + "Vuoi aggiungere contesto? (es. 'we are the vendor, customer is a bank')")
    print(Fore.WHITE + "Premi INVIO per saltare: ", end="")
    context = input().strip()

    results = []
    for filename in contracts:
        path = os.path.join(CONTRACTS_DIR, filename)
        print(Fore.CYAN + f"\n📄 Analisi: {filename}")

        try:
            # Extract text
            print("   → Estrazione testo...")
            text = extract_text(path)
            print(f"   → {len(text)} caratteri estratti")

            # Sanitize PII
            try:
                from reviewer.sanitizer import sanitize, desanitize
                text, pii_mapping = sanitize(text)
                print(f"   → PII sanitizzato: {len(pii_mapping)} entità redatte")
            except Exception as e:
                pii_mapping = {}
                print(f"   → PII sanitization skipped: {e}")

            # Analyze
            if multi_agent:
                print(f"   → Avvio modalità MULTI-AGENT ({provider.upper()})...")
            else:
                print(f"   → Invio a {provider.upper()}...")

            analysis, provider_used = analyze_contract(text, context)

            # Restore PII in analysis
            if pii_mapping:
                from reviewer.sanitizer import desanitize
                analysis = desanitize(analysis, pii_mapping)

            # Print preview
            for line in analysis.split("\n")[:10]:
                if "OVERALL RISK" in line:
                    if "RED" in line:
                        print(Fore.RED + f"   {line}")
                    elif "YELLOW" in line:
                        print(Fore.YELLOW + f"   {line}")
                    elif "GREEN" in line:
                        print(Fore.GREEN + f"   {line}")
                elif line.strip():
                    print(f"   {line}")

            # Generate report
            print(f"\n   → Generazione report ({output_format})...")
            paths = generate_report(
                contract_name=filename,
                analysis=analysis,
                provider=provider_used,
                output_dir=OUTPUT_DIR,
                output_format=output_format
            )

            for fmt, p in paths.items():
                print(Fore.GREEN + f"   ✓ {fmt.upper()}: {p}")

            results.append({"filename": filename, "paths": paths})

        except Exception as e:
            print(Fore.RED + f"   ❌ Errore: {e}")

    print(Fore.WHITE + Style.BRIGHT + "\n" + "="*50)
    print(Fore.GREEN + f"✅ {len(results)} contratto/i analizzato/i.")
    print(f"   Report in: {OUTPUT_DIR}/")
    print("="*50)


if __name__ == "__main__":
    main()