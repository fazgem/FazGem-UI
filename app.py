"""
FAZGEM ENTERPRISE GATEWAY (app.py)
Zero-Trust entry point. Authenticates via IAP and initializes tenant state.
"""

import streamlit as st
from utils.iap_auth import resolve_identity

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="FazGem | Zero-Trust Gateway", page_icon="🌍", layout="centered")

# 2. RESOLVE IDENTITY (Simulating GCP IAP Headers)
identity = resolve_identity()

# 3. UNAUTHENTICATED STATE (The Security Wall)
if not identity.get("authenticated", False):
    st.error("🔒 **Access Denied: Enterprise SSO Challenge Failed**")
    st.markdown("""
    **No active Identity-Aware Proxy (IAP) session detected.** 
    
    FazGem is a Zero-Trust environment. You must authenticate through your firm's central Identity Provider (Okta, Azure AD, or Google Workspace) to access this node.
    """)
    st.info("💡 *If you are an authorized user, please return to your firm's intranet portal and launch FazGem from the SSO dashboard.*")
    
    # KILLS ALL FURTHER EXECUTION - Sidebar and pages remain inaccessible
    st.stop()

# 4. AUTHENTICATED STATE (The Gateway)
# Persist credentials into session memory for the sub-pages
st.session_state["authenticated"] = True
st.session_state["user_email"] = identity.get("user_email")
st.session_state["tenant_id"] = identity.get("tenant_id")
st.session_state["role"] = identity.get("role")
st.session_state["jurisdiction_lock"] = identity.get("jurisdiction_lock")

# Render the Authorized Gateway
st.title("🌍 FazGem Enterprise Gateway")
st.subheader("Secure Credentialless Authentication")

st.success(f"✅ Identity Verified: **{identity.get('user_email')}**")

# Clean, appropriately sized metrics (The UI Polish)
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🏢 Active Tenant")
    st.markdown(f"**{identity.get('tenant_id')}**")
with col2:
    st.caption("🛡️ Authorization Role")
    st.markdown(f"**{identity.get('role')}**")
with col3:
    st.caption("⚖️ Jurisdictional Lock")
    st.markdown(f"**{identity.get('jurisdiction_lock')}**")

st.divider()

st.info("👉 **Gateway Secured. Select a module from the sidebar to proceed.**")
st.caption("FazGem Regulatory & Compliance Engine (RCE) - Immutable Multi-Tenant Architecture.")