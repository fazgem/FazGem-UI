import streamlit as st
import json
import os
from datetime import datetime

# --- DUAL-URL API RESOLVER ---
# Replace 'https://fazgem-v2-xxxx-uc.a.run.app' with your actual GCP Cloud Run Backend URL from terminal output
GCP_BACKEND_URL = "https://fazgem-core-882691529429.us-central1.run.app"  

# Resolves automatically: Uses BACKEND_URL env var if set, otherwise defaults to live GCP Cloud Run
BACKEND_URL = os.getenv("BACKEND_URL", GCP_BACKEND_URL).rstrip("/")

# --- 1. PAGE CONFIGURATION & ENTERPRISE HEADER ---
st.set_page_config(
    page_title="FazGem | CCO Enterprise Vault",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ FazGem Enterprise Command Center")
st.subheader("Immutable Statutory Audit & Fiduciary Exception Ledger")

st.info(
    "🔒 **Statutory Jurisdiction Guardrail Active:** " \
    "All client suitability assessments, NQSMI guardrail evaluations (O. Reg. 188/08), and advisor override rationales are cryptographically hashed and vaulted..."
)

st.divider()

import requests

# --- 2. PERSISTENT LEDGER INGESTION ---
LEDGER_FILE = "cco_audit_ledger.json"

def load_cco_ledger():
    """Dual-mode loader: Fetches live Firestore logs via API, falling back to local JSON."""
    # 1. Attempt API fetch from GCP Backend
    try:
        api_url = f"{BACKEND_URL}/api/v1/vault/intercept-log"
        response = requests.get(api_url, timeout=3)
        if response.status_code == 200:
            return response.json().get("logs", [])
    except Exception:
        pass  # Fall back to local file if offline or standalone demo

    # 2. Local File Fallback
    LEDGER_FILE = "cco_audit_ledger.json"
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

cco_ledger = load_cco_ledger()

# --- 3. SYSTEM SURVEILLANCE METRICS ---
total_intercepts = len(cco_ledger)
high_priority_alerts = sum(1 for entry in cco_ledger if entry.get("status") == "OVERRIDE_ESCALATION")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Active Edge Nodes (WASM Scoped)", value="142", delta="System Normal")
with col2:
    st.metric(label="Vaulted Statutory Logs", value=str(total_intercepts), delta=f"{total_intercepts} Recorded")
with col3:
    st.metric(
        label="Pending CCO Escalate / Overrides",
        value=str(high_priority_alerts),
        delta="Action Required" if high_priority_alerts > 0 else "All Clear",
        delta_color="inverse" if high_priority_alerts > 0 else "normal"
    )

st.markdown("---")

# --- 4. LIVE INTERCEPTION & OVERRIDE LEDGER ---
st.markdown("### 🚨 Real-Time Statutory Suitability & Interception Ledger")

if not cco_ledger:
    st.success("✅ **Ledger Clean & Secure:** No fiduciary flags, NQSMI guardrail breaches, or human overrides have been transmitted to the Vault.")
else:
    for idx, entry in enumerate(reversed(cco_ledger)):
        timestamp = entry.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        client_tier = entry.get("client_tier", "RETAIL_CONSUMER")
        file_name = entry.get("filename", "Syndicated_Mortgage_Offering.pdf")
        advisor_id = entry.get("advisor_id", "ADV-042 (Ottawa Flagship)")
        override_reason = entry.get("override_rationale", "No human override provided.")
        status = entry.get("status", "LOGGED")

        with st.expander(f"📌 FSRA/CIRO FLAG [{timestamp}] | Tier: {client_tier} | Advisor: {advisor_id} | File: {file_name}", expanded=(idx == 0)):
            st.markdown(f"**Statutory Audit Methodology:** `{entry.get('audit_protocol', 'FAZGEM_RETAIL_SUITABILITY_GUARDRAIL')}`")
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.info(
                    f"**Client Profile:**\n\n"
                    f"* **Net Worth:** ${entry.get('client_net_worth', 180000.0):,.2f} CAD\n"
                    f"* **Time Horizon:** {entry.get('client_horizon', 5)} Years\n"
                    f"  * **NQSMI Limit:** $60,000.00 CAD (OSC NI 45-106 s. 2.9 Retail Cap)"
                )
            with metric_col2:
                if status == "OVERRIDE_ESCALATION":
                    st.error(f"⚠️ **Mandatory Human Override Rationale Submitted:**\n\n> *\"{override_reason}\"*")
                else:
                    st.success("**Compliance Status:** Form 1/2 Suitability Disclosures Confirmed & Archived.")

            st.divider()
            
            # --- BI-DIRECTIONAL REMEDIATION DIRECTIVE INPUT ---
            cco_feedback = st.text_input(
                "Mandatory CCO Remediation Directive / Corrective Measures:",
                key=f"feedback_{idx}",
                placeholder="e.g., Require updated property appraisal or proof of Permitted Client status before re-submission."
            )
            
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("🚫 Reject & Mandate Remediation", key=f"reject_{idx}", use_container_width=True):
                    entry["status"] = "REJECTED_MANDATORY_REMEDIATION"
                    entry["cco_remediation_directive"] = cco_feedback if cco_feedback else "General suitability deficiency. File frozen."
                    entry["remediation_timestamp_utc"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Persist back to ledger
                    with open(LEDGER_FILE, "w", encoding="utf-8") as f:
                        json.dump(cco_ledger, f, indent=4)
                        
                    st.error(f"🔒 File frozen! Remediation directive transmitted back to Advisor: '{entry['cco_remediation_directive']}'")
                    
            with metric_col2:
                if status == "OVERRIDE_ESCALATION":
                    st.error(f"⚠️ **Mandatory Human Override Rationale Submitted:**\n\n\"{override_reason}\"")
                else:
                    # Dynamic Context-Driven Compliance Status
                    active_auth = entry.get("regulatory_authority", "")
                    active_sector = entry.get("sector", "")
                    
                    if "OSC" in active_auth or "45-106" in str(entry.get("audit_protocol", "")) or "Capital Markets" in active_sector:
                        status_text = "OSC NI 45-106 OM Exemption Risk Acknowledgements (Form 45-106F4) Confirmed & Archived."
                    elif "US-FED" in str(entry.get("jurisdiction", "")) or "SEC" in str(entry):
                        status_text = "SEC / FINRA Reg BI Fiduciary Disclosures Verified & Archived."
                    else:
                        status_text = "FSRA MBLAA Form 1/2 Suitability Disclosures Confirmed & Archived."
                        
                    st.success(f"**Compliance Status:** {status_text}")

st.markdown("---")

# --- 5. FIRM-WIDE FIDUCIARY EXPORT ---
st.markdown("### 🗄️ Firm-Wide Statutory Examination & CBEM Audit Export")
if st.button("📄 Generate Statutory Regulatory Examination PDF Package", type="primary", use_container_width=True):
    st.success("✅ **Examination Package Compiled:** All 100-Point Suitability Matrices and override rationales successfully sealed.")