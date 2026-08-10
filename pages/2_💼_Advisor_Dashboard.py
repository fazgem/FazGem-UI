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
    page_title="FazGem | Advisor Workspace",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ FazGem Advisor Workspace")
st.subheader("Client Recommendation & Fiduciary Audit Review")

# Check if CCO sent back a mandatory remediation directive
ledger_file = "cco_audit_ledger.json"
if os.path.exists(ledger_file):
    with open(ledger_file, "r", encoding="utf-8") as f:
        ledger_data = json.load(f)
        if ledger_data:
            latest_entry = ledger_data[-1]
            if latest_entry.get("status") == "REJECTED_MANDATORY_REMEDIATION":
                st.error(
                    f"🔒 **CCO REMEDIATION MANDATE ACTIVE:** The Chief Compliance Officer rejected the prior override submission.\n\n"
                    f"**Directive:** `{latest_entry.get('cco_remediation_directive')}`"
                )

# --- 2. LOAD LIVE AUDIT FROM CLIENT PORTAL HANDOFF ---
handoff_file = "advisor_handoff_report.json"

if os.path.exists(handoff_file):
    try:
        with open(handoff_file, "r", encoding="utf-8") as f:
            live_audit = json.load(f)
    except Exception:
        live_audit = {
            "filename": "No Active Upload",
            "client_classification": "RETAIL_CONSUMER",
            "audit_protocol": "STANDBY",
            "audit_report": "No active client document submitted through the Zero-Trust Portal.",
            "client_net_worth": 0.0,
            "client_horizon": 0
        }
else:
    live_audit = {
        "filename": "No Active Upload",
        "client_classification": "RETAIL_CONSUMER",
        "audit_protocol": "STANDBY",
        "audit_report": "No active client document submitted through the Zero-Trust Portal.",
        "client_net_worth": 0.0,
        "client_horizon": 0
    }

# --- 3. DISPLAY CLIENT PROFILE & INGESTED OFFERING ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📋 Active Client Profile")
    st.info(
        f"**Classification:** {live_audit.get('client_classification', 'N/A')}\n\n"
        f"**Net Worth:** ${live_audit.get('client_net_worth', 0.0):,.2f} CAD | "
        f"**Horizon:** {live_audit.get('client_horizon', 0)} Years\n\n"
        f"**Ingested File:** `{live_audit.get('filename', 'N/A')}`"
    )

with col2:
    st.markdown("### 🏛️ Statutory Methodology")
    st.success(f"**Active Guardrail:** `{live_audit.get('audit_protocol', 'N/A')}`")
    st.write(
        "Under O. Reg. 188/08 s. 24, all mortgage recommendations must be documented "
        "and proven suitable against the client's financial profile."
    )

st.divider()

# --- 4. DISPLAY ROSE'S SUITABILITY & RISK ASSESSMENT ---
st.markdown("### 🧠 AI Fiduciary Second Opinion (Rose Core)")
with st.container(border=True):
    st.markdown(live_audit.get("audit_report", "No report available."))

st.divider()

# --- 5. EXECUTION ROUTING & CCO OVERRIDE ---
# 1. Deterministic Statutory Intercept: Check if Rose mandated a CCO Override
audit_report_text = live_audit.get("audit_report", "")
is_cco_override_mandated = "MANDATORY CCO OVERRIDE" in audit_report_text.upper() or "HARD_STOP" in audit_report_text.upper()

st.markdown("### ⚖️ Execution Routing")

if is_cco_override_mandated:
    st.error(
        "🚨 **STATUTORY INTERCEPT ACTIVE:** Rose Core has flagged a critical suitability deficiency or "
        "cumulative NQSMI exposure limit requiring **Mandatory CCO Dual-Ledger Review** under CBEM Section 4000."
    )

action = st.radio(
    "How do you wish to proceed with Rose's Statutory Assessment?",
    options=[
        "Select Action...",
        "I agree. Proceed with recommendation & archive Form 1/2 suitability disclosures.",
        "I disagree. Request CCO Override (Triggers Dual-Ledger Review)."
    ]
)

if action == "I agree. Proceed with recommendation & archive Form 1/2 suitability disclosures.":
    if is_cco_override_mandated:
        st.error(
            "🛑 **EXECUTION BLOCKED:** You cannot bypass a mandatory CCO override directive. "
            "Please select **'I disagree. Request CCO Override'** below and submit your rationale to the Chief Compliance Officer."
        )
    else:
        st.success("✅ Trade recommendation validated. Form 1/2 suitability disclosures queued for client signature.")
       # --- UPGRADED: SERIALIZED TENANT DOSSIER ARCHIVE ---
        advisor_id = live_audit.get("advisor_id", "ADV-042")
        tenant_vault_dir = os.path.join("vaulted_cases", advisor_id)
        os.makedirs(tenant_vault_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(tenant_vault_dir, f"DOSSIER_{timestamp}.json")

        live_audit["execution_status"] = "APPROVED_BY_ADVISOR"
        live_audit["execution_timestamp_utc"] = datetime.now().isoformat()

        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(live_audit, f, indent=4)

        st.success(f"🔒 Transaction validated! Serialized to tenant archive: `{archive_path}`")

elif action == "I disagree. Request CCO Override (Triggers Dual-Ledger Review).":
    st.error("🚨 HARD STOP: Trade Execution Blocked. Mandatory CCO Review Required.")
    override_rationale = st.text_area("Mandatory Human Override Rationale (For CCO Review):")
    
    if st.button("Submit Dual-Ledger Override to CCO Vault", type="primary"):
        if not override_rationale.strip():
            st.warning("⚠️ You must provide a regulatory rationale before submitting an override.")
        else:
            ledger_file = "cco_audit_ledger.json"
            cco_ledger = []
            if os.path.exists(ledger_file):
                try:
                    with open(ledger_file, "r", encoding="utf-8") as f:
                        cco_ledger = json.load(f)
                except Exception:
                    cco_ledger = []
            
            new_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "filename": live_audit.get("filename", "Syndicated_Mortgage_Offering.pdf"),
                "client_tier": live_audit.get("client_classification", "RETAIL_CONSUMER"),
                "client_net_worth": live_audit.get("client_net_worth", 180000.0),
                "client_horizon": live_audit.get("client_horizon", 5),
                "audit_protocol": live_audit.get("audit_protocol", "FAZGEM_RETAIL_SUITABILITY_GUARDRAIL"),
                "advisor_id": "ADV-042 (Ottawa Flagship)",
                "override_rationale": override_rationale.strip(),
                "status": "OVERRIDE_ESCALATION"
            }
            cco_ledger.append(new_entry)
            with open(ledger_file, "w", encoding="utf-8") as f:
                json.dump(cco_ledger, f, indent=4)
            
            st.success("✅ Override transmitted to the CCO Vault. Audit ledger updated.")