import streamlit as st
import json
import os
import uuid
from datetime import datetime
import time

st.set_page_config(page_title="FazGem Simulator", page_icon="🧪", layout="wide")

st.title("🧪 FazGem Fiduciary Simulator")
st.markdown("Inject deterministic test scenarios into the Zero-Trust ledger for UI demonstration.")
st.divider()

def inject_audit(scenario_type):
    doc_id = f"AUDIT_{str(uuid.uuid4())[:6].upper()}"
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    if scenario_type == "PASS":
        record = {
            "doc_id": doc_id,
            "timestamp": timestamp,
            "verdict_status": "PASS",
            "financial_metrics": {"net_worth": 1250000, "proposed_amount": 0.0},
            "intercept_details": [],
            "contextual_flags": ["Routine tax document", "No active capital proposal"],
            "document_summary": "Synthetic T5 statement indicating $1,250 routine dividend income. No capital deployment proposed.",
            "client_type": "RETAIL_CONSUMER",
            "jurisdiction": "CA-ON",
            "sector": "wealth_management",
            "action_directive": "Document reviewed and logged. No active capital transaction or statutory intercepts detected."
        }
    elif scenario_type == "FAIL":
        record = {
            "doc_id": doc_id,
            "timestamp": timestamp,
            "verdict_status": "MANDATORY_CCO_MANUAL_REVIEW",
            "financial_metrics": {"net_worth": 250000, "proposed_amount": 60000},
            "intercept_details": [
                {"rule": "CONCENTRATION_GUARDRAIL", "reason": "Proposed $60,000 transaction represents 24.0% of liquid net worth (Exceeds 20% hard limit)."},
                {"rule": "SUITABILITY_FLAG", "reason": "High-risk syndicated mortgage proposed for conservative retail consumer."}
            ],
            "contextual_flags": ["High concentration risk", "Alternative asset class"],
            "document_summary": "Proposed $60,000 allocation into a high-risk private syndicated mortgage for a retail consumer with a $250,000 net worth.",
            "client_type": "RETAIL_CONSUMER",
            "jurisdiction": "CA-ON",
            "sector": "exempt_market_securities",
            "action_directive": "Compliance Intercept Triggered. Trade Execution Blocked. Mandatory CCO override required."
        }
        
    # Write to shared ledger
    ledger_path = "data/active_audits.json"
    os.makedirs("data", exist_ok=True)
    
    ledger = []
    if os.path.exists(ledger_path):
        try:
            with open(ledger_path, "r", encoding="utf-8") as f:
                ledger = json.load(f)
        except json.JSONDecodeError:
            ledger = []
            
    ledger.append(record)
    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=4)
        
    return doc_id

# --- UI CONTROLS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 Scenario A: Clean Routine Document")
    st.caption("Simulates a standard tax slip with $0 proposed capital. Should trigger a standard PASS.")
    if st.button("Inject PASS Scenario", type="secondary", use_container_width=True):
        with st.spinner("Simulating engine evaluation..."):
            time.sleep(1) # Fake delay for effect
            doc_id = inject_audit("PASS")
            st.success(f"✅ Fiduciary Audit `{doc_id}` generated! Check the Advisor Dashboard.")

with col2:
    st.subheader("🔴 Scenario B: Concentration Guardrail Breach")
    st.caption("Simulates a $60k high-risk allocation against a $250k net worth (24%). Should trigger a hard block.")
    if st.button("Inject FAIL Scenario", type="primary", use_container_width=True):
        with st.spinner("Simulating engine evaluation..."):
            time.sleep(1) # Fake delay for effect
            doc_id = inject_audit("FAIL")
            st.error(f"🛑 Sentinel Intercept `{doc_id}` generated! Check the CCO Vault.")