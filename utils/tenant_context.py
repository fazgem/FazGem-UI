"""
TENANT CONTEXT UTILITY (tenant_context.py)
Handles dynamic branding and configuration based on the active tenant ID.
Ensures the UI feels bespoke to each enterprise client.
"""

def get_tenant_branding(tenant_id: str) -> dict:
    """Returns dynamic branding data for the multi-tenant UI."""
    branding_db = {
        "TENANT_FLAGSHIP_001": {
            "firm_name": "Flagship Wealth Partners",
            "primary_color": "#004080",
            "logo_text": "🚢 Flagship Wealth"
        },
        "DEFAULT": {
            "firm_name": "FazGem Enterprise",
            "primary_color": "#4CAF50",
            "logo_text": "🌍 FazGem RCE"
        }
    }
    
    return branding_db.get(tenant_id, branding_db["DEFAULT"])