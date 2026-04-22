# Copyright (c) 2026 Marco De Roni. All rights reserved.
# Licensed under the MIT License — see LICENSE file for details.

import streamlit as st
import os
import tempfile
import warnings
warnings.filterwarnings("ignore")
from reviewer.extractor import extract_text
from reviewer.analyzer import analyze_contract, load_settings
from reviewer.reporter import generate_report

st.set_page_config(
    page_title="Legal GPT Reviewer",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Legal GPT Reviewer")
st.caption("AI-powered contract review — multi-agent analysis with R/Y/G risk scoring, missing clause detection and PII protection")

# ── Sidebar ──
with st.sidebar:
    st.header("⚙️ Configuration")

    settings = load_settings()

    provider = st.selectbox(
        "AI Provider",
        ["groq", "openai"],
        index=0 if settings.get("provider", "groq") == "groq" else 1
    )

    mode = st.radio(
        "Analysis Mode",
        ["multi", "single"],
        index=0 if settings.get("multi_agent", True) else 1,
        format_func=lambda x: "🧠 Multi-Agent (more accurate)" if x == "multi" else "⚡ Single Agent (faster)"
    )

    output_format = st.selectbox(
        "Output Format",
        ["both", "docx", "pdf"],
        index=0
    )

    sanitize_pii = st.checkbox("🔒 Enable PII sanitization", value=True)

    context = st.text_area(
        "Additional context (optional)",
        placeholder="e.g. we are the customer, vendor is Microsoft"
    )

# ── Main ──
uploaded_file = st.file_uploader(
    "Upload contract (PDF or DOCX)",
    type=["pdf", "docx"]
)

if uploaded_file:
    if st.button("▶ Analyse Contract", type="primary"):

        # Override settings
        settings["provider"] = provider
        settings["multi_agent"] = (mode == "multi")
        settings["output_format"] = output_format

        with st.spinner(f"Analysing with {provider.upper()} in {'multi-agent' if mode == 'multi' else 'single agent'} mode..."):

            # Save to temp file
            suffix = ".pdf" if uploaded_file.name.endswith(".pdf") else ".docx"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            # Extract text
            text = extract_text(tmp_path)
            os.unlink(tmp_path)

            # PII sanitization
            pii_mapping = {}
            if sanitize_pii:
                try:
                    from reviewer.sanitizer import sanitize, desanitize
                    text, pii_mapping = sanitize(text)
                    st.info(f"🔒 PII sanitized: {len(pii_mapping)} entities redacted")
                except Exception as e:
                    st.warning(f"PII sanitization skipped: {e}")

            # Analyze
            analysis, provider_used = analyze_contract(text, context)

            # Restore PII
            if pii_mapping:
                from reviewer.sanitizer import desanitize
                analysis = desanitize(analysis, pii_mapping)

            # Build PII summary
            pii_summary = {"total_entities": len(pii_mapping), "breakdown": {}}
            for placeholder in pii_mapping.keys():
                entity_type = placeholder.split("_")[0].replace("[", "")
                pii_summary["breakdown"][entity_type] = pii_summary["breakdown"].get(entity_type, 0) + 1

        # ── Results ──
        overall = "UNKNOWN"
        for line in analysis.split("\n"):
            if "OVERALL RISK" in line:
                if "RED" in line: overall = "RED"
                elif "YELLOW" in line: overall = "YELLOW"
                elif "GREEN" in line: overall = "GREEN"
                break

        color_map = {"RED": "🔴", "YELLOW": "🟡", "GREEN": "🟢"}
        st.subheader(f"{color_map.get(overall, '⚪')} Overall Risk: {overall}")

        # Show analysis in expandable sections
        sections = {}
        current_section = "Summary"
        current_content = []

        for line in analysis.split("\n"):
            if line.startswith("## "):
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = line.replace("## ", "")
                current_content = []
            else:
                current_content.append(line)
        if current_content:
            sections[current_section] = "\n".join(current_content)

        for section_name, content in sections.items():
            with st.expander(section_name, expanded=("RISK" in section_name or "FINDINGS" in section_name)):
                for line in content.split("\n"):
                    if not line.strip():
                        continue
                    if "🔴" in line:
                        st.error(line.replace("- ", ""))
                    elif "🟡" in line:
                        st.warning(line.replace("- ", ""))
                    elif "🟢" in line:
                        st.success(line.replace("- ", ""))
                    elif "⚪" in line:
                        st.info(line.replace("- ", ""))
                    else:
                        st.write(line)

        # ── Download ──
        st.subheader("📥 Download Report")
        output_dir = tempfile.mkdtemp()
        paths = generate_report(
            contract_name=uploaded_file.name,
            analysis=analysis,
            provider=provider_used,
            output_dir=output_dir,
            output_format=output_format,
            pii_summary=pii_summary
        )

        col1, col2 = st.columns(2)
        if "docx" in paths:
            with col1:
                with open(paths["docx"], "rb") as f:
                    st.download_button(
                        "📝 Download Word",
                        f,
                        file_name=f"report_{uploaded_file.name}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
        if "pdf" in paths:
            with col2:
                with open(paths["pdf"], "rb") as f:
                    st.download_button(
                        "📄 Download PDF",
                        f,
                        file_name=f"report_{uploaded_file.name}.pdf",
                        mime="application/pdf"
                    )

else:
    st.info("👆 Upload a contract to begin analysis.")
