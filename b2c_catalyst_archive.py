import streamlit as st

# =====================================================================
# STRATEGIC ARCHIVE: B2C LEAD GENERATION WIDGET (THE COMPOUNDING CATALYST)
# Vaulted on: July 19, 2026
# Purpose: White-labeled lead magnet for independent wealth managers.
# =====================================================================

def calculate_layer_0_bleed(current_savings, monthly_savings, years_to_retire, annual_return=0.07):
    """The Compounding Catalyst Math Engine."""
    months = years_to_retire * 12
    monthly_rate = annual_return / 12

    def future_value(p, pmt, r, n):
        if n <= 0: return 0
        principal_growth = p * ((1 + r) ** n)
        contribution_growth = pmt * (((1 + r) ** n - 1) / r)
        return principal_growth + contribution_growth

    wealth_today = future_value(current_savings, monthly_savings, monthly_rate, months)
    wealth_wait_3 = future_value(current_savings, monthly_savings, monthly_rate, max(0, months - (3 * 12)))
    wealth_wait_5 = future_value(current_savings, monthly_savings, monthly_rate, max(0, months - (5 * 12)))
    wealth_wait_10 = future_value(current_savings, monthly_savings, monthly_rate, max(0, months - (10 * 12)))

    return {
        "Base_Trajectory": wealth_today,
        "Bleed_3_Years": wealth_today - wealth_wait_3,
        "Bleed_5_Years": wealth_today - wealth_wait_5,
        "Bleed_10_Years": wealth_today - wealth_wait_10
    }

def render_layer_0_hook():
    """PHASE 1: The Gamified Math Bleed (Low Friction B2C Entry)"""
    st.markdown("<h2 style='text-align: center; color: #00d2ff;'>FazGem Vault: Layer 0</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>The Compounding Catalyst - Calculating the mathematical cost of hesitation.</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<h4 style='color: #00d2ff;'>Your Baseline Capital</h4>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #00d2ff; margin-top: 0;'>", unsafe_allow_html=True)

        current_savings = st.slider("Initial Capital ($)", min_value=0, max_value=100000, step=1000, value=5000)
        monthly_savings = st.slider("Monthly Savings ($)", min_value=0, max_value=5000, step=100, value=500)
        years_to_retire = st.slider("Time Horizon (Years)", min_value=5, max_value=50, step=1, value=30)

    with col2:
        results = calculate_layer_0_bleed(current_savings, monthly_savings, years_to_retire)
        st.success(f"🚀 **Optimal Trajectory (Start Today)**\n\nIf you execute today, your projected wealth is **${results['Base_Trajectory']:,.0f}** (adjusted for inflation).")
        st.error(f"⚠️ **The Opportunity Cost of Waiting**\n\nHesitation permanently erases capital from your net worth. Exact mathematical bleed:\n\n"
                 f"- **Wait 3 Years:** Bleed **${results['Bleed_3_Years']:,.0f}**\n"
                 f"- **Wait 5 Years:** Bleed **${results['Bleed_5_Years']:,.0f}**\n"
                 f"- **Wait 10 Years:** Bleed **${results['Bleed_10_Years']:,.0f}**")

    st.markdown("---")
    if st.button("Stop the Bleed: Secure Your Baseline", type="primary", use_container_width=True):
        st.session_state.triage_step = "RPSA"
        st.rerun()