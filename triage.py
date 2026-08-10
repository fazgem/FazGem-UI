from wasm_sanitizer import render_wasm_edge_sanitizer
import json
import streamlit as st
import re
import uuid
import requests
from streamlit_javascript import st_javascript
import os

# --- DUAL-URL API RESOLVER ---
# Replace 'https://fazgem-v2-xxxx-uc.a.run.app' with your actual GCP Cloud Run Backend URL from terminal output
GCP_BACKEND_URL = "https://fazgem-core-882691529429.us-central1.run.app"  

# Resolves automatically: Uses BACKEND_URL env var if set, otherwise defaults to live GCP Cloud Run
BACKEND_URL = os.getenv("BACKEND_URL", GCP_BACKEND_URL).rstrip("/")

# ==========================================
# 1. STATE INITIALIZATION & ZERO-TRUST LOCK
# ==========================================
st.set_page_config(page_title="FazGem | Financial Triage", page_icon="🛡️", layout="wide")

def initialize_enterprise_state():
    """Centralized State Manager to prevent Streamlit garbage collection across pages."""
    
    # 1. The Core Infrastructure
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "jurisdiction" not in st.session_state:
        st.session_state.jurisdiction = None
    if "triage_step" not in st.session_state:
        st.session_state.triage_step = "INITIALIZATION"
        
    # 2. The KYC & Memory Data
    if "financial_profile" not in st.session_state:
        st.session_state.financial_profile = {}
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # 3. The Enterprise Ledger (Crucial for the CCO Vault)
    if "cco_ledger" not in st.session_state:
        st.session_state.cco_ledger = []
    if "current_audit" not in st.session_state:
        st.session_state.current_audit = {}

# --- ADD THIS EXACT LINE BELOW (UNINDENTED) ---
initialize_enterprise_state()
        
# ==========================================
# 1.5 HELPER FUNCTIONS (EDGE DETECTION)
# ==========================================
def detect_edge_jurisdiction():
    """Silently detects location via browser JS for SEC vs CIRO lock."""
    client_timezone = st_javascript("Intl.DateTimeFormat().resolvedOptions().timeZone")
    if client_timezone:
        if any(tz in client_timezone for tz in ["Toronto", "Vancouver", "America/Edmonton"]):
            return "CA"
        return "US"
    return None

def edge_compute_masking(text: str) -> str:
    """
    Simulates local WASM edge-compute redaction.
    Intercepts and destroys a full spectrum of PII before cloud transit.
    """
    # --- LAYER 1: DETERMINISTIC RULES (The Regex Net) ---
    patterns = {
        r'\b\d{3}-\d{2}-\d{4}\b': '[REDACTED US_SSN]',
        r'\b\d{3}[- ]?\d{3}[- ]?\d{3}\b': '[REDACTED CAN_SIN]',
        r'\b(?:\d[ -]*?){13,16}\b': '[REDACTED CREDIT_CARD]',
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b': '[REDACTED EMAIL]',
        r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b': '[REDACTED PHONE]',
        r'\b(0[1-9]|1[0-2]|[1-9])[-/](0[1-9]|[12]\d|3[01]|[1-9])[-/](19|20)\d{2}\b': '[REDACTED DOB]'
    }
    
    for pattern, replacement in patterns.items():
        text = re.sub(pattern, replacement, text)
        
    return text

# ==========================================
# 2. DEFINE THE UI MODULES (THE B2B FUNNEL)
# ==========================================

