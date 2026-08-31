"""
FAZGEM API CLIENT (api_client.py)
The secure bridge between the stateless Streamlit edge and the Ogu Feray backend.
Handles dynamic routing, payload transmission, and tenant header injection.
"""

import os
import time
import requests
import streamlit as st

# Dynamic backend URL resolution (Defaults to local backend port 8080 inside Docker/Local)
# Change Line 13 from "http://localhost:8080" to "http://fazgem-core-backend:8080"
BACKEND_URL = os.environ.get("BACKEND_URL", "https://fazgem-core-backend-454322585999.us-central1.run.app").rstrip("/")


class FazGemAPI:
    """Static utility class to handle all secure outbound REST requests."""

    @staticmethod
    def evaluate_document(payload_dict: dict, tenant_id: str = "DEFAULT_TENANT") -> dict:
        """Transmits WASM-sanitized payload to Ogu Feray engine."""
        endpoint = f"{BACKEND_URL}/api/v1/evaluate_document"
        headers = {
            "Content-Type": "application/json",
            "X-Tenant-ID": tenant_id
        }

        try:
            start_time = time.perf_counter()
            response = requests.post(endpoint, json=payload_dict, headers=headers, timeout=15.0)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            if response.status_code == 200:
                st.toast(f"Document Processed in {elapsed_ms:.2f} ms", icon="⚡")
                return response.json()
            else:
                st.error(f"🚨 Backend Error [{response.status_code}]: {response.text}")
                return {}

        except requests.exceptions.RequestException as e:
            st.error(f"🔴 Critical Connection Error: Could not reach backend at {endpoint}. Detail: {e}")
            return {}

    @staticmethod
    def fetch_cco_ledger(tenant_id: str = "DEFAULT_TENANT", limit: int = 50) -> list:
        """Fetches decrypted CCO Vault ledger for the tenant."""
        endpoint = f"{BACKEND_URL}/api/v1/vault/ledger?limit={limit}"
        headers = {"X-Tenant-ID": tenant_id}

        try:
            start_time = time.perf_counter()
            response = requests.get(endpoint, headers=headers, timeout=10.0)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            if response.status_code == 200:
                st.toast(f"Vault Synced in {elapsed_ms:.2f} ms", icon="⚡")
                return response.json().get("ledger", [])
            else:
                st.error(f"🚨 Failed to load Vault [{response.status_code}]")
                return []

        except requests.exceptions.RequestException as e:
            st.warning(f"Vault Offline: Unable to connect to backend database. {e}")
            return []