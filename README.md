# 💎 FazGem: Enterprise Pre-Trade AI Interceptor

**FazGem** is an enterprise-grade AI RegTech platform engineered for wealth management and capital markets. It introduces a dual-engine inline interceptor that combines qualitative fiduciary intent reasoning with sub-50ms deterministic statutory math to prevent non-compliant trades *a priori*.

Submitted as part of the **Google Cloud #AllThingsAgentic Hackathon** (*Fortified Enterprise Fleet* track).

---

## 🏛️ System Architecture Overview

FazGem operates as an inline Stage 2 gatekeeper within the 8-Stage Trade Lifecycle:

* **Leg 1: Rose Engine (Qualitative Reasoner)** – Powered by **Gemini 3.7 Flash**, Rose evaluates qualitative intent, fiduciary suitability, and portfolio mandates.
* **Leg 2: Ogu Feray Sentinel (Deterministic Guardrail)** – A sub-50ms Python runtime (`app.py`, `triage.py`) that executes hard mathematical bounds for SEC Rule 15c3-5 and CIRO compliance.
* **Zero-Trust Edge (Model Armor)** – Client intake utilizes WebAssembly (`wasm_sanitizer.py`) to scrub Personally Identifiable Information (PII) locally in browser memory before network transit.
* **Audit Vault** – Immutable logging stored in KMS-encrypted Firestore ledger (`cco_audit_ledger.json`).

---

## 🚀 Spin-Up & Local Setup Instructions

Follow these step-by-step instructions to set up and run FazGem locally or deploy it to Google Cloud.

### Prerequisites

* **Python**: v3.10 or higher
* **Google Cloud SDK**: Installed and authenticated (`gcloud auth login`)
* **Gemini API Key**: Access to Gemini 3.7 Flash via Google GenAI SDK

---

### 1. Clone the Repository

```bash
git clone [https://github.com/fazgem/FazGem-UI.git](https://github.com/fazgem/FazGem-UI.git)
cd FazGem-UI

🛡️ Reproducible Testing & Verification
PII Sanitization Test: Upload a test client text file containing synthetic PII (SIN/SSN, names, addresses). Verify in terminal logs that wasm_sanitizer.py intercepts and scrubs the memory stream prior to backend dispatch.

Pre-Trade Gatekeeping Test: Trigger a trade order exceeding $250,000 or breaching daily cumulative leverage caps. Verify that triage.py emits an immediate sub-50ms hard BLOCK verdict.

Audit Verification: Access the CCO Vault dashboard to confirm the event has been appended to the KMS-encrypted audit ledger.

⚖️ License & Intellectual Property Notice
© 2026 FazGem Inc. All Rights Reserved. Confidential & Proprietary.

Architected and authored by Clifford Amicar, Founder and Lead Architect of FazGem Inc. Conceptualized with the assistance of Google Cloud AI Ecosystem & Gemini 3.7 Flash as an AI Design Co-Pilot.