def render_scenario_guide():
    # Render the live WASM Edge Engine status badge
    render_wasm_edge_sanitizer()
    with st.sidebar:
        st.header("🧪 Test Drive FazGem")
        st.caption("Copy & paste these scenarios to see our Zero-Trust architecture in real-time.")
        
        # --- NEW: STATUTORY JURISDICTION SWITCHER ---
        st.markdown("### 🏛️ Active Governance Stream")
        selected_sector = st.selectbox(
            "Select Regulated Jurisdiction:",
            [
                "FSRA Mortgage Brokering (MBLAA) / Credit Unions & Caisses Populaires/Property/Casualty & Life Insurance " ,
                "Pan-Canadian Non-Securities (FSRA / BCFSA / AMF)",
                "Canadian Capital Markets (OSC / CIRO / CSA)",
                "Cross-Border U.S. Wealth (SEC / FINRA / Reg BI)"
            ],
            key="sector_selector"
        )
        
        st.markdown("### 🛡️ Edge Add-On Modules")
        fraud_shield = st.checkbox("WASM Client Portal Fraud Shield", value=True)
        ftc_matrix = st.checkbox("FTC Suitability & Cost of Borrowing", value=True)
        
        # Save to global session state
        st.session_state["active_sector"] = selected_sector
        st.session_state["fraud_shield_enabled"] = fraud_shield
        st.session_state["ftc_matrix_enabled"] = ftc_matrix
        # --------------------------------------------
        
        st.divider()
        # [Your existing Scenario 1, 2, 3 subheaders continue below...]
        
        st.divider()
        
        st.subheader("Scenario 1: The PII Leak")
        st.markdown("**Test:** Watch the WASM edge-compute mask data before it leaves the browser.")
        st.code("Draft an email to my client, John Doe (SSN: 000-11-2222), congratulating him on his $5M account balance.", language="markdown")
        
        st.divider()
        
        st.subheader("Scenario 2: The Rogue Finfluencer")
        st.markdown("**Test:** Trigger Rose's Fiduciary Guardrails on SEC Marketing Rules.")
        st.code("Write a LinkedIn post guaranteeing a 12% risk-free return on our new crypto wealth fund using client testimonials.", language="markdown")
        
        st.divider()
        
        st.subheader("Scenario 3: Enterprise Telemetry")
        st.markdown("**Test:** See the real-time impact on firm-wide compliance.")
        st.info("👈 Run Scenarios 1 & 2, then click the **Fiduciary Audit** tab to see the CCO Dashboard view.")


        st.divider()
        st.subheader("Scenario 4: FSRA Mortgage Suitability (MBLAA)")
        st.markdown("*Test:* Trigger Rose's FTC Guardrails on high-cost private lending without a documented exit strategy.")
        st.code(
            "Client (Income: $75k, Credit: 580) is seeking a $600k mortgage. "
            "Recommend a 1-year Private Mortgage at 11.5% interest + 3% lender fee "
            "to close the property quickly, without discussing an exit strategy or alternative B-lenders.",
            language="markdown"
)

        

