import dash
from dash import Dash, html, dcc, Input, Output, State
import uuid
import datetime
from google.cloud import firestore
import dash_bootstrap_components as dbc

# Initialize the GCP Firestore Client right below your imports
db = firestore.Client()

# Initialize the Dash app with Bootstrap
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])
#app.title = "FazGem Compliance Review"

def calculate_b2b_compliance_score(data_tier, intercept_tier, llm_tier, retention_tier):
    """
    FazGem Enterprise B2B Compliance Matrix (V4)
    Takes tiers 1-4 for each variable and returns (Score, Risk Level, Narrative)
    """
    # 1. The Point System Mapping
    tier_points = {1: 100, 2: 75, 3: 40, 4: 0}
    
    # 2. Tripwire Alpha: The Litigation Trap
    if data_tier in [3, 4] and intercept_tier in [3, 4]:
        narrative = "CRITICAL VULNERABILITY: Unmasked PII is traversing the open internet before redaction. High probability of SOC2 / HIPAA violation and class-action exposure."
        return 0, "Critical Vulnerability", narrative
        
    # 3. Calculate Base Mathematical Score
    base_score = (tier_points[data_tier] * 0.30) + \
                 (tier_points[intercept_tier] * 0.30) + \
                 (tier_points[llm_tier] * 0.30) + \
                 (tier_points[retention_tier] * 0.10)
                 
    # 4. Tripwire Bravo: The LLM Leak (Cap at 40)
    if data_tier in [2, 3] and llm_tier == 4:
        capped_score = min(base_score, 40)
        narrative = "DATA EXPOSURE RISK: Sensitive corporate data is training public AI models, mirroring the 2023 Samsung intellectual property leak."
        return capped_score, "Critical Vulnerability", narrative
        
    # 5. Standard Routing Logic
    if base_score <= 59:
        risk_tier = "Critical Vulnerability"
        narrative = "Your AI deployment fails standard NIST compliance tests. The transit of unmasked data exposes you to severe regulatory fines. Action: Schedule a Zero-Trust Architecture Audit to see how FazGem closes these gaps."
    elif base_score <= 84:
        risk_tier = "Moderate Risk"
        narrative = "Your infrastructure relies on compensating controls but remains vulnerable to transit-interception. Action: Upgrade to FazGem Edge-Compute Masking to achieve full audit-readiness."
    else:
        risk_tier = "Enterprise Secure"
        narrative = "Your architecture aligns with NIST SP 800-207. Action: Deploy the FazGem Gateway today to maintain this rigorous Zero-Trust posture."
        
    return base_score, risk_tier, narrative

