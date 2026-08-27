"""
IDENTITY-AWARE PROXY (IAP) AUTHENTICATION MOCK
Simulates credentialless multi-tenant routing via GCP Workload Identity.
"""

import os

def resolve_identity() -> dict:
    """
    In production, this reads the X-Goog-Authenticated-User-Email and X-Tenant-ID 
    headers injected by Google Cloud IAP before the request hits Streamlit.
    For local development, it provides a secure mock tenant.
    """
    is_production = os.environ.get("FAZGEM_ENV") == "production"
    
    if is_production:
        return {"authenticated": False, "error": "Missing IAP Headers"}
        
    # Local Development Mock Identity
    return {
        "authenticated": True,
        "user_email": "jane.doe@flagship-wealth.ca",
        "tenant_id": "TENANT_FLAGSHIP_001",
        "role": "ADVISOR",  # Can be ADVISOR or CCO
        "jurisdiction_lock": "CA-ON"
    }