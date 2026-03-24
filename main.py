# Copyright (c) 2025 Marco De Roni. All rights reserved.
# Licensed under the MIT License — see LICENSE file for details.

import os
import sys
from colorama import Fore, Style, init
from reviewer.extractor import extract_text
from reviewer.analyzer import analyze_contract
from reviewer.reporter import generate_report

init(autoreset=True)

CONTRACTS_DIR = "contracts"
OUTPUT_DIR = "output"


def main():
    print(Fore.WHITE + Style.BRIGHT + "\n=== Legal GPT Reviewer | Powered by GPT-4o ===\n")

    # Find contracts
    contracts = [
        f for f in os.listdir(CONTRACTS_DIR)
        if f.lower().endswith((".pdf", ".docx"))
    ]

    if not contracts:
        print(Fore.YELLOW + f"⚠️  Nessun contratto trovato in '{CONTRACTS_DIR}/'")
        print("   Metti uno o più file PDF o DOCX nella cartella contracts/ e riprova.")
        return

    print(Fore.CYAN + f"📂 {len(contracts)} contratto/i trovato/i\n")

    # Optional context
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

            # Analyze with GPT-4o
            print("   → Invio a GPT-4o...")
            analysis = analyze_contract(text, context)

            # Print summary to terminal
            lines = analysis.split("\n")
            for line in lines[:10]:  # Print first 10 lines as preview
                if "RED" in line and "OVERALL" in line:
                    print(Fore.RED + f"   {line}")
                elif "YELLOW" in line and "OVERALL" in line:
                    print(Fore.YELLOW + f"   {line}")
                elif "GREEN" in line and "OVERALL" in line:
                    print(Fore.GREEN + f"   {line}")
                elif line.strip():
                    print(f"   {line}")

            # Generate Word report
            print("\n   → Generazione report Word...")
            report_path = generate_report(filename, analysis, OUTPUT_DIR)
            print(Fore.GREEN + f"   ✓ Report: {report_path}")

            results.append({"filename": filename, "report": report_path})

        except Exception as e:
            print(Fore.RED + f"   ❌ Errore: {e}")

    print(Fore.WHITE + Style.BRIGHT + "\n" + "="*50)
    print(Fore.GREEN + f"✅ {len(results)} contratto/i analizzato/i.")
    print(f"   Report in: {OUTPUT_DIR}/")
    print("="*50)


if __name__ == "__main__":
    main()