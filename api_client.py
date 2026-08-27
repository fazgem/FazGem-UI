"""
FAZGEM API CLIENT (api_client.py)
The secure bridge between the stateless Streamlit edge and the Ogu Feray backend.
Handles dynamic routing, payload transmission, and tenant header injection.
"""

import os
import requests
import streamlit as st

# Resolve Backend URL dynamically 
# In production, this targets the Google Cloud Run URL. For local testing, it defaults to localhost.
BACKEND_URL = os.environ.get("https://fazgem-core-backend-454322585999.us-central1.run.app", "http://localhost:8080").rstrip("/")

class FazGemAPI:
    """Static utility class to handle all secure outbound REST requests."""
    
    @staticmethod
    def evaluate_document(payload_dict: dict, tenant_id: str = "DEFAULT_TENANT") -> dict:
        """
        Transmits the WASM-sanitized edge payload to the backend for 
        Rose's extraction and Ogu Feray's mathematical evaluation.
        """
        endpoint = f"{"https://fazgem-core-backend-454322585999.us-central1.run.app"}/api/v1/evaluate_document"
        
        # We inject the Tenant ID directly into the headers for backend isolation
        headers = {
            "Content-Type": "application/json",
            "X-Tenant-ID": tenant_id  
        }
        
        try:
            # We allow a 15-second timeout since Rose is making live Gemini calls
            response = requests.post(endpoint, json=payload_dict, headers=headers, timeout=15.0)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"🚨 Backend Error [{response.status_code}]: {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            st.error(f"🛑 Critical Connection Error: Could not reach the FazGem Core Backend. Verify the engine is running. Detail: {e}")
            return {}

    @staticmethod
    def fetch_cco_ledger(tenant_id: str = "DEFAULT_TENANT", limit: int = 50) -> list:
        """
        Fetches the decrypted CCO Vault ledger for the specific tenant.
        """
        endpoint = f"{"https://fazgem-core-backend-454322585999.us-central1.run.app"}/api/v1/vault/ledger?limit={limit}"
        headers = {"X-Tenant-ID": tenant_id}
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=10.0)
            
            if response.status_code == 200:
                return response.json().get("ledger", [])
            else:
                st.error(f"🚨 Failed to load Vault: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            st.warning(f"Vault Offline: Unable to connect to backend database. {e}")
            return []