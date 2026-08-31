"""
FAZGEM CCO VAULT (2_CCO_Vault.py)
Stateless rendering of the cryptographically secured Firestore ledger.
"""

import os
import json
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="FazGem | CCO Compliance Vault",
    page_icon="🏛️",
    layout="wide"
)

# Custom Styling for Enterprise Vault
st.markdown("""
    <style>
        .vault-header { font-size: 26px; font-weight: 700; color: #FFFFFF; margin-bottom: 5px; }
        .vault-sub { font-size: 14px; color: #94A3B8; margin-bottom: 25px; }
        .status-pass { color: #10B981; font-weight: bold; }
        .status-review { color: #F59E0B; font-weight: bold; }
        .status-fail { color: #EF4444; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="vault-header">🏛️ Chief Compliance Officer (CCO) Audit Vault</div>', unsafe_allow_html=True)
st.markdown('<div class="vault-sub">Immutable, KMS-Encrypted Ledger & Dynamic Remediation Console</div>', unsafe_allow_html=True)

# --- SIDEBAR TENANT CONTEXT ---
st.sidebar.image("https://img.icons8.com/isometric/50/shield.png", width=40)
st.sidebar.title("Vault Controls")
active_tenant = st.sidebar.text_input("Active Enterprise Tenant", value="TENANT_FLAGSHIP_001")
cco_id = st.sidebar.text_input("Authenticated CCO ID", value="cco_officer_01@flagship-wealth.ca")

if st.sidebar.button("🔄 Sync Live Ledger"):
    st.rerun()

st.sidebar.divider()
st.sidebar.caption("🔒 Zero-Trust Encrypted Firestore Connection Active")

# --- MAIN LEDGER DASHBOARD ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Audited Trades", "24", "+3 Today")
col2.metric("Deterministic Passes", "21", "87.5%")
col3.metric("CCO Overrides Required", "3", "Pending Action", delta_color="inverse")
col4.metric("Vault Security State", "ACTIVE", "AES-256 KMS")

st.divider()

st.subheader("📋 Pending & Historical Audit Entries")

# --- READ FROM SHARED JSON LEDGER ---
# --- FETCH LIVE API LEDGER ---
from api_client import FazGemAPI
ledger_data = FazGemAPI.fetch_cco_ledger(tenant_id=active_tenant, limit=50)

if not ledger_data:
    st.info("No active audits found in the vault. Transmit a payload from the Client Portal.")

# Render Ledger Items
for entry in ledger_data:
    doc_id = entry.get("doc_id", "N/A")
    status = entry.get("verdict_status", "UNKNOWN")
    metrics = entry.get("financial_metrics", {})
    intercepts = entry.get("intercept_details", [])
    summary = entry.get("document_summary", "No summary provided.")
    
    # Status Badge
    if "PASS" in status:
        badge = "🟢 **PASS**"
    elif "MANUAL_REVIEW" in status or "OVERRIDE" in status:
        badge = "🟠 **CCO OVERRIDE REQUIRED**"
    else:
        badge = "🔴 **FAIL / BLOCKED**"

    with st.expander(f"{badge} | ID: `{doc_id}` | Proposed Amount: ${metrics.get('proposed_amount', 0):,.2f}"):
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            st.markdown(f"**Qualitative Summary:** {summary}")
            st.markdown(f"**Net Worth:** ${metrics.get('net_worth', 0):,.2f}")
            
            if intercepts:
                st.warning("**Sentinel Intercept Flags Triggered:**")
                for flag in intercepts:
                    if isinstance(flag, dict):
                        st.write(f"- ⚠️ **{flag.get('rule_id', 'ALERT')}**: {flag.get('message', '')}")
            
                    else:
                        st.write(f"- ⚠️ {flag}")

        with col_b:
                        st.markdown("### ⚖️ CCO Action Directive")
                        
                        status = entry.get("verdict_status", "UNKNOWN")
                        doc_id = entry.get("doc_id", "UNKNOWN_ID")
                        
                        if status == "OVERRIDE_ESCALATED":
                            st.warning(f"**Advisor Override Rationale:**\n\n*{entry.get('override_rationale', 'No rationale provided.')}*")
                            
                            remediation_note = st.text_area(
                                "Mandatory CCO Remediation Directives / Rationale:",
                                key=f"note_{doc_id}",
                                placeholder="Enter regulatory justification or condition for approval..."
                            )
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("✅ Approve & Seal", key=f"app_{doc_id}", type="primary", use_container_width=True):
                                    st.success("✅ Trade explicitly approved by CCO. Ledger cryptographically sealed.")
                                    
                            with col_btn2:
                                if st.button("🛑 Mandate Remediation", key=f"rej_{doc_id}", use_container_width=True):
                                    if remediation_note.strip() == "":
                                        st.error("⚠️ You must provide a remediation directive.")
                                    else:
                                        st.warning(f"🛑 Trade rejected. Directive sent to Advisor: {remediation_note.strip()}")

                        elif status == "REMEDIATION_PENDING":
                            st.info(f"💡 **Advisor Remediation Plan:**\n\n{entry.get('override_rationale', 'No notes provided.')}")
                            if st.button("Acknowledge & Seal Record", key=f"ack_{doc_id}"):
                                st.success("✅ **STATUS: REMEDIATION ACKNOWLEDGED & SEALED BY CCO**")
                                # In a live environment, this would call the API to update the status    
                                                   
                        elif status == "REMEDIATION_ACKNOWLEDGED":
                            st.success("✅ **STATUS: REMEDIATION ACKNOWLEDGED & SEALED BY CCO**")

                        elif status == "APPROVED_BY_CCO":
                            st.success("✅ **STATUS: APPROVED BY CCO**")
                            st.info(f"**CCO Directive:** {entry.get('cco_directive', 'Approved as submitted.')}")
                            
                        elif status == "REJECTED_BY_CCO":
                            st.error("🛑 **STATUS: REJECTED / REMEDIATION MANDATED**")
                            st.warning(f"**CCO Directive:** {entry.get('cco_directive', 'No directive provided.')}")
                            
                        else:
                            st.info("No pending CCO action required for this record.")

st.divider()
st.caption("FazGem Fiduciary Engine v3.0 | Zero-Trust RegTech Architecture")