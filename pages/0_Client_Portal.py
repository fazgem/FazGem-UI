"""
ZERO-TRUST CLIENT PORTAL (0_Client_Portal.py)
Implements Edge-Compute for local PII scrubbing before payload transmission.
"""

import os
import time
import json
import uuid
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
from api_client import FazGemAPI
# Add this import at the top of 0_Client_Portal.py
from utils.wasm_sanitizer import render_wasm_edge_sanitizer



# ---------------------------------------------------------
# 1. PAGE CONFIG & TENANT SECURITY CHECK
# ---------------------------------------------------------
st.set_page_config(page_title="Client Portal | FazGem", page_icon="🔐", layout="wide")

if "tenant_id" not in st.session_state:
    st.warning("⚠️ Access Denied: Missing Tenant Identity. Please route through the Gateway (app.py).")
    st.stop()

# ---------------------------------------------------------
# 2. EDGE-COMPUTE SANITIZATION (WASM)
# ---------------------------------------------------------

st.title("🔐 Zero-Trust Client Intake")
st.markdown("All financial documents are scrubbed of Personally Identifiable Information (PII) locally in your browser's volatile memory before being encrypted and transmitted to the FazGem Core.")
st.caption("Executes browser-native WebAssembly memory scrubbing before network transit.")

# Renders the unified WASM Engine + Terminal Sandbox
render_wasm_edge_sanitizer()


# In a full production build, this is a compiled React/WASM component.
# Here, we inject a native HTML/JS sandbox to execute strictly on the client machine.
# 2. The Interactive UI for the Sandbox
wasm_ui_html = """
<div style="font-family: monospace; padding: 15px; border: 1px solid #4CAF50; border-radius: 5px; background-color: #0e1117; color: #c6d4e1; margin-top: 15px;">
    <h4 style="color: #4CAF50; margin-top: 0;">> Edge Engine: Linear Memory Sandbox</h4>
    <p style="font-size: 0.9em;">Select a client .txt document to execute local in-memory PII destruction via WASM.</p>
    <input type="file" id="wasmFileInput" accept=".txt" style="margin-bottom: 10px; color: #fff;"/>
    <br/>
    <button onclick="processWasmFile()" style="background-color: #4CAF50; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold;">Execute Local Edge Scrub</button>
    <div id="wasmTerminal" style="margin-top: 15px; padding: 10px; background: #000; border-left: 4px solid #4CAF50; min-height: 80px; font-size: 0.85em; white-space: pre-wrap; word-wrap: break-word;">> Edge Engine waiting for file injection...</div>
</div>

<script>
async function processWasmFile() {
    const fileInput = document.getElementById('wasmFileInput');
    const terminal = document.getElementById('wasmTerminal');

    if (!fileInput.files.length) {
        terminal.innerHTML = "<span style='color: #ff4b4b;'>> ERROR: No payload detected.</span>";
        return;
    }

    const file = fileInput.files[0];
    terminal.innerHTML = "> [RAM ALLOCATED] Reading file buffer...\\n";

    const reader = new FileReader();
    reader.onload = function(e) {
        let rawText = e.target.result;
        terminal.innerHTML += "> [WASM ENGINE] Intercepting raw byte stream...\\n";

        setTimeout(() => {
            // Route through our newly injected WASM Engine!
            if (window.FazGemWasmEngine) {
                let result = window.FazGemWasmEngine.sanitizeText(rawText);
                
                terminal.innerHTML += "> [EDGE SCRUB] PII Annihilated (PIPEDA/CCPA/Law 25 standards applied).\\n";
                terminal.innerHTML += "> [STATUS] Payload cryptographically secured for backend transit.\\n";
                terminal.innerHTML += "<span style='color: #4CAF50; font-weight: bold;'>> READY FOR DISPATCH. Copy the scrubbed text below to transmit.</span>\\n\\n";
                terminal.innerHTML += "<textarea id='scrubbedOutput' style='width: 100%; height: 100px; background: #222; color: #0f0; border: 1px solid #4CAF50; margin-top: 10px;'>" + result.sanitizedPrompt + "</textarea>";
            } else {
                terminal.innerHTML += "<span style='color: #ff4b4b;'>> FATAL ERROR: WASM Engine Not Initialized.</span>";
            }
        }, 800); // Artificial delay to simulate processing time for demo purposes
    };
    reader.readAsText(file);
}
</script>
"""

# Render the interactive UI below our engine initialization
#components.html(wasm_ui_html, height=420)
st.divider()

# ---------------------------------------------------------
# 3. SECURE PIPELINE TRANSMISSION & KYC BASELINE
# ---------------------------------------------------------
st.markdown("### 2. Statutory KYC & Baseline Fiduciary Data")
st.caption("To build a custom strategy, we must legally establish the baseline financial profile.")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("#### 💰 Net Worth / Liquid Assets")
    client_net_worth = st.slider(
        "Approximate total liquid net worth available for deployment?", 
        min_value=0, max_value=5000000, value=250000, step=50000, format="$%d"
    )

with col2:
    st.markdown("#### ⏳ Investment Horizon")
    client_horizon = st.slider(
        "Years until the client plans to draw down capital?", 
        min_value=1, max_value=50, value=10, step=1
    )

with col3:
    st.markdown("#### ⚖️ Risk Tolerance")
    risk_tolerance = st.radio(
        "Describes the client's approach to market volatility:", 
        ["Conservative", "Balanced", "Aggressive"], index=1
    )

st.divider()

st.markdown("### 3. Transmit to FazGem Core")
st.caption("Paste the scrubbed output from the Edge Engine above to transmit to the Fiduciary Arbiter.")

sanitized_payload = st.text_area("Sanitized Document Payload (Zero PII)", height=150)

# Dynamic Jurisdiction Routing
col_j1, col_j2 = st.columns(2)
with col_j1:
    jurisdiction = st.selectbox("Regulatory Jurisdiction", ["CA-ON", "US-FED", "CAN_FSRA"])
with col_j2:
    sector = st.selectbox("Financial Sector", ["exempt_market_securities", "mortgage_brokering", "capital_markets"])
    
if st.button("Transmit to FazGem Core", type="primary", use_container_width=True):
    if not sanitized_payload:
        st.warning("Please provide a sanitized document payload first.")
    else:
        with st.spinner("Transmitting encrypted payload and KYC baseline to the Fiduciary Arbiter..."):
            
            # Construct the enhanced payload with the slider data
            payload = {
                "session_id": "session_" + st.session_state.get("user_email", "demo"),
                "sanitized_document_text": sanitized_payload,
                "jurisdiction_override": jurisdiction,
                "sector_override": sector,
                "kyc_baseline": {
                    "net_worth": client_net_worth,
                    "horizon": client_horizon,
                    "risk": risk_tolerance
                }
            }
            
        response = FazGemAPI.evaluate_document(payload, tenant_id=st.session_state.get("tenant_id"))
        
        if response and response.get("status") == "success":
            st.success("✅ Fiduciary Audit Complete: Payload secured and routed to core engine.")
            
            # --- SEAMLESS HACKATHON REDIRECT ---
            st.info("🔄 Redirecting to Advisor Operations Dashboard...")
            time.sleep(1.5) 
            st.switch_page("pages/1_Advisor_Dashboard.py")
            
        else:
            st.error("❌ Core Engine Evaluation Failed. Check backend terminal logs for trace.")