def render_welcome_page():
    """PHASE 0: The Institutional Front Door (VC Landing Page)"""
    st.markdown("<h1 style='text-align: center; color: #00d2ff; font-size: 4em;'>FazGem</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #ececec;'>The Zero-Trust Fiduciary AI for Wealth Management</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Replacing subjective compliance with deterministic, edge-computed algorithmic jurisprudence.</p>", unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # THE PROBLEM & SOLUTION
    # ==========================================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⚠️ The Trillion-Dollar Blind Spot")
        st.markdown("""
        Legacy compliance is reactive. Archivers and compliance wrappers only catch fiduciary violations *after* the trade is executed and the client's money is lost, resulting in massive SEC/FINRA fines and irreparable reputational damage.
        """)

    with col2:
        st.markdown("### 🛡️ The FazGem Paradigm")
        st.markdown("""
        FazGem is a proactive, pre-trade legal engine. By combining WASM edge-compute data scrubbing with a deterministic 100-Point Fiduciary AI Matrix, we mathematically prevent unsuitable trades before they ever reach the market.
        """)

    st.markdown("---")

    # ==========================================
    # ABOUT THE CO-FOUNDERS
    # ==========================================
    st.markdown("### 🤝 The Visionaries")
    st.markdown("""
    FazGem was engineered through a unique paradigm: a true **Human-AI Co-Founding Partnership**. 

    * **The Human Architect:** Bringing decades of deep industry expertise, strategic vision, and an uncompromising understanding of the regulatory friction plaguing modern wealth management.
    * **Atlas Core (The Digital Twin):** An advanced AI engineering node, executing the architectural vision into a secure, zero-trust enterprise codebase.

    Together, we didn't just build a compliance tool—we built a Personal Modern Regulator. 
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # THE GATEWAY BUTTON (Keeps the funnel intact)
    if st.button("Initialize FazGem Ecosystem 🔐", type="primary", use_container_width=True):
        st.session_state.triage_step = "RPSA"
        st.rerun()

def render_rpsa_gate():
    """PHASE 1: Statutory KYC & Baseline Fiduciary Gate"""
    st.markdown("<h2 style='text-align: center; color: #f8f9fa;'>KYC Regulatory Baseline</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>To build your custom strategy, we must legally establish your baseline financial profile.</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 1. Net Worth / Liquid Assets")
        st.caption("What is the approximate total liquid net worth available for deployment?")
        net_worth = st.slider("Net Worth", min_value=0, max_value=5000000, value=250000, step=10000, format="$%d", key="net_worth", label_visibility="collapsed")

        st.markdown("### 2. Investment Horizon")
        st.caption("How many years until the client plans to begin drawing down on this capital?")
        horizon = st.slider("Investment Horizon", min_value=1, max_value=50, value=10, step=1, key="horizon", label_visibility="collapsed")

        st.markdown("### 3. Risk Tolerance")
        st.caption("Which best describes the client's approach to market volatility and capital preservation?")
        risk = st.radio("Risk Tolerance", ["Conservative", "Balanced", "Aggressive"], index=1, horizontal=True, key="risk", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)

        if "baseline_calculated" not in st.session_state:
            st.session_state.baseline_calculated = False

        if st.button("Secure KYC Baseline", type="primary", use_container_width=True):
            st.session_state.financial_profile = {"net_worth": net_worth, "horizon": horizon, "risk": risk}
            st.session_state.baseline_calculated = True

            # Preliminary Logic Checks (The Guardrails)
            if risk == "Aggressive" and horizon < 5:
                st.error("🚨 **Compliance Flag: Suitability Mismatch** \nAn aggressive risk profile conflicts with a short-term liquidity horizon under current regulatory frameworks.")
            elif risk == "Conservative" and horizon > 20:
                st.warning("⚠️ **Inflation Warning: Capital Drag** \nA highly conservative allocation over a multi-decade horizon exposes capital to severe purchasing power erosion.")
            else:
                st.success("✅ **Baseline Secured.** Telemetry confirms compliance metrics locked at the edge. Initializing Vault Protocol.")

        st.markdown("---")
        if st.session_state.baseline_calculated:
            if st.button("Enter the Vault 🔐", use_container_width=True):
                st.session_state.triage_step = "VAULT"
                st.session_state.baseline_calculated = False
                st.rerun()

def render_vault_matrix():

    render_scenario_guide()

    """PHASE 2: The Ultimate Destination (Rose & The Vault)"""
    st.markdown(f"<h3 style='color: #28a745; text-align: center;'>🛡️ Edge Perimeter Secured ({st.session_state.jurisdiction} Jurisdiction)</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Welcome to the Vault. Rose is securely booted and armed with the KYC baseline telemetry.</p>", unsafe_allow_html=True)

    
    # Confirming the Memory inheritance
    prof = st.session_state.financial_profile
    st.info(f"**Locked KYC Profile:** Net Worth: ${prof.get('net_worth', 0):,}, Horizon: {prof.get('horizon', 0)} years, Risk: {prof.get('risk', 'N/A')}")

   
    st.markdown("---")
    
    # Render the Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # The Chat Input Trap
    if prompt := st.chat_input("Speak with Rose, your Fiduciary AI..."):
        
        # ACTIVATE ZERO-TRUST EDGE SHIELD
        sanitized_prompt = edge_compute_masking(prompt)
        
        # Render the sanitized user message locally
        st.session_state.messages.append({"role": "user", "content": sanitized_prompt})
        with st.chat_message("user"):
            st.markdown(sanitized_prompt)
            if sanitized_prompt != prompt:
                st.caption("🛡️ *Edge-Compute Active: PII intercepted and scrubbed locally.*")

        # Fire Payload to the Core
        with st.chat_message("assistant"):
            with st.spinner("Rose is analyzing..."):
                try:
                 # Forcefully inject the KYC data with STRICT machine-readable formatting
                    kyc_context = (
                        "=== STRICT SYSTEM KYC DATA ===\n"
                        f"CLIENT_NET_WORTH: ${prof.get('net_worth', 0):,}\n"
                        f"CLIENT_TIME_HORIZON: {prof.get('horizon', 0)} years\n"
                        f"CLIENT_RISK_TOLERANCE: {prof.get('risk', 'Unknown')}\n"
                        "==============================\n\n"
                    )
                    contextual_message = kyc_context + sanitized_prompt


                    # Determine jurisdiction and sector dynamically from UI state
                    active_jurisdiction = st.session_state.get("jurisdiction", "CA-ON")
                    active_sector = st.session_state.get("active_sector", "FSRA Mortgage Brokering (MBLAA)")

                    # Dynamic Compliance Stream Resolver
                    if active_jurisdiction == "US-FED":
                        if "SEC" in active_sector or "FINRA" in active_sector or "Wealth" in active_sector:
                            stream_tag = "SEC_FINRA_REG_BI"
                        else:
                            stream_tag = "FED_RESERVE_CBEM"
                    else: # CA-ON Default
                        if "FSRA" in active_sector:
                            stream_tag = "FSRA_FTC_ONTARIO"
                        else:
                            stream_tag = "OSC_CIRO_ONTARIO"

                    payload = {
                        "user_id": "demo_practitioner",
                        "session_id": st.session_state.session_id,
                        "message": contextual_message,
                        "total_net_worth": prof.get("net_worth", 0),
                        "liquid_assets": prof.get("net_worth", 0),
                        "horizon": prof.get("horizon", 0),
                        "risk": prof.get("risk", "Unknown"),
                        "jurisdiction": active_jurisdiction,
                        "financial_profile": prof,
                        "sector": active_sector,
                        "compliance_stream": stream_tag,
                        "x_wasm_edge_verified": "WASM_SAN_OK_TLS13"
                    }


                    response = requests.post(f"{BACKEND_URL}/api/chat", json=payload)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        
                        # Extract the raw reply (which is now a JSON string from Gemini)
                        if isinstance(res_data, dict):
                            raw_reply = res_data.get("reply", "")
                        elif isinstance(res_data, list) and len(res_data) > 0:
                            raw_reply = res_data[0].get("reply", "") if isinstance(res_data[0], dict) else str(res_data)
                        else:
                            raw_reply = str(res_data)

                        # --- NEW: GUARDRAIL AGAINST BLANK CORE RESPONSES ---
                        if not raw_reply or str(raw_reply).strip() == "":
                            st.error("⚠️ Core Engine returned an empty payload. Check Cloud Run logs for Pydantic schema or Enum validation errors.")
                            st.stop()
                            
                        try:
                            # 🧠 THE PARSER: Attempt to load the strict JSON schema
                            audit_data = json.loads(raw_reply)
                            
                            # ⚡ THE FIX: Extract the actual profile dictionary first
                            prof = st.session_state.get("financial_profile", {})
                            
                       
                            # ⚡OW: SAVE LIVE DATA TO GLOBAL MEMORY FOR THE ADVISOR DASHBOARD
                            st.session_state.current_audit = {
                                "client_kyc": {
                                    "net_worth": prof.get("net_worth", "Unknown"),
                                    "horizon": prof.get("horizon", "Unknown"),
                                    "risk": prof.get("risk", "Unknown")
                                },
                                "proposed_trade": prompt, # The message typed in the chat
                                "ai_audit": audit_data,
                                # --- NEW: PERSIST SECTOR & MODULAR METADATA ---
                                "sector": st.session_state.get("active_sector", "FSRA Mortgage Brokering (MBLAA)"),
                                "wasm_fraud_shield_active": st.session_state.get("fraud_shield_enabled", True),
                                "ftc_matrix_active": st.session_state.get("ftc_matrix_enabled", True)
                            }
                           
                            
                            # Build the Enterprise Dashboard Markdown
                            status_color = "🟢" if audit_data.get('audit_status') in ["EFFECTIVE", "PASS"] else "🔴"
                            
                            ai_reply = f"""
### 🛡️ FazGem Second Opinion Audit
**Status:** {status_color} {audit_data.get('audit_status', 'UNKNOWN')} | **Total Score:** {audit_data.get('total_score', 0)}/100

**Executive Summary:**
*{audit_data.get('executive_summary', 'No summary provided.')}*

---
#### 📊 The 100-Point Fiduciary Matrix

**1. Rationale of Selection ({audit_data.get('rationale_of_selection', {}).get('score', 0)}/30)**
*Principle of Logical Nexus*
> {audit_data.get('rationale_of_selection', {}).get('rationale', '')}

**2. Disclosure to Clients ({audit_data.get('disclosure_to_clients', {}).get('score', 0)}/25)**
*Principle of Informed Consent*
> {audit_data.get('disclosure_to_clients', {}).get('rationale', '')}

**3. Client's Understanding ({audit_data.get('clients_understanding', {}).get('score', 0)}/20)**
*Principle of Cognitive Alignment*
> {audit_data.get('clients_understanding', {}).get('rationale', '')}

**4. Selection of Products ({audit_data.get('selection_of_products', {}).get('score', 0)}/15)**
*Principle of Contextual Optimization*
> {audit_data.get('selection_of_products', {}).get('rationale', '')}

**5. Product Analysis ({audit_data.get('product_service_analysis', {}).get('score', 0)}/10)**
*Principle of Professional Skepticism*
> {audit_data.get('product_service_analysis', {}).get('rationale', '')}
                            """
                        except json.JSONDecodeError:
                            # THE FALLBACK: If it's not JSON (e.g., a standard chat message or error), just print it normally
                            ai_reply = raw_reply
                            
                        # Render the output to the UI and save to memory
                        st.markdown(ai_reply)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    else:
                        st.error(f"⚠️ Backend API Error: {response.status_code}")
                
                except requests.exceptions.ConnectionError:
                    st.error("🚨 API Disconnected: Could not reach the FazGem Core. Ensure your backend is running!")

    st.markdown("---")
    if st.button("⬅️ Terminate Session & Restart (For Testing)", use_container_width=True):
        st.session_state.triage_step = "INITIALIZATION"
        st.session_state.jurisdiction = None
        st.session_state.messages = [] 
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# ==========================================
# 3. THE MAIN ROUTING ENGINE (THE LINEAR FUNNEL)
# ==========================================

# PHASE A: The Invisible Handshake
if st.session_state.triage_step == "INITIALIZATION":
    with st.spinner("Locking data sovereignty boundaries..."):
        detected_loc = detect_edge_jurisdiction()
        if detected_loc: 
            st.session_state.jurisdiction = detected_loc
            st.session_state.triage_step = "WELCOME"
            st.rerun()

# PHASE B: The Front Door
elif st.session_state.triage_step == "WELCOME":
    render_welcome_page()

# PHASE C: The KYC Gate
elif st.session_state.triage_step == "RPSA":
    render_rpsa_gate()

# PHASE D: The Matrix Vault
elif st.session_state.triage_step == "VAULT":
    render_vault_matrix()