# The 4 V4 Enterprise Matrix Questions
questions = [
    {
        "id": "q1",
        "text": "1. Data Classification: What is the most sensitive tier of data interacting with your AI?",
        "options": [
            {"label": " Level 1: Public / Sanitized Data Only", "value": 1},
            {"label": " Level 2: Internal Corporate Data (No PII)", "value": 2},
            {"label": " Level 3: Regulated PII / Financial Data", "value": 3},
            {"label": " Level 4: Highly Sensitive PHI / Credentials", "value": 4}
        ]
    },
    {
        "id": "q2",
        "text": "2. Masking & Interception Protocol: Where is sensitive data redacted?",
        "options": [
            {"label": " Level 1: Edge-Compute Pre-transit Redaction", "value": 1},
            {"label": " Level 2: Private Cloud Post-transit Redaction", "value": 2},
            {"label": " Level 3: Manual Human Redaction / Ad-Hoc", "value": 3},
            {"label": " Level 4: No Redaction / Raw Data Transmission", "value": 4}
        ]
    },
    {
        "id": "q3",
        "text": "3. LLM / AI Environment: Who controls the model processing the data?",
        "options": [
            {"label": " Level 1: Fully Air-Gapped / Local Edge LLM", "value": 1},
            {"label": " Level 2: Private VPC Enterprise LLM", "value": 2},
            {"label": " Level 3: Opt-Out Public API", "value": 3},
            {"label": " Level 4: Public Shared LLM (e.g., ChatGPT Web)", "value": 4}
        ]
    },
    {
        "id": "q4",
        "text": "4. Regulatory Retention Governance: How are historical logs managed?",
        "options": [
            {"label": " Level 1: Automated, Policy-Driven (WORM Compliant)", "value": 1},
            {"label": " Level 2: Formal Written Policy (Manually Enforced)", "value": 2},
            {"label": " Level 3: Default System Settings", "value": 3},
            {"label": " Level 4: No Policy / Infinite Data Lakes", "value": 4}
        ]
    }
]
# 1. We wrap the initialization in a connector function
def init_pulse_dashboard(server):
    # 2. We pass the main Flask 'server' into Dash and set the URL path
    dash_app = Dash(
        __name__,
        server=server, 
        url_base_pathname='/pulse/', 
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    # 2. The Layout
    # Generate UI for Questions
    def generate_question_ui(q):
        return dbc.Card([
            dbc.CardBody([
                html.H5(q["text"], className="card-title text-dark mb-3"),
                dbc.RadioItems(
                    options=q["options"],
                    value=None,
                    id=q["id"],
                    className="mb-2",
                    style={"fontSize": "16px"}
                )
            ])
        ], className="mb-4 shadow-sm")
    dash_app.layout = dbc.Container = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Enterprise AI Compliance Review", className="text-center fw-bold mt-5 mb-3"),
                    html.P("Find out your organization's exact probability of an AI-driven data breach or compliance failure in under 60 seconds.", className="text-center text-muted mb-5"),
                    
                    # Render Questions
                    html.Div([generate_question_ui(q) for q in questions]),
                    
                    # Submit Button
                    html.Div(
                        dbc.Button("Generate Risk Report", id="submit-btn", color="primary", size="lg", className="w-100 fw-bold shadow-sm"),
                        className="d-grid gap-2 mb-5"
                    ),
                    
                    # Results Div (Hidden initially)
                    html.Div(id="results-output", className="mb-5")
                    
                ], style={"maxWidth": "800px", "margin": "0 auto"})
            ], width=12)
        ])
    ], fluid=True, className="bg-light min-vh-100")

 
   # 3. The Callback (Notice the indentation and 'dash_app')

    @dash_app.callback(
    Output("results-output", "children"),
    Input("submit-btn", "n_clicks"),
    [State("q1", "value"), State("q2", "value"), State("q3", "value"), State("q4", "value")],
    prevent_initial_call=True
)
    def calculate_risk(n_clicks, q1, q2, q3, q4):
        # Validation: Ensure all 4 questions are answered
        if None in [q1, q2, q3, q4]:
            return dbc.Alert("Please answer all 4 questions to generate your report.", color="danger", className="mt-4")
            
        # Pass the inputs directly into our V4 Math Engine!
        score, risk_tier, narrative = calculate_b2b_compliance_score(q1, q2, q3, q4)
        
        # --- ATLAS TELEMETRY PATCH ---
        try:
            # Generate a unique anonymous ID for this specific session
            session_id = str(uuid.uuid4())
            
            # Package the data payload
            telemetry_data = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc),
                "session_id": session_id,
                "q1_response": q1,
                "q2_response": q2,
                "q3_response": q3,
                "q4_response": q4,
                "final_risk_score": score,
                "converted_to_meeting": False # Defaults to False!
            }
            
            # Push to Firestore
            db.collection('pulse_ghost_leads').document(session_id).set(telemetry_data)
            print(f"Logged ghost lead {session_id} with score {score}.")
            
        except Exception as e:
            print(f"Telemetry Error: {e}")
        # -----------------------------

        # Determine UI colors based on risk tier
        if score <= 59:
            color = "danger"
        elif score <= 84:
            color = "warning"
        else:
            color = "success"

        # Generate the Results Card
        return dbc.Card([
            dbc.CardHeader(html.H3("Enterprise Risk Report Generated", className="text-center fw-bold mb-0")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.P("RISK LEVEL", className="text-muted fw-bold mb-0"),
                        html.H4(risk_tier, className=f"text-{color} fw-bold")
                    ], width=6),
                    dbc.Col([
                        html.P("COMPLIANCE SCORE", className="text-muted fw-bold mb-0 text-end"),
                        html.H4(f"{score} / 100", className=f"text-{color} fw-bold text-end")
                    ], width=6)
                ], className="border-bottom pb-3 mb-4"),
                
                html.P(narrative, className="fw-semibold mb-4"),
                
                html.Div(
                    html.A(
                        "Book Your Architecture Review",
                        href="https://calendar.google.com/calendar/u/0/r?pli=1", # UPDATE YOUR LINK HERE
                        target="_blank",
                        className=f"btn btn-{color} btn-lg fw-bold shadow-sm"
                    ),
                    className="text-center"
                )
            ])
        ], className=f"border-{color} shadow-lg mt-5")

# 4. The Return Statement (Must be at the very end of the function)
    return dash_app


 