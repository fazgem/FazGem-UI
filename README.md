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
