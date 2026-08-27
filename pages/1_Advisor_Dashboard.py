"""
ADVISOR DASHBOARD (1_Advisor_Dashboard.py)
Front-line interface for advisors to review their specific transaction audits.
"""
import os
import json
import streamlit as st
from api_client import FazGemAPI

# ---------------------------------------------------------
# 1. PAGE CONFIG & TENANT SECURITY CHECK
# ---------------------------------------------------------
st.set_page_config(page_title="Advisor Dashboard | FazGem", page_icon="📈", layout="wide")

if "tenant_id" not in st.session_state:
    st.warning("⚠️ Access Denied: Missing Tenant Identity. Please route through the Gateway (app.py).")
    st.stop()

tenant_id = st.session_state["tenant_id"]
user_email = st.session_state.get("user_email", "Advisor")
role = st.session_state.get("role", "UNKNOWN")

st.title("📈 Advisor Operations Dashboard")
st.markdown(f"**Welcome back, {user_email}** | **Firm:** `{tenant_id}`")
st.markdown("Review your recent Fiduciary Audits and active Sentinel Guardrails.")
st.divider()

# ---------------------------------------------------------
# 2. ADVISOR METRICS & RECENT AUDITS
# ---------------------------------------------------------
st.markdown("### 📊 My Recent Transaction Audits")

if st.button("🔄 Refresh My Audits", type="secondary"):
    with st.spinner("Securely fetching your audit history..."):
            # --- READ FROM SHARED JSON LEDGER ---
            ledger_path = "data/active_audits.json"
            ledger_data = []
            
            if os.path.exists(ledger_path):
                try:
                    with open(ledger_path, "r", encoding="utf-8") as f:
                        ledger_data = json.load(f)
                    ledger_data.reverse() # Newest first
                except json.JSONDecodeError:
                    st.error("Ledger file is corrupted or empty.")
            # --- END SHARED LEDGER READ ---
            st.success("Audit history synchronized.")
            
            # High-level Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Transactions Evaluated", len(ledger_data))
            
            passes = sum(1 for r in ledger_data if r.get("verdict_status") == "PASS")
            col2.metric("Compliant (PASS)", passes)
            
            intercepts = len(ledger_data) - passes
            col3.metric("Action Required", intercepts, delta_color="inverse")
            
            st.divider()
            
           # Render the individual audits
            for idx, record in enumerate(ledger_data):
                verdict = record.get("verdict_status", "UNKNOWN")
                status_icon = "✅" if verdict == "PASS" else "⚠️"
                doc_id = record.get("doc_id", "UNKNOWN_ID")

                # Force expander open if action is required
                is_open = (verdict != "PASS" and verdict != "APPROVED_BY_CCO")
                
                with st.expander(f"{status_icon} Document Audit: {doc_id} | Status: {verdict}", expanded=is_open):
                         
                    # 1. Pull Rose's Qualitative Data
                    st.markdown(f"**Qualitative Summary:** {record.get('document_summary', 'No summary available.')}")
                    
                    col_a, col_b = st.columns(2)
                    metrics = record.get("financial_metrics", {})
                    with col_a:
                        st.markdown(f"**Net Worth:** ${metrics.get('net_worth', 0):,.2f}")
                    with col_b:
                        st.markdown(f"**Proposed Amount:** ${metrics.get('proposed_amount', 0):,.2f}")

                   # 2. Execution Routing & Overrides
                    if verdict == "PASS":
                        # The UI just blindly prints the exact regulatory text the AI Engine provided
                        st.success(f"✅ {record.get('action_directive', 'Compliance check passed.')}")
                    else:
                        st.error("**🛑 Compliance Intercept Triggered. Trade Execution Blocked.**")
                        
                        intercepts = record.get("intercept_details", [])
                        for flag in intercepts:
                            if isinstance(flag, dict):
                                st.write(f"- ⚠️ **{flag.get('rule', 'ALERT')}**: {flag.get('reason', '')}")
                            else:
                                st.write(f"- ⚠️ {flag}")


                    st.divider()
                    st.markdown("### ⚖️ Execution Routing")
                
                    # Wrap the entire action block in a form to prevent premature UI closing
                    with st.form(key=f"routing_form_{doc_id}"):
                        action = st.radio(
                            "How do you wish to proceed with Rose's Statutory Assessment?",
                            options=[
                                "Select Action...", 
                                "I agree. Proceed with recommendation & archive trade.", 
                                "I disagree. Request CCO Override (Triggers Dual-Ledger Review)."
                            ]
                        )
                        
                        rationale = st.text_area(
                            "Advisor Notes / Remediation Plan (For CCO Ledger):", 
                            placeholder="Enter your remediation timeline or override justification here..."
                        )
                        
                        submit_action = st.form_submit_button("Submit Execution Directive", type="primary")
                        
                        if submit_action:
                            if action == "Select Action...":
                                st.error("⚠️ Please select an action before submitting.")
                                
                            elif action == "I agree. Proceed with recommendation & archive trade.":
                                if rationale.strip() == "":
                                    st.warning("⚠️ Please provide a brief note on how you will remediate this before archiving.")
                                else:
                                    import json, os
                                    ledger_path = "data/active_audits.json"
                                    if os.path.exists(ledger_path):
                                        with open(ledger_path, "r", encoding="utf-8") as f:
                                            current_ledger = json.load(f)
                                        for item in current_ledger:
                                            if item.get("doc_id") == doc_id:
                                                item["verdict_status"] = "REMEDIATION_PENDING"
                                                item["override_rationale"] = rationale.strip()
                                                item["action_directive"] = "Advisor agreed with AI. Remediation timeline submitted."
                                                break
                                        with open(ledger_path, "w", encoding="utf-8") as f:
                                            json.dump(current_ledger, f, indent=4)
                                    st.success("✅ Remediation plan archived and diarized for CCO follow-up.")
                                    st.rerun()

                            elif action == "I disagree. Request CCO Override (Triggers Dual-Ledger Review).":
                                if rationale.strip() == "":
                                    st.error("⚠️ You must provide a regulatory rationale before submitting an override.")
                                else:
                                    import json, os
                                    ledger_path = "data/active_audits.json"
                                    if os.path.exists(ledger_path):
                                        with open(ledger_path, "r", encoding="utf-8") as f:
                                            current_ledger = json.load(f)
                                        for item in current_ledger:
                                            if item.get("doc_id") == doc_id:
                                                item["verdict_status"] = "OVERRIDE_ESCALATED"
                                                item["override_rationale"] = rationale.strip()
                                                item["action_directive"] = "Trade frozen. Escalated to Chief Compliance Officer."
                                                break
                                        with open(ledger_path, "w", encoding="utf-8") as f:
                                            json.dump(current_ledger, f, indent=4)
                                    st.success("🚀 Override transmitted to the CCO Vault. Audit ledger updated.")
                                    st.rerun() # Instantly refresh the UI to reflect the new locked state
                        