import uuid # <--- Add this at the very top of your file with the other imports
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import redirect, session, has_request_context, render_template
from audit_tools.assessment import init_pulse_dashboard # 1. Import our new connector function from the audit_tools folder
from authlib.integrations.flask_client import OAuth
import dash
from dash import html, dcc, Input, Output, State, no_update, ctx
import pandas as pd  # <--- WE ADD THIS LINE HERE
import plotly.express as px
import datetime
import hashlib
import re 
import unicodedata
#from google import genai - need to install google-genai package and import Client
import requests
import base64 
import dash_bootstrap_components as dbc # Ensure you have this or use standard html.Div
from google.cloud import firestore


# --- 1. CONFIGURATION ---
# ⚠️ PASTE YOUR KEY HERE
#GOOG_API_KEY = "no longer needed here, we are routing through our V2 API server!"

# --- [V77] THE ENGINE 🦅 ---
def initialize_modern_brain():
    try:
        client = genai.Client(api_key=GOOG_API_KEY)
        return client, "ONLINE"
    except Exception as e:
        return None, "OFFLINE"

client, BRAIN_STATUS = initialize_modern_brain()

# --- 2. INITIALIZE APP ---
# [V96] UI POLISH: UNIVERSAL SEND ICON (Fixes French Overflow)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1, maximum-scale=1'}])
app.config.suppress_callback_exceptions = True
server = app.server 

# --- CONNECT THE PULSE PIPELINE ---
init_pulse_dashboard(server)

app.title = "FazGem | Financial Wellness"
# --- THE PROXY SHIELD FIX ---
# Tell the underlying Flask server to trust Google Cloud's HTTPS proxy
server.wsgi_app = ProxyFix(server.wsgi_app, x_proto=1, x_host=1)

# --- VIP CHECK-IN (OAUTH SETUP) ---
# The engine needs a secret key to safely store cookies
app.server.secret_key = "fazgem_super_secret_key_2026"

# --- ENTERPRISE OAUTH CONFIGURATION ---
# 1. Force secure cookies because we are on HTTPS
app.server.config['SESSION_COOKIE_SECURE'] = True
# 2. Allow cookies to jump between www.fazgem.com and fazgem.com safely
app.server.config['SESSION_COOKIE_DOMAIN'] = ".fazgem.com"

# ⚠️ PASTE YOUR GOOGLE KEYS HERE:
GOOGLE_CLIENT_ID = "882691529429-eh72pg4iidlc48k56mujjq2s15agf8lm.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

# The exact door Google will send them back to
# The exact door Google will send them back to
REDIRECT_URI = "https://fazgem.com/callback"

# Initialize the Bouncer
oauth = OAuth(app.server)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- THE DOORWAYS ---
@app.server.route('/login')
def login():
    # Send user to Google
    return google.authorize_redirect(REDIRECT_URI)

@app.server.route('/callback')
def callback():
    # Google sends them back, we grab their ID card and save it in the 'session'
    token = google.authorize_access_token()
    session['user'] = token.get('userinfo')
    return redirect('/')

@app.server.route('/logout')
def logout():
    # Shred the ID card and kick them out to the front step
    session.pop('user', None)
    return redirect('/')

# --- 3. TRANSLATIONS ---
TRANSLATIONS = {
    'en': {
        'tab_home': "Home", 'tab_app': "Ask Rose",
        'hero_title': "Financial Clarity.",
        'hero_sub': "Your AI Guardian against fraud, bad debt, and uncertainty.",
        'how_it_works': [
            "1. 🗂️ **The Data Vault:** Securely drag and drop your bank statement for instant AI ingestion.",
            "2. 🎛️ **Simulate:** Use the interactive sliders to model your real-world mortgage, retirement, and risk scenarios.",
            "3. 🧠 **Analyze:** Chat with Rose to detect financial leaks, explain complex terms, and flag fraud.",
            "4. 🤝 **Enterprise Handoff:** Connect with a vetted advisor. Rose auto-generates a KYC compliance dossier, saving hours of paperwork."
        ],
        'btn_start': "🛡️ Launch Rose",
        'welcome_chat': "👋 **Hello. I am Rose.**\n\nI am your financial guardian. **I do not sell products.**\n\nI can compare scenarios, explain complex terms, and detect fraud.\n\n* 👇 **Select a Mode** on the right (or use the Toggle button) to start.*",
        'disclaimer': "FazGem is an educational tool. Rose provides insights, not legal advice.",
        'lbl_risk': "Risk Profile:", 'lbl_age': "Current Age:", 'lbl_retire': "Retirement Age:", 'lbl_contrib': "Monthly Savings:", 'lbl_tax': "Account Type:",
        'lbl_loan': "Mortgage Amount:", 'lbl_rate': "Interest Rate (%):", 'lbl_years': "Amortization (Years):",
        'lbl_ins_debt': "Total Debt to Cover:", 'lbl_ins_inc': "Annual Income to Replace:", 'lbl_ins_years': "Years of Income Needed:", 'lbl_ins_have': "Existing Life Insurance:",
        'btn_connect_wealth': "Connect Advisor 🤝", 'btn_connect_mort': "Connect Broker 🏠", 'btn_connect_ins': "Connect Specialist 🛡️", 
        # [V96] UNIVERSAL ICON - No text to overflow
        'btn_send': "➤",
        'lbl_wealth_engine': "💰 Wealth Projection", 'lbl_mortgage_engine': "🏠 Mortgage Check", 'lbl_ins_engine': "🛡️ Protection Gap", 'lbl_fraud_engine': "🚨 Fraud Shield",  
        'fraud_checklist': "**STOP. DO NOT CLICK.**\n\n1. 🛑 **Pause.** Scammers create urgency.\n2. 🚫 **Block** the sender immediately.\n3. 🔗 [Report to CAFC (Canada)](https://www.antifraudcentre-centreantifraude.ca/)\n4. 🔗 [Report to FTC (USA)](https://reportfraud.ftc.gov/)",
        'msg_switch_wealth': "💰 **Wealth Mode Active.**\n\nI've pulled up the Growth Engine. Adjust the sliders to see your potential future value.",
        'msg_switch_mort': "🏠 **Mortgage Mode Active.**\n\nI'm ready to calculate payments. Adjust the loan amount and rate to see the true cost.",
        'msg_switch_ins': "🛡️ **Insurance Mode Active.**\n\nLet's find your safety gap. Enter your debts and income needs to see if you are covered.",
        'lbl_read_more': "📚 Click for Analysis, Examples & Scenarios",
        'btn_toggle': "👁️ Show/Hide Dashboard",
        'lbl_tax_opt_reg': "TFSA / RRSP", 'lbl_tax_opt_non': "Taxable / Cash",
        'lbl_rate_type': "Rate Type:"
    },
    'fr': {
        'tab_home': "Accueil", 'tab_app': "Demander à Rose",
        'hero_title': "Clarté Financière.",
        'hero_sub': "Votre Gardienne IA contre la fraude et l'incertitude.",
        'how_it_works': [
            "1. 🗂️ **Le Coffre-fort :** Glissez-déposez votre relevé bancaire en toute sécurité pour une analyse IA instantanée.",
            "2. 🎛️ **Simulez :** Utilisez les curseurs interactifs pour modéliser vos scénarios réels d'hypothèque, de retraite et de risque.",
            "3. 🧠 **Analysez :** Discutez avec Rose pour détecter les fuites financières, expliquer les termes complexes et signaler la fraude.",
            "4. 🤝 **Relais Entreprise :** Parlez à un conseiller. Rose génère automatiquement un dossier de conformité KYC, économisant des heures de paperasse."
        ],
        'btn_start': "🛡️ Lancer Rose",
        'welcome_chat': "👋 **Bonjour. Je suis Rose.**\n\nJe suis votre gardienne financière. **Je ne vends rien.**\n\nJe peux comparer des scénarios, expliquer des termes complexes et détecter la fraude.\n\n* 👇 **Sélectionnez un Mode** à droite pour commencer.*",
        'disclaimer': "FazGem est un outil éducatif. Rose fournit des analyses, pas des conseils.",
        'lbl_risk': "Profil de Risque :", 'lbl_age': "Âge Actuel :", 'lbl_retire': "Âge de Retraite :", 'lbl_contrib': "Épargne Mensuelle :", 'lbl_tax': "Type de Compte :",
        'lbl_loan': "Montant Hypothèque :", 'lbl_rate': "Taux d'Intérêt (%) :", 'lbl_years': "Amortissement (Années) :",
        'lbl_ins_debt': "Dette à Couvrir :", 'lbl_ins_inc': "Revenu à Remplacer :", 'lbl_ins_years': "Années Requises :", 'lbl_ins_have': "Assurance Vie Actuelle :",
        'btn_connect_wealth': "Parler Conseiller 🤝", 'btn_connect_mort': "Parler Courtier 🏠", 'btn_connect_ins': "Parler Spécialiste 🛡️", 
        # [V96] UNIVERSAL ICON - Fixes "Envoyer" overflow
        'btn_send': "➤",
        'lbl_wealth_engine': "💰 Projection Patrimoine", 'lbl_mortgage_engine': "🏠 Vérif. Hypothèque", 'lbl_ins_engine': "🛡️ Analyse Protection", 'lbl_fraud_engine': "🚨 Anti-Fraude", 
        'fraud_checklist': "**ARRÊTEZ. NE CLIQUEZ PAS.**\n\n1. 🛑 **Pause.** Les fraudeurs créent l'urgence.\n2. 🚫 **Bloquez** l'expéditeur.\n3. 🔗 [Signaler (Canada)](https://www.antifraudcentre-centreantifraude.ca/)\n4. 🔗 [Signaler (USA)](https://reportfraud.ftc.gov/)",
        'msg_switch_wealth': "💰 **Mode Patrimoine Activé.**\n\nAjustez les curseurs pour voir votre croissance potentielle.",
        'msg_switch_mort': "🏠 **Mode Hypothèque Activé.**\n\nJe suis prête. Ajustez le montant et le taux pour voir le coût réel.",
        'msg_switch_ins': "🛡️ **Mode Assurance Activé.**\n\nTrouvons votre déficit de protection. Entrez vos dettes et besoins.",
        'lbl_read_more': "📚 Cliquez pour Analyse, Exemples et Scénarios",
        'btn_toggle': "👁️ Afficher/Masquer Outils",
        'lbl_tax_opt_reg': "CELI / REER", 'lbl_tax_opt_non': "Non-Enregistré",
        'lbl_rate_type': "Type de Taux :"
        
    },
}
    # =====================================================================
    # 🌍 FAZGEM GLOBAL COMPLIANCE DICTIONARIES (Loaded on the Edge)
    # =====================================================================
JURISDICTION_FRAMEWORKS = {
            "CANADA_PIPEDA": {
                "health_vectors": ["diagnosis", "treatment", "cardiac", "oncology", "therapy", "mental health", "prescription", "symptoms", "surgery", "blood pressure", "ultrasound", "mri", "patient record"],
                "identity_vectors": ["patient", "client", "individual", "mr.", "mrs.", "dr.", "health card"]
            },
            "US_HIPAA": {
                "health_vectors": ["diagnosis", "treatment", "medicare", "medicaid", "veterans affairs", "hmo", "ppo", "health plan", "medical record number"],
                "identity_vectors": ["patient", "member", "beneficiary", "subscriber", "ssn"]
            },
            "EU_GDPR": {
                "health_vectors": ["genetic data", "biometric data", "health status", "medical provision", "data concerning health"],
                "identity_vectors": ["data subject", "citizen", "resident", "eu individual"]
            }
    }



# --- 4. ENGINE LOGIC ---
def generate_hash(content): return hashlib.sha256(content.encode()).hexdigest()[:8]
def strip_accents(text): return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def sanitize_input(text): 
    if not text: return ""
    return re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text))

# =====================================================================
# 🛡️ FAZGEM LOCAL EDGE SHIELD (ZERO-TRUST HYBRID ENGINE)
# =====================================================================
def local_edge_shield_intercept(user_text: str, jurisdiction: str = "CANADA_PIPEDA") -> tuple[str, bool]:
    """
    Simulates the WASM edge container. 
    Layer 1: Deterministic Regex for hard identifiers.
    Layer 2: Dynamic NLP Simulation based on local Jurisdictional Statutes.
    """
    if not user_text:
        return "", False

    was_masked = False
    modified_text = user_text
    text_lower = modified_text.lower()

    # --- LAYER 1: DETERMINISTIC RULES (The Regex Net) ---
    patterns = {
        "US_SSN": r'\b\d{3}-\d{2}-\d{4}\b',
        "CAN_SIN": r'\b\d{3}[- ]?\d{3}[- ]?\d{3}\b',
        "CREDIT_CARD": r'\b(?:\d[ -]*?){13,16}\b',
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        "PHONE_NA": r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        "DOB_DATE": r'\b(0[1-9]|1[0-2]|[1-9])[-/](0[1-9]|[12]\d|3[01]|[1-9])[-/](19|20)\d{2}\b'
    }

    for token_type, pattern in patterns.items():
        if re.search(pattern, modified_text):
            modified_text = re.sub(pattern, f"[REDACTED: {token_type}]", modified_text)
            was_masked = True

    # --- LAYER 2: DYNAMIC JURISDICTIONAL CONTEXT ---
    # We dynamically pull the dictionary based on the parameter passed to the function
    active_framework = JURISDICTION_FRAMEWORKS.get(jurisdiction, JURISDICTION_FRAMEWORKS["CANADA_PIPEDA"])
    
    has_health_context = any(health_word in text_lower for health_word in active_framework["health_vectors"])
    has_identity_context = any(id_word in text_lower for id_word in active_framework["identity_vectors"])

    if has_health_context and has_identity_context:
        # The block message dynamically updates to cite the specific law that caught it!
        law_name = jurisdiction.split("_")[1] # Extracts PIPEDA, HIPAA, or GDPR
        modified_text = f"[🛡️ FAZGEM EDGE INTERCEPT: Contextual {law_name} Health Data Detected. Prompt Structurally Quarantined at Edge.]"
        was_masked = True

    return modified_text, was_masked

    # ---------------------------------------------------------
    # 🌉 THE FAZGEM V2 API BRIDGE
    # We are no longer using the basic direct-to-Google call.
    # We are routing the message to our Enterprise V2 Server!
    # ---------------------------------------------------------
    
def call_external_brain_gemini(clean_text, context_data, lang):
    # Generate a unique ID for this specific browser session
    if not hasattr(call_external_brain_gemini, "session_id"):
        call_external_brain_gemini.session_id = f"session_{uuid.uuid4().hex[:8]}"

    payload = {
        "user_uid": "test_user_alpha", 
        "session_id": call_external_brain_gemini.session_id, # <--- 🧠 THE FIX: A fresh memory bank!
        "message": f"[UI State: {context_data}] User says: {clean_text}"
    }
    
    try:
        # We fire the packet to the API
        url = "https://fazgem-v2-882691529429.northamerica-northeast1.run.app/api/chat"
        response = requests.post(url, json=payload, timeout=20)

        # We catch the reply
        if response.status_code == 200:
            try:
                reply = response.json().get("reply", "No reply found.")
                return reply, "V2_ENTERPRISE_API"
            except Exception:
                # If the API sends mangled data, gracefully handle it
                return "⚠️ Secure connection to the AI core experienced a brief interruption. Please try again in a moment.", "API_BLOCKED"
        else:
            # If Google Cloud throws a 500/502 error, we catch it elegantly without using .json()
            return "⚠️ Rose is currently experiencing high volume or a brief network delay. Please try your request again.", "API_BLOCKED"

    except requests.exceptions.RequestException as e:
        # If the server is completely asleep and times out
        return "⚠️ The secure vault is warming up. Connection timed out—please try again in a few seconds.", "API_TIMEOUT"


def get_rose_response(user_text, current_mode, lang, w_data, m_data, i_data):
    if not user_text: return ("", "", "EMPTY", current_mode)
    clean_text = sanitize_input(user_text)
    
    #fraud_msg, fraud_code = check_fraud(user_text.lower(), lang)
    #if fraud_msg: return (fraud_msg, "Fraud Detected", fraud_code, "fraud")

    new_mode = current_mode
    txt = user_text.lower()
    if any(x in txt for x in ['mortgage', 'house', 'loan', 'rate', 'hypothèque', 'maison', 'pret']): new_mode = 'mortgage'
    elif any(x in txt for x in ['wealth', 'retire', 'save', 'invest', 'patrimoine', 'retraite']): new_mode = 'wealth'
    elif any(x in txt for x in ['insurance', 'protect', 'life', 'gap', 'assurance', 'vie', 'famille']): new_mode = 'insurance'
    elif any(x in txt for x in ['fraud', 'scam', 'suspicious', 'fraude', 'arnaque']): new_mode = 'fraud'

    context_data = {'mode': new_mode}
    if new_mode == 'wealth': context_data.update(w_data)
    elif new_mode == 'mortgage': context_data.update(m_data)
    elif new_mode == 'insurance': context_data.update(i_data)

    # Use regex boundary \b to ensure we only match exact words!
    local_triggers = [r"\bconnect\b", r"\badvisor\b", r"\bbroker\b", r"\bparler\b"]
    if any(re.search(pat, strip_accents(txt)) for pat in local_triggers):
        return ("**Concierge Mode Activated** 🥂. I am preparing the secure handoff dossier. (Live Advisor Routing unlocking in Phase 2).", "Hand-off", "TRANSFER", new_mode)

        
    brain_response, reason = call_external_brain_gemini(clean_text, context_data, lang)
    return (brain_response, reason, "AI_GENERATED", new_mode)

# ... existing code (get_rose_response, etc.) ...

# =====================================================================
# 🎨 UI HELPER COMPONENTS
# =====================================================================
def render_chat_bubble(text_or_components, is_user=True, was_shielded=False):
    """
    Renders ultra-sleek, modern chat bubbles matching the premium B2B UI framework.
    """
    if is_user:
        # Premium Deep Blue for User Messages (Turns Crimson if Shielded)
        bg_color = "#7f1d1d" if was_shielded else "#1e3a8a"
        border_style = "none"
        text_color = "#ffffff"
        align = "flex-end"
        margin = "10px 0px 10px auto"
    else:
        # Minimalist, Clean Off-White for Rose Response
        bg_color = "#ffffff"
        border_style = "1px solid #e2e8f0"
        text_color = "#0f172a"
        align = "flex-start"
        margin = "10px auto 10px 0px"

    # The warning badge if the Edge Shield was triggered
    shield_badge = html.Span("🛡️ LOCAL EDGE SHIELD ACTIVE\n\n", style={"fontWeight": "bold", "fontSize": "11px", "color": "#fca5a5", "display": "block"}) if was_shielded and is_user else ""

    # Check if we passed a string or an existing HTML component (like Rose's 'Read More' buttons)
    if isinstance(text_or_components, str):
        content = html.P(text_or_components, style={"margin": "0", "whiteSpace": "pre-wrap"})
    else:
        content = text_or_components

    return html.Div(
        style={
            "maxWidth": "85%",
            "width": "fit-content",
            "padding": "14px 20px",
            "borderRadius": "16px",
            "backgroundColor": bg_color,
            "border": border_style,
            "color": text_color,
            "fontFamily": "Segoe UI, Arial, sans-serif",
            "fontSize": "15px",
            "lineHeight": "1.5",
            "boxShadow": "0 2px 5px rgba(0,0,0,0.02)",
            "margin": margin,
            "alignSelf": align
        },
        children=[shield_badge, content]
    )

# --- 5. VISUALS ---
def generate_wealth_story(age_now, age_retire, final_amt, principal, lang):
    interest = final_amt - principal
    t = {'en': "Projected Value", 'fr': "Valeur Projetée"}
    if lang == 'fr': 
        details = f"* **Vos Contributions :** ${principal:,.0f}\n* **Intérêts :** ${interest:,.0f}"
    else: 
        details = f"* **Your Cash:** ${principal:,.0f}\n* **Market Growth:** ${interest:,.0f}"
    return f"### {t[lang]}\n**${final_amt:,.0f}**\n\n{details}"

def generate_mortgage_story(monthly, total_cost, total_int, lang):
    t = {'en': "Monthly Payment", 'fr': "Paiement Mensuel"}
    return f"### {t[lang]}\n**${monthly:,.2f}**\n*(Interest Cost: ${total_int:,.0f})*"

def generate_insurance_story(gap, lang):
    t = {'en': ["Coverage Gap", "Fully Covered"], 'fr': ["Déficit", "Couvert"]}
    status = f"⚠️ **{t[lang][0]}**" if gap > 0 else f"✅ **{t[lang][1]}**"
    return f"### {status}\n**${gap:,.0f}**"

# --- 6. LAYOUT STYLES ---
NAVY = "#2C3E50"
SOFT_BG = "#F4F6F8"
WHITE = "#FFFFFF"
ACCENT = "#D4AF37" 

# --- 7. APP LAYOUT ---
def get_main_layout():
    return html.Div(className='app-container', children=[
        # 🧠 RESTORED: THE INVISIBLE MEMORY BANK
        dcc.Store(id='active-mode', data='wealth'), dcc.Store(id='vault-signal', data=None),
        
        # 🕳️ THE DUMMY DROP: A hidden mailbox to catch the ghost data and stop React from crashing!
        html.Div(id='welcome-msg', style={'display': 'none'}),
        
        # 🧠 NEW: The Invisible Page Load Trigger
        dcc.Location(id='url', refresh=False),
        
        # NAVBAR
        html.Div([
            html.Div([
                html.H2("FAZGEM™", style={'color': WHITE, 'margin': 0, 'fontWeight': '700', 'letterSpacing': '2px', 'fontSize': '1.5em'}),
        ], style={'display': 'flex', 'alignItems': 'center'}),

        # RIGHT SIDE OF NAVBAR (Toggle + Logout)
        html.Div(id='b2b-flex-container', style={'display': 'flex', 'gap': '30px', 'marginTop': '20px'}, children=[
            # THE SECRET B2B TRIGGER FOR INVESTOR DEMOS
            html.Button("💼", id="btn-secret-b2b", n_clicks=0, style={'background': 'transparent', 'border': 'none', 'cursor': 'pointer', 'fontSize': '1.5em', 'marginLeft': '15px'}),
            
            dcc.RadioItems(id='lang-toggle', options=[{'label': ' EN', 'value': 'en'}, {'label': ' FR', 'value': 'fr'}], value='en', 
                           labelStyle={'display': 'inline-block', 'color': WHITE, 'marginLeft': '15px', 'cursor': 'pointer', 'fontWeight': 'bold'}),
            # The Logout Door
            html.A("🚪 Logout", href="/logout", style={'color': '#EF9A9A', 'marginLeft': '25px', 'textDecoration': 'none', 'fontWeight': 'bold', 'fontSize': '0.9em'})
        ])
    ], style={'padding': '15px 20px', 'backgroundColor': NAVY, 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'}),

    
    # MAIN CONTENT
    html.Div([
        dcc.Tabs(id="tabs-main", value='tab-home', 
            colors={"border": SOFT_BG, "primary": NAVY, "background": "#E0E0E0"}, 
            
            # [FIX 1] PARENT: Add 'display': 'flex' here. This tells the container to stretch its children.
            style={'marginTop': '20px', 'maxWidth': '1000px', 'margin': '20px auto 0 auto', 'display': 'flex'},

            children=[
                # [FIX 2] CHILDREN: Merge styles into ONE dictionary. 'flex': '1' makes them share space equally.
                dcc.Tab(label='Home', value='tab-home', 
                        style={'borderRadius': '10px 10px 0 0', 'flex': '1', 'textAlign': 'center'}), 
                
                dcc.Tab(label='Ask Rose', value='tab-app', 
                        style={'borderRadius': '10px 10px 0 0', 'flex': '1', 'textAlign': 'center'})
            ]
        ),

        # HOME TAB
        html.Div(id='home-container', style={'maxWidth': '800px', 'margin': '40px auto', 'textAlign': 'center', 'padding': '20px'}, children=[
            # ... (The rest of your code remains exactly the same)      
            html.H1(id='home-title', style={'color': NAVY, 'fontSize': '2.8em', 'marginBottom': '10px'}),
            html.H3(id='home-sub', style={'color': '#E0E0E0', 'fontWeight': '300'}),
            html.Div(id='home-steps', style={'marginTop': '40px', 'textAlign': 'left', 'backgroundColor': WHITE, 'padding': '30px', 'borderRadius': '15px', 'boxShadow': '0 4px 10px rgba(0,0,0,0.05)'}),
            # [V93] FLEXBOX CENTERING FOR LAUNCH BUTTON
            html.Button(id='btn-launch-rose', n_clicks=0, style={'marginTop': '40px', 'backgroundColor': NAVY, 'color': WHITE, 'padding': '15px 30px', 'borderRadius': '30px', 'border': 'none', 'fontSize': '1.1em', 'fontWeight': 'bold', 'cursor': 'pointer', 'boxShadow': '0 4px 15px rgba(44, 62, 80, 0.3)', 'display': 'inline-flex', 'alignItems': 'center', 'justifyContent': 'center'}),
        ]),

        # APP TAB
        html.Div(id='app-container', style={'display': 'none', 'maxWidth': '1200px', 'margin': 'auto', 'padding': '10px'}, children=[
            
            # [V77] TOGGLE BUTTON ROW
            html.Div(style={'textAlign': 'right', 'marginBottom': '10px'}, children=[
                # [V93] FLEXBOX CENTERING FOR TOGGLE BUTTON
                html.Button(id='btn-toggle-tools', n_clicks=1, style={'backgroundColor': '#90A4AE', 'color': WHITE, 'border': 'none', 'padding': '8px 15px', 'borderRadius': '20px', 'cursor': 'pointer', 'fontSize': '0.9em', 'fontWeight': 'bold', 'display': 'inline-flex', 'alignItems': 'center', 'justifyContent': 'center'})
            ]),

            html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px'}, children=[
                
                # LEFT: CHAT
                # 🗂️ THE DATA VAULT (DRAG & DROP)
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div(id='upload-text', children='📂 Drag and Drop your Document (PDF, Image, CSV) here'),
                        style={
                            'width': '100%', 'height': '50px', 'lineHeight': '50px',
                            'borderWidth': '2px', 'borderStyle': 'dashed', 'borderRadius': '10px',
                            'textAlign': 'center', 'marginBottom': '15px', 'backgroundColor': '#E3F2FD',
                            'cursor': 'pointer', 'color': '#1565C0', 'fontWeight': 'bold'
                        },
                        multiple=False
                    ), html.Div("Supported: Bank Statements, Portfolio Summaries (PDF, Image, CSV). Max 5MB.", style={'fontSize': '0.8em', 'color': '#546E7A', 'marginTop': '5px', 'textAlign': 'center', 'marginBottom': '10px'}),
                    html.Div(id='upload-status', style={'textAlign': 'center', 'color': '#2E7D32', 'fontWeight': 'bold', 'marginBottom': '10px'}),
               html.Div(style={'flex': '1', 'minWidth': '300px', 'maxWidth': '800px', 'margin': '0 auto'}, children=[
                    
                # [V95] RESTORED SPINNER
                dcc.Loading(id="loading-chat", type="dot", color=NAVY, children=[
                        html.Div(id='chat-window', style={'height': '550px', 'overflowY': 'auto', 'padding': '20px', 'backgroundColor': WHITE, 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'}, children=[]),
                    ]),
                    
                    # [V91] FLEXBOX ROW for Input + Send Button
                    html.Div([
                        dcc.Input(id='user-input', type='text', placeholder='Message...', n_submit=0, style={'flex': '1', 'padding': '15px', 'borderRadius': '25px', 'border': '1px solid #CFD8DC', 'outline': 'none', 'minWidth': '0'}),
                        # [V93] FLEXBOX CENTERING FOR SEND BUTTON
                        html.Button('➤', id='send-button', n_clicks=0, style={'marginLeft': '10px', 'padding': '0', 'width': '50px', 'height': '50px', 'backgroundColor': NAVY, 'color': WHITE, 'border': 'none', 'borderRadius': '50%', 'cursor': 'pointer', 'flexShrink': '0', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'fontSize': '1.2em'})
                    ], style={'marginTop': '15px', 'display': 'flex', 'alignItems': 'center'}), 
                    html.Div(
                            "FazGem is an AI-powered financial intelligence platform, not a registered investment advisor. Information provided is for educational and simulation purposes and does not constitute financial, legal, or tax advice.",
                            style={
                                'fontSize': '11px',
                                'color': '#888888',
                                'textAlign': 'center',
                                'marginTop': '10px',
                                'fontFamily': 'Arial, sans-serif',
                                'padding': '0 15px'
                            }
                        ),
                    
                 # --- THE ENTERPRISE DATA WALLET ---
        html.Details(style={'marginTop': '15px', 'border': '1px solid #E0E0E0', 'borderRadius': '8px', 'padding': '12px', 'backgroundColor': '#F8F9FA', 'maxWidth': '800px', 'margin': '15px auto'}, children=[
            html.Summary("🔐 Enterprise Data Wallet & Consent", style={'fontWeight': 'bold', 'cursor': 'pointer', 'color': NAVY, 'fontSize': '0.95em'}),
            
            html.Div(style={'marginTop': '15px', 'fontSize': '0.85em', 'color': '#333'}, children=[
                html.H4("1. Algorithmic Profiling Status", style={'borderBottom': '1px solid #ccc', 'paddingBottom': '5px', 'marginTop': '0'}),
                html.Div(style={'display': 'flex', 'gap': '10px', 'flexWrap': 'wrap', 'marginBottom': '15px'}, children=[
                    html.Span("Risk: Assessed", style={'background': '#E3F2FD', 'padding': '4px 10px', 'borderRadius': '12px', 'border': '1px solid #90CAF9'}),
                    html.Span("KYC: Incomplete", style={'background': '#FFF3E0', 'padding': '4px 10px', 'borderRadius': '12px', 'border': '1px solid #FFCC80'}),
                    html.Span("AML Flags: Clear", style={'background': '#E8F5E9', 'padding': '4px 10px', 'borderRadius': '12px', 'border': '1px solid #A5D6A7'}),
                ]),
                
                html.H4("2. Fiduciary Handoff Authorization", style={'borderBottom': '1px solid #ccc', 'paddingBottom': '5px'}),
                dcc.Checklist(
                    id='consent-toggle',
                    options=[{'label': ' I authorize FazGem to compile and encrypt my chat history into a B2B Suitability Dossier for a registered fiduciary advisor.', 'value': 'authorized'}],
                    value=[], 
                    style={'marginTop': '10px', 'marginBottom': '10px', 'lineHeight': '1.5', 'fontWeight': 'bold', 'color': '#D32F2F'}
                ),
                html.Div(id='wallet-status', style={'color': 'gray', 'fontStyle': 'italic', 'fontSize': '0.9em'}, children="*System Status: Dossier Locked. B2B Pipeline awaiting user authorization.*")
            ])
        ]),
    ]),
    # 🕳️ THE DUMMY DROPS (Catch the old callback data to stop the crash!)
                html.Div(id='lbl-audit', style={'display': 'none'}),
                html.Div(id='audit-log-display', style={'display': 'none'}),

                # RIGHT: TOOLS
                html.Div(id='right-panel-container', style={'flex': '1', 'minWidth': '300px', 'maxWidth': '100%', 'margin': '0 auto'}, children=[
                    html.Div(id='cockpit-panel', style={'padding': '25px', 'backgroundColor': WHITE, 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'}, children=[
                        
                        html.Div(style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap', 'marginBottom': '20px', 'borderBottom': '1px solid #EEE', 'paddingBottom': '15px', 'gap': '10px'}, children=[
                            html.Button("💰 Wealth", id='btn-mode-wealth', n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontWeight': 'bold', 'color': '#2E7D32'}),
                            html.Button("🏠 Mortgage", id='btn-mode-mort', n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontWeight': 'bold', 'color': '#1565C0'}),
                            html.Button("🛡️ Insurance", id='btn-mode-ins', n_clicks=0, style={'border': 'none', 'background': 'none', 'cursor': 'pointer', 'fontWeight': 'bold', 'color': '#C62828'}),
                        ]),

                        html.Div(id='wealth-controls', children=[
                            html.H4(id='lbl-wealth-engine', style={'color': '#2E7D32', 'borderBottom': '2px solid #A5D6A7', 'paddingBottom': '10px'}),
                           html.Label(id='lbl-risk', style={'fontWeight': 'bold', 'color': NAVY}), 
                            dcc.Dropdown(id='dropdown-risk', options=[{'label': '⚖️ Balanced', 'value': 'Balanced'}, {'label': '🛡️ Safe', 'value': 'Conservative'}, {'label': '🚀 Growth', 'value': 'Aggressive'}], value='Balanced', clearable=False, style={'marginBottom': '20px'}),
                            
                            html.Label(id='lbl-age', style={'fontWeight': 'bold', 'color': NAVY}), dcc.Slider(id='slider-age-now', min=18, max=60, step=1, value=30, marks=None, tooltip={'placement': 'bottom', 'always_visible': True}),
                            html.Br(), html.Label(id='lbl-retire', style={'fontWeight': 'bold', 'color': NAVY}), dcc.Slider(id='slider-age-retire', min=50, max=75, step=1, value=65, marks=None, tooltip={'placement': 'bottom', 'always_visible': True}),
                            html.Br(), html.Label(id='lbl-contrib', style={'fontWeight': 'bold', 'color': NAVY}), dcc.Slider(id='slider-contrib', min=50, max=2000, step=50, value=500, marks=None, tooltip={'placement': 'bottom', 'always_visible': True}),
                            html.Br(), html.Label(id='lbl-tax', style={'fontWeight': 'bold', 'color': NAVY}), dcc.RadioItems(id='radio-tax', value='TFSA', inline=True)
                        ]),

                        html.Div(id='mortgage-controls', style={'display': 'none'}, children=[
                            html.H4(id='lbl-mortgage-engine', style={'color': '#1565C0', 'borderBottom': '2px solid #90CAF9', 'paddingBottom': '10px'}),
                            html.Label(id='lbl-rate-type', style={'fontWeight': 'bold', 'color': NAVY}),
                            dcc.RadioItems(id='radio-mort-type', options=[{'label': ' Fixed', 'value': 'Fixed'}, {'label': ' Variable', 'value': 'Variable'}], value='Fixed', inline=True, style={'marginBottom': '15px'}),
                            
                            html.Label(id='lbl-loan', style={'fontWeight': 'bold', 'color': NAVY}), dcc.Slider(id='slider-mort-loan', min=100000, max=2000000, step=10000, value=500000, marks=None, tooltip={'placement': 'bottom', 'always_visible': True}),
                            html.Br(), html.Label(id='lbl-rate', style={'fontWeight': 'bold', 'color': NAVY}), dcc.Slider(id='slider-mort-rate', min=1.0, max=10.0, step=0.1, value=5.0, marks=None, tooltip={'placement': 'bottom', 'always_visible': True}),
                            html.Br(), html.Label(id='lbl-years', style={'fontWeight': 'bold', 'color': NAVY}), dcc.Slider(id='slider-mort-years', min=5, max=30, step=5, value=25, marks=None, tooltip={'placement': 'bottom', 'always_visible': True})
                        ]),

                        html.Div(id='insurance-controls', style={'display': 'none'}, children=[
                            html.H4(id='lbl-ins-engine', style={'color': '#C62828', 'borderBottom': '2px solid #EF9A9A', 'paddingBottom': '10px'}),
                            
                            html.Label(id='lbl-ins-debt', style={'fontWeight': 'bold', 'color': NAVY}), dcc.Slider(id='slider-ins-debt', min=0, max=1000000, step=50000, value=500000, marks=None, tooltip={'placement': 'bottom', 'always_visible': True}),
                            html.Br(), html.Label(id='lbl-ins-inc', style={'fontWeight': 'bold', 'color': NAVY}), dcc.Slider(id='slider-ins-inc', min=30000, max=300000, step=10000, value=80000, marks=None, tooltip={'placement': 'bottom', 'always_visible': True}),
                            html.Br(), html.Label(id='lbl-ins-years', style={'fontWeight': 'bold', 'color': NAVY}), dcc.Slider(id='slider-ins-years', min=0, max=25, step=1, value=10, marks=None, tooltip={'placement': 'bottom', 'always_visible': True}),
                            html.Br(), html.Label(id='lbl-ins-have', style={'fontWeight': 'bold', 'color': NAVY}), dcc.Slider(id='slider-ins-have', min=0, max=1000000, step=50000, value=100000, marks=None, tooltip={'placement': 'bottom', 'always_visible': True})
                        ]),
                        
                        html.Div(id='fraud-controls', style={'display': 'none'}, children=[
                            html.H4(id='lbl-fraud-engine', style={'color': '#D32F2F', 'textAlign': 'center'}),
                            html.Div(style={'backgroundColor': '#FFEBEE', 'padding': '15px', 'borderRadius': '10px', 'border': '1px solid #EF9A9A'}, children=[dcc.Markdown(id='fraud-checklist-display')])
                        ]),

                        html.Br(),
                        dcc.Graph(id='simulation-graph', config={'displayModeBar': False}, style={'height': '250px'}),
                        html.Div(id='narrative-box', style={'backgroundColor': '#FAFAFA', 'padding': '15px', 'borderRadius': '10px', 'marginTop': '15px', 'borderLeft': '4px solid #2E7D32'}),
                        html.Br(),
                        # [V93] FLEXBOX CENTERING FOR CONNECT BUTTON
                        html.Button(id='connect-btn', n_clicks=0, style={'width': '100%', 'padding': '15px', 'backgroundColor': ACCENT, 'color': WHITE, 'border': 'none', 'borderRadius': '8px', 'fontSize': '1em', 'fontWeight': 'bold', 'cursor': 'pointer', 'whiteSpace': 'normal', 'height': 'auto', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
                    ])
                ])
            ])
        ])
    ]),
    # --- THE SECRET B2B PARTNER PORTAL (MODAL) ---
        html.Div(id='b2b-modal', style={'display': 'none', 'position': 'fixed', 'top': '10%', 'left': '10%', 'width': '80%', 'height': '75%', 'backgroundColor': '#121212', 'zIndex': 9999, 'borderRadius': '15px', 'padding': '40px', 'color': 'white', 'boxShadow': '0 20px 50px rgba(0,0,0,0.8)', 'overflowY': 'auto', 'border': '1px solid #333'}, children=[
            html.H2("🛡️ FAZGEM ENTERPRISE: ADVISOR PORTAL", style={'color': '#A5D6A7', 'borderBottom': '1px solid #333', 'paddingBottom': '15px'}),
            
           html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px', 'marginTop': '20px'}, children=[
                # Left Column: KYC Data
                html.Div(style={'flex': '1', 'backgroundColor': '#1E1E1E', 'padding': '20px', 'borderRadius': '10px'}, children=[
                    html.H4("📂 ACTIVE LEAD: Client #88The Enterprise Data Wallet29", style={'color': '#90CAF9'}),
                    html.Hr(style={'borderColor': '#333'}),
                    html.P("KYC/AML Status: ✅ VERIFIED AUTOMATICALLY"),
                    html.P("Document Scanned: Bank Statement (PDF)"),
                    html.P("Risk Tolerance: Balanced"),
                    html.P("Estimated Wealth Focus: Growth & Consolidation"),
                    html.Button("📞 INITIATE SECURE CALL", style={'marginTop': '20px', 'width': '100%', 'padding': '15px', 'backgroundColor': '#1565C0', 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'fontWeight': 'bold', 'cursor': 'pointer', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '10px'}),
                    html.Div("Live Advisor Routing unlocking in Phase 2.", style={'color': '#FFD700', 'fontSize': '12px', 'textAlign': 'center', 'marginTop': '10px', 'fontStyle': 'italic'})
                ]),
                
                # Right Column: Rose's Summary
                html.Div(style={'flex': '2', 'backgroundColor': '#1E1E1E', 'padding': '20px', 'borderRadius': '10px'}, children=[
                    html.H4("🧠 ROSE COMPLIANCE & STRATEGY BRIEF", style={'color': '#CE93D8'}),
                    html.Hr(style={'borderColor': '#333'}),
                    dcc.Markdown("""
                    **Source:** Concierge Handoff (User requested human advisor)
                    
                    **AI Pre-Meeting Brief:**
                    * Client exhibits high uninvested cash reserves sitting in standard checking accounts.
                    * High recurring subscription burn rate detected; excellent opportunity for budget consolidation.
                    * **Recommended Advisor Action:** Pitch the 'FazGem Premium Wealth Tier' to redirect subscription leaks into a tax-advantaged growth portfolio.
                    
                    *Note: This brief was generated securely by FazGem AI. All PII has been encrypted.*
                    """)
                ])
            ]),
            # Close Button
            html.Button("CLOSE PORTAL", id="btn-close-b2b", n_clicks=0, style={'marginTop': '30px', 'padding': '10px 20px', 'backgroundColor': '#C62828', 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'float': 'right'})
        ])
])
# --- THE VIP ROUTER (LOCKED DOOR) ---
def serve_layout():
    # BYPASS LOGIN FOR LOCAL DEMO RECORDING
    return get_main_layout()

# Tell Dash to use the router
app.layout = serve_layout

def render_compliance_workspace(lang='en'):
    t = {
        'en': {
            'tab1': '🛡️ Audit Live',
            'tab2': '🎙️ Meeting Co-Pilot',
            'tab3': '📈 Optimization',
            'status': 'System Status: Active Monitoring',
        },
        'fr': {
            'tab1': '🛡️ Audit en Direct',
            'tab2': '🎙️ Co-Pilote de Réunion',
            'tab3': '📈 Optimisation',
            'status': 'État du système : Surveillance Active',
        }
    }[lang]

    return html.Div([
        # Header for the Workspace
        html.Div([
            html.H3("Gemie: Expert AI Compliance War Room", style={'color': '#D4AF37', 'marginBottom': '5px'}),
            html.Span(t['status'], style={'color': '#2E7D32', 'fontSize': '0.85em', 'fontWeight': 'bold'})
        ], style={'padding': '15px', 'borderBottom': '1px solid #E0E0E0'}),

        dcc.Tabs(id="compliance-tabs", value='tab-audit', children=[
            # TAB 1: Live Red Flags & Lifecycle
            dcc.Tab(label=t['tab1'], value='tab-audit', children=[
                html.Div([
                    html.P("Live Red Flag Ticker (Pulse Analysis)", style={'marginTop': '15px', 'fontWeight': 'bold'}),
                    html.Div(id='compliance-live-ticker', style={
                        'height': '200px', 'backgroundColor': '#1E1E1E', 'color': '#00FF00', 
                        'padding': '10px', 'fontFamily': 'Courier New', 'borderRadius': '5px', 'overflowY': 'scroll'
                    }, children=["> Initializing real-time transaction monitoring...", html.Br(), "> Scanning regulatory updates for G7 jurisdictions..."])
                ], style={'padding': '20px'})
            ]),

            # TAB 2: Meeting Co-Pilot (Gemini Brain)
            dcc.Tab(label=t['tab2'], value='tab-pilot', children=[
                html.Div([
                    html.Div([
                        html.Button("⏺️ Start Secure Meeting", id="btn-start-meeting", className="btn-pilot-start"),
                        html.Button("⏹️ End & Auto-Document", id="btn-end-meeting", className="btn-pilot-end"),
                    ], style={'display': 'flex', 'gap': '10px', 'marginTop': '15px'}),
                    html.Div(id='meeting-transcription-view', children=[
                        html.P("Real-time extraction will appear here during client interactions.", 
                               style={'fontStyle': 'italic', 'color': '#666', 'marginTop': '20px'})
                    ])
                ], style={'padding': '20px'})
            ]),

            # TAB 3: Business Optimization (Cost/Efficiency)
            dcc.Tab(label=t['tab3'], value='tab-opti', children=[
                html.Div([
                    html.H4("Efficiency & Effectiveness Report", style={'marginTop': '15px'}),
                    html.Div(id='optimization-metrics', children=[
                        html.P("AI-detected workflow gaps: 3 items identified."),
                        html.P("Potential monthly labor savings: 14.5 hours.")
                    ])
                ], style={'padding': '20px'})
            ]),
        ], style={'marginTop': '10px'})
    ], style={'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0px 4px 10px rgba(0,0,0,0.1)'})

# --- 8. CALLBACKS ---
@app.callback(
    [Output('tabs-main', 'value'), Output('home-container', 'style'), Output('app-container', 'style'),
     Output('chat-window', 'children'), Output('user-input', 'value'),
     Output('active-mode', 'data'), Output('wealth-controls', 'style'), Output('mortgage-controls', 'styl' \
     'e'), Output('insurance-controls', 'style'), Output('fraud-controls', 'style'),
     Output('simulation-graph', 'figure'), Output('simulation-graph', 'style'), Output('narrative-box', 'children'), Output('narrative-box', 'style'),
     Output('home-title', 'children'), Output('home-sub', 'children'), Output('btn-launch-rose', 'children'), Output('home-steps', 'children'),
     Output('welcome-msg', 'children'), Output('lbl-risk', 'children'), Output('lbl-age', 'children'), Output('lbl-retire', 'children'), Output('lbl-contrib', 'children'), Output('lbl-tax', 'children'), Output('connect-btn', 'children'), 
     Output('lbl-wealth-engine', 'children'), 
     Output('lbl-mortgage-engine', 'children'), Output('lbl-loan', 'children'), Output('lbl-rate', 'children'), Output('lbl-years', 'children'),
     Output('lbl-ins-engine', 'children'), 
     Output('lbl-ins-debt', 'children'), Output('lbl-ins-inc', 'children'), Output('lbl-ins-years', 'children'), Output('lbl-ins-have', 'children'),
     Output('lbl-fraud-engine', 'children'), Output('fraud-checklist-display', 'children'),
     Output('send-button', 'children'), Output('dropdown-risk', 'options'), Output('radio-tax', 'options'),
     Output('cockpit-panel', 'style'),
     Output('right-panel-container', 'style'), Output('btn-toggle-tools', 'children'),
     Output('lbl-rate-type', 'children')],
    [Input('tabs-main', 'value'), Input('btn-launch-rose', 'n_clicks'), Input('send-button', 'n_clicks'), Input('user-input', 'n_submit'), Input('connect-btn', 'n_clicks'), Input('lang-toggle', 'value'),
     Input('slider-age-now', 'value'), Input('slider-age-retire', 'value'), Input('slider-contrib', 'value'), Input('radio-tax', 'value'), Input('dropdown-risk', 'value'),
     Input('slider-mort-loan', 'value'), Input('slider-mort-rate', 'value'), Input('slider-mort-years', 'value'), Input('radio-mort-type', 'value'),
     Input('slider-ins-debt', 'value'), Input('slider-ins-inc', 'value'), Input('slider-ins-years', 'value'), Input('slider-ins-have', 'value'),
     Input('btn-mode-wealth', 'n_clicks'), Input('btn-mode-mort', 'n_clicks'), Input('btn-mode-ins', 'n_clicks'), Input('btn-toggle-tools', 'n_clicks'), Input('url', 'pathname'), Input('vault-signal', 'data')
], 

[
    State('user-input', 'value'), 
    State('chat-window', 'children'), 
    State('active-mode', 'data'),
    
]) 
                   
                 

def master_control(tab_val, btn_launch, btn_send, enter_key, btn_connect, lang, age_now, age_retire, contrib, tax_type, risk_profile,mort_loan, mort_rate, mort_years, mort_type,
                   ins_debt, ins_inc, ins_years, ins_have, btn_wealth, btn_mort, btn_ins,btn_toggle, pathname, vault_msg, input_val, history, current_mode):
                   
    # 📡 SONAR PING 1: Check if the function woke up!
    print("🚨 SONAR 1: master_control triggered!", flush=True)

    t = TRANSLATIONS[lang]
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'none'
    
    # 📡 SONAR PING 2: What triggered us?
    print(f"🚨 SONAR 2: Triggered by: {trigger_id}", flush=True)

    # ... Your fallback defaults (risk_profile, age_now, etc) ...
     # --- [V96 FIX] SAFETY DEFAULTS (PREVENT "NONETYPE" CRASHES) ---
    # This ensures that if the app is loading and inputs are "None", we use a safe fallback.
   # --- [V99 FIX] THE NUMERIC ARMOR (BUSTING THE GHOST) ---
    # --- THE ULTIMATE GHOSTBUSTER (Bulletproof Variables) ---
    # 1. Force dropdowns to never be blank
    
    risk_profile = risk_profile if risk_profile else 'Balanced'
    tax_type = tax_type if tax_type else 'TFSA'

    try:
       # 2. Force every number to be a strict integer or float (Catching 'None' safely)
        age_now = int(float(age_now)) if age_now is not None else 30
        age_retire = int(float(age_retire)) if age_retire is not None else 65
        contrib = float(contrib) if contrib is not None else 500.0

        mort_loan = float(mort_loan) if mort_loan is not None else 500000.0
        mort_rate = float(mort_rate) if mort_rate is not None else 5.0
        mort_years = int(float(mort_years)) if mort_years is not None else 25

        ins_debt = float(ins_debt) if ins_debt is not None else 0.0
        ins_inc = float(ins_inc) if ins_inc is not None else 0.0
        ins_years = int(float(ins_years)) if ins_years is not None else 0
        ins_have = float(ins_have) if ins_have is not None else 0.0
        # ---------------------------------------------------------
    except (ValueError, TypeError):
        # Fallbacks just in case the browser sends complete garbage data
        age_now, age_retire, contrib = 30, 65, 500
        mort_loan, mort_rate, mort_years = 500000, 5.0, 25
        ins_debt, ins_inc, ins_years, ins_have = 0, 0, 0, 0
    # ---------------------------------------------------------

    t = TRANSLATIONS[lang]
    t = TRANSLATIONS[lang]
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'none'
    
    # 🔨 THE OVERRIDE: Set defaults BEFORE the Welcome Mat runs!
    out_chat, out_input = dash.no_update, dash.no_update 

    # 📡 SONAR PING 3: Checking the Bouncers!
    print("🚨 SONAR 3: Hitting Bouncer 1 (history)...", flush=True)
    if isinstance(history, dict):
        history = [history]
    elif not history:
        history = []
        
    #print("🚨 SONAR 4: Hitting Bouncer 2 (audit_log)...", flush=True)
    #if isinstance(audit_log, dict):
        #audit_log = [audit_log]
    #elif not audit_log:
        #audit_log = [html.Div("System Ready.")]

    # 📡 SONAR PING 5: We survived the Bouncers!
    print("🚨 SONAR 5: Bouncers cleared! Checking User Input Logic...", flush=True)
    
    # 🪤 THE GHOST TRAP: Wrap the entire rest of the function!
    try:
        active_tab = 'tab-app' if trigger_id == 'btn-launch-rose' else tab_val
        
        HOME_STYLE = {'maxWidth': '800px', 'margin': '40px auto', 'textAlign': 'center', 'padding': '20px'}
        home_style = dict(HOME_STYLE, display='block') if active_tab == 'tab-home' else {'display': 'none'}
        app_style = {'display': 'none'} if active_tab == 'tab-home' else {'display': 'block'}

        # [V77] TOGGLE LOGIC
        tools_visible = True
        if btn_toggle and (btn_toggle % 2 == 0): tools_visible = False
        
        tools_style = {'flex': '1', 'minWidth': '300px', 'display': 'block' if tools_visible else 'none'}
        toggle_text = t['btn_toggle'] if not tools_visible else ("✖ " + t['btn_toggle'].split(' ')[-1])


    # --- TARGET B: THE AGGRESSIVE WELCOME MAT ---
        # 🧠 NEW: If the user is NOT actively sending a chat message...
        # 📡 SONAR 6: If we reach this, there are zero math or logic errors!
        print("🚨 SONAR 6: All logic passed! Preparing to send to UI...", flush=True)
        # --- THE CHAT & PROACTIVE ROSE LOGIC ---
        # 1. Handle Brand New Page Loads (Fixing the Blank Chat!)
        if not history or len(history) == 0:
            welcome_msg = "Welcome to FazGem. I am Rose, your AI Financial Guardian. How can I assist you today?"
            history = [html.Div([dcc.Markdown(welcome_msg)], style={'padding': '15px', 'backgroundColor': '#ECEFF1', 'borderRadius': '10px 10px 10px 0', 'color': '#263238', 'marginBottom': '15px'})]
        
        # 2. Handle Slider Adjustments (Making Rose Proactive!)
        if trigger_id and (trigger_id.startswith('slider-') or trigger_id == 'dropdown-risk'):
            if current_mode == 'wealth':
                proactive_msg = f"*(Rose notes the change)*: I see you are exploring a **{risk_profile}** strategy at **${contrib}/mo**. Would you like me to analyze this scenario?"
            elif current_mode == 'mortgage':
                proactive_msg = f"*(Rose notes the change)*: I see you are looking at a **${mort_loan:,.0f}** mortgage over **{mort_years}** years. Shall we run the numbers?"
            else:
                proactive_msg = f"*(Rose notes the change)*: I am tracking your adjustments. Let me know when you're ready for my analysis."
            
            # Instantly inject Rose's proactive message at the TOP of the chat window
            new_bubble = html.Div([dcc.Markdown(proactive_msg)], style={'padding': '15px', 'backgroundColor': '#E8F5E9', 'border': '1px solid #81C784', 'borderRadius': '10px 10px 10px 0', 'color': '#1B5E20', 'marginBottom': '15px'})
            history = [new_bubble] + history
            
        out_chat = history
        # ----------------------------------------
            
        msg_switch = None
        if trigger_id == 'btn-mode-wealth': 
            current_mode = 'wealth'
            msg_switch = t['msg_switch_wealth']
        elif trigger_id == 'btn-mode-mort': 
            current_mode = 'mortgage'
            msg_switch = t['msg_switch_mort']
        elif trigger_id == 'btn-mode-ins': 
            current_mode = 'insurance'
            msg_switch = t['msg_switch_ins']
        
        if msg_switch:
            rose_msg = html.Div([dcc.Markdown(msg_switch)], style={ "backgroundColor": "#ffffff",  "border": "1px solid #e2e8f0", "padding": "14px 20px", "borderRadius": "15px 15px 15px 0", "marginTop": "10px",  "maxWidth": "85%",  "color": "#0f172a", "fontFamily": "Segoe UI, Arial, sans-serif", "boxShadow": "0 2px 5px rgba(0,0,0,0.02)",  "wordWrap": "break-word"})
            history = history + [rose_msg]

        # [V85] PASS MORTGAGE TYPE TO CONTEXT
        w_data = {'risk': risk_profile, 'contrib': contrib}
        m_data = {'loan': mort_loan, 'rate': mort_rate, 'type': mort_type}
        i_data = {'gap': max(0, ((ins_debt or 0) + ((ins_inc or 0) * (ins_years or 0))) - (ins_have or 0))}

       
        # --- PROACTIVE VAULT MESSAGE ---
        if trigger_id == 'vault-signal' and vault_msg:
            # 🛡️ THE TITANIUM WIRE: Safely read the signal
            if isinstance(vault_msg, dict):
                actual_text = vault_msg.get('text', '')
            else:
                actual_text = str(vault_msg)
                
            # 💊 THE ANTIDOTE: We wrapped the text in an [ html.P(...) ] array so React never crashes!
            new_bubble = html.Div(
                [html.P(actual_text, style={'margin': 0, 'lineHeight': '1.5'})], 
                style={ "backgroundColor": "#ffffff",  "border": "1px solid #e2e8f0", "padding": "14px 20px", "borderRadius": "15px 15px 15px 0", "marginTop": "10px",  "maxWidth": "85%",  "color": "#0f172a", "fontFamily": "Segoe UI, Arial, sans-serif", "boxShadow": "0 2px 5px rgba(0,0,0,0.02)",  "wordWrap": "break-word"})
            
            # 🔨 Safely combine the lists
            history = list(history) + [new_bubble] 
            out_chat = history

    # 🧠 THE SMART RESET: Only ignore the chat if we aren't actively building a Welcome Mat or sending a message
        if trigger_id not in ['btn-launch-rose', 'send-button', 'user-input', 'vault-signal']:
            out_chat = dash.no_update
            
        # Always clear the input box after a message is sent
        # 🎯 TRACER: Is the Send Button even reaching the server?
        if trigger_id in ['send-button', 'user-input']:
            print(f"🚨 SEND BUTTON CLICKED! Input value is: '{input_val}'", flush=True)
        else:
            out_input = dash.no_update
        
          # 🛡️ THE TITANIUM GATE: Only proceed if there is actual text (ignoring blank spaces)
        if (trigger_id == 'send-button' or trigger_id == 'user-input') and input_val and input_val.strip():
            
            # 1. 🛡️ INTERCEPT THE DATA LOCALLY FIRST
            safe_text, shield_activated = local_edge_shield_intercept(input_val.strip())
            
            # 2. 🎨 DYNAMIC UI RENDERING
            if shield_activated:
                # If shielded, turn the bubble Crimson Red and add the warning badge
                bg_color = "#7f1d1d" 
                text_color = "#ffffff"
                shield_badge = html.Span("🛡️ LOCAL EDGE SHIELD ACTIVE\n\n", style={"fontWeight": "bold", "fontSize": "11px", "color": "#fca5a5", "display": "block"})
                display_text = safe_text # Show the masked text (████) in the bubble
            else:
                # Normal user message (Deep Blue)
                bg_color = "#1e3a8a"
                text_color = "#ffffff"
                shield_badge = ""
                display_text = input_val.strip()

            user_msg = html.Div(
                style={"backgroundColor": bg_color, "padding": "12px 18px", "borderRadius": "15px 15px 0 15px", "marginLeft": "auto", "maxWidth": "80%", "color": text_color, "wordWrap": "break-word"},
                children=[shield_badge, html.P(display_text, style={"margin": "0", "whiteSpace": "pre-wrap"})]
            )
            
            history_with_user = history + [html.Div(style={'height': '15px'}), user_msg]
            
            # [V83] EXPLAINABLE AI LOGIC
            # 🎯 TRACER BULLETS: Prove the API is the bottleneck!
            print(f"🎯 TRACER: Sending '{safe_text}' to Rose API...", flush=True) 
            
            try:
                # 🛡️ THE SAFETY NET: Try to call the API (Note: we pass safe_text instead of input_val)
                resp_full, reas, log_type, new_mode = get_rose_response(safe_text, current_mode, lang, w_data, m_data, i_data)
                
            except Exception as e:
                # 🛑 IF THE API CRASHES OR HANGS, CATCH IT AND PREVENT THE UI FROM FREEZING!
                print(f"🛑 TRACER FATAL ERROR: API Connection Failed! Details: {str(e)}")
                resp_full = "⚠️ **Connection Error:** I could not reach the server. Please check your API keys and backend logs.|||Error details logged in terminal."
                reas = "API Offline"
                log_type = "System Error"
                new_mode = current_mode
            current_mode = new_mode
            
            if "|||" in resp_full:
                part_summary, part_details = resp_full.split("|||", 1)
            else:
                part_summary, part_details = resp_full, ""

            bubble_content = [dcc.Markdown(part_summary.strip())]
            if part_details:
                bubble_content.append(html.Details([
                    html.Summary(t['lbl_read_more'], style={'cursor': 'pointer', 'color': '#1565C0', 'marginTop': '10px', 'fontWeight': 'bold'}),
                    html.Div(dcc.Markdown(part_details.strip()), style={'marginTop': '10px', 'fontSize': '0.9em', 'borderTop': '1px solid #CFD8DC', 'paddingTop': '10px'})
                ]))

            rose_msg = html.Div(bubble_content, style={'backgroundColor': '#ECEFF1', 'padding': '15px', 'borderRadius': '15px 15px 15px 0', 'marginTop': '10px', 'maxWidth': '85%', 'color': NAVY, 'wordWrap': 'break-word'})
            
            history = history_with_user + [rose_msg]
            # 🔨 FIX: Create a brand new list for the Audit Log to prevent React freezes!
            #new_log = html.Div(f"[{datetime.datetime.now().strftime('%H:%M')}] {log_type}: {reas}")
            #audit_log = [new_log] + audit_log
            out_chat, out_input = history, ""
        
        if trigger_id == 'connect-btn':
            if current_mode == 'fraud':
                # Don't call the API! Just give a local warning.
                rose_msg = html.Div([dcc.Markdown("🚨 **Fraud Reporting:** Please use the official government links provided in the Fraud Shield panel above to report this incident immediately.")], style={'backgroundColor': '#FFEBEE', 'padding': '15px', 'borderRadius': '15px 15px 15px 0', 'marginTop': '10px', 'color': '#C62828'})
            else:
                # Call the API for normal Advisor handoffs
                resp, reas, log_type, new_mode = get_rose_response("connect", current_mode, lang, w_data, m_data, i_data)
                rose_msg = html.Div([dcc.Markdown(resp)], style={ "backgroundColor": "#ffffff",  "border": "1px solid #e2e8f0", "padding": "14px 20px", "borderRadius": "15px 15px 15px 0", "marginTop": "10px",  "maxWidth": "85%",  "color": "#0f172a", "fontFamily": "Segoe UI, Arial, sans-serif", "boxShadow": "0 2px 5px rgba(0,0,0,0.02)",  "wordWrap": "break-word"})
            
            history = history + [rose_msg]
            out_chat = history
        
        BASE_PANEL = {'padding': '25px', 'borderRadius': '15px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)', 'transition': 'background-color 0.5s ease'}
        wealth_style, mort_style, ins_style, fraud_style = {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
        narrative_style = {'display': 'block', 'backgroundColor': '#FAFAFA', 'padding': '15px', 'borderRadius': '10px', 'marginTop': '15px', 'borderLeft': '4px solid #2E7D32'}
        
        # Update master_control logic for added Compliance Mode:
      # --- THE COMPLIANCE HIJACK ---
        if current_mode == 'compliance':
            # 1. Hide ALL standard tools
            wealth_style = mort_style = ins_style = fraud_style = {'display': 'none'}
            
            # 2. Use the story_markdown to hold the entire War Room UI
            # This 'injects' the workspace into your existing narrative-box
            story_markdown = render_compliance_workspace(lang)
            
            # 3. Clean up the rest
            fig = px.bar(x=[0], y=[0]) # Empty graph
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis={'visible':False}, yaxis={'visible':False})
            btn_label = "ADVISOR PORTAL ACTIVE"
            panel_style = dict(BASE_PANEL, backgroundColor='#F5F5F5')
        
        if current_mode == 'fraud':
            fraud_style = {'display': 'block'}
            narrative_style['display'] = 'none'
            fig, story_markdown = px.bar(x=[0], y=[0]), ""
            btn_label = "⚠ REPORT"
            panel_style = dict(BASE_PANEL, backgroundColor='#FFEBEE')
        elif current_mode == 'insurance':
            ins_style = {'display': 'block'}
            btn_label = t['btn_connect_ins']
            narrative_style['borderLeft'] = '4px solid #C62828'
            story_markdown = dcc.Markdown(generate_insurance_story(i_data['gap'], lang))
            fig = px.bar(x=[t['lbl_ins_have'].split(':')[0], "Need"], y=[ins_have, ((ins_debt or 0) + ((ins_inc or 0) * (ins_years or 0)))], 
                        color=["Have", "Need"], color_discrete_map={"Have": "#66BB6A", "Need": "#EF5350"})
            fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            panel_style = dict(BASE_PANEL, backgroundColor='#FFEBEE')
        elif current_mode == 'mortgage':
            mort_style = {'display': 'block'}
            btn_label = t['btn_connect_mort']
            narrative_style['borderLeft'] = '4px solid #1565C0'
            r_m = (mort_rate or 5.0)/100/12
            n_p = int((mort_years or 25)*12) # <-- ADD int() HERE
            pmt = (mort_loan * (r_m * (1 + r_m)**n_p) / ((1 + r_m)**n_p - 1)) if r_m > 0 else mort_loan/n_p
            story_markdown = dcc.Markdown(generate_mortgage_story(pmt, pmt*n_p, (pmt*n_p)-mort_loan, lang))
            bal_arr = [max(0, mort_loan - (pmt - mort_loan*r_m)*i) for i in range(n_p+1)]
            fig = px.area(x=[i/12 for i in range(n_p+1)], y=bal_arr)
            fig.update_traces(line_color='#1565C0')
            fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            panel_style = dict(BASE_PANEL, backgroundColor='#E3F2FD')
        else:
            wealth_style = {'display': 'block'}
            btn_label = t['btn_connect_wealth']
            r = 0.06 if risk_profile == 'Balanced' else (0.04 if 'Conservative' in risk_profile else 0.08)
            
            # [OGOU FERAY'S ARMOR]: Force strict integers and prevent negative years
            safe_age_now = int(float(age_now or 30))
            safe_age_retire = int(float(age_retire or 65))
            safe_contrib = float(contrib or 500)
            
            years = max(0, safe_age_retire - safe_age_now)
            vals = [0]
            for _ in range(years): 
                vals.append((vals[-1] + (safe_contrib * 12)) * (1 + r))
                
            # Guarantee X and Y arrays are always the exact same length
            x_axis = [safe_age_now + i for i in range(len(vals))]
            
            story_markdown = dcc.Markdown(generate_wealth_story(safe_age_now, safe_age_retire, vals[-1], safe_contrib * 12 * years, lang))
            fig = px.area(x=x_axis, y=vals) 
            
            fig.update_traces(line_color='#2E7D32')
            fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            panel_style = dict(BASE_PANEL, backgroundColor='#F1F8E9')

            # --- THE MATRIX HIJACK (B2B MODE) ---
        if current_mode == 'compliance':
            # 1. Silence the consumer graphs
            wealth_style = mort_style = ins_style = fraud_style = {'display': 'none'}
            
            # 2. Inject the War Room into the narrative box
            story_markdown = render_compliance_workspace(lang)
            
            # 3. Reset the visual field
            fig = px.bar(x=[0], y=[0])
            fig.update_layout(xaxis={'visible':False}, yaxis={'visible':False}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            panel_style = dict(BASE_PANEL, backgroundColor='#F5F5F5') # Neutral Pro Gray

       # 🧠 THE FIX: Changed 'color': NAVY to 'color': WHITE so you can actually read it!
       # THE FIX: Hardcoded '#FFFFFF' guarantees the text is brilliant white against the navy background.
        home_steps_content = [html.P(dcc.Markdown(step), style={'fontSize': '1.1em', 'marginBottom': '15px', 'color': '#2C3E50'}) for step in t['how_it_works']]
        risk_opts = [{'label': '🛡️ '+('Prudent' if lang=='fr' else 'Safe'), 'value': 'Conservative'}, {'label': '⚖️ '+('Équilibré' if lang=='fr' else 'Balanced'), 'value': 'Balanced'}, {'label': '🚀 '+('Audacieux' if lang=='fr' else 'Growth'), 'value': 'Aggressive'}]
        
        # [V85] FIXED FRENCH LOGIC
        tax_opts = [{'label': t['lbl_tax_opt_reg'], 'value': 'TFSA'}, {'label': t['lbl_tax_opt_non'], 'value': 'TAXED'}]

        # --- 🛡️ THE DOM SHIELD (THE ULTIMATE GHOST TRAP) ---
        # If the user is adjusting a slider or dropdown, DO NOT rebuild the UI containers.
        # This prevents React from destroying the DOM, stopping slider freezes and dropdown blanks!
        if trigger_id.startswith('slider-') or trigger_id == 'dropdown-risk' or trigger_id.startswith('radio-'):
            wealth_style = mort_style = ins_style = fraud_style = dash.no_update
            #risk_opts = tax_opts = dash.no_update
            panel_style = tools_style = narrative_style = dash.no_update
            home_style = app_style = active_tab = dash.no_update
            btn_label = toggle_text = home_steps_content = dash.no_update
        # ---------------------------------------------------
        return (active_tab, home_style, app_style, out_chat, out_input, current_mode, wealth_style, mort_style, ins_style, fraud_style, fig, {'display': 'block'}, story_markdown, narrative_style,
                t['hero_title'], t['hero_sub'], t['btn_start'], home_steps_content, "", 
                t['lbl_risk'], f"{t['lbl_age']} {age_now}", f"{t['lbl_retire']} {age_retire}", f"{t['lbl_contrib']} ${contrib}", t['lbl_tax'], btn_label, 
                t['lbl_wealth_engine'], 
                t['lbl_mortgage_engine'], f"{t['lbl_loan']} ${mort_loan:,.0f}", f"{t['lbl_rate']} {mort_rate}%", f"{t['lbl_years']} {mort_years}y",
                t['lbl_ins_engine'], f"{t['lbl_ins_debt']} ${ins_debt:,.0f}", f"{t['lbl_ins_inc']} ${ins_inc:,.0f}", f"{t['lbl_ins_years']} {ins_years}y", f"{t['lbl_ins_have']} ${ins_have:,.0f}",
                t['lbl_fraud_engine'], t['fraud_checklist'],
                t['btn_send'], risk_opts, tax_opts,
                panel_style, tools_style, toggle_text, t['lbl_rate_type'])
    
    # 🚨 IF ANYTHING CRASHES, CATCH IT AND SQUEAL!
    except Exception as e:
        import traceback
        print(f"🛑 GHOST CAUGHT! Fatal Python Crash: {str(e)}", flush=True)
        print(traceback.format_exc(), flush=True) # This prints the EXACT line number!
        raise e # Let it crash, but now we have the evidence!
    
# --- THE WIZARD OF OZ: EDGE COMPUTE ILLUSION ---
@app.callback(
    [Output('upload-status', 'children'),
     Output('vault-signal', 'data')], 
    Input('upload-data', 'contents'),
    [State('upload-data', 'filename'),
     State('lang-toggle', 'value')],
    prevent_initial_call=True
)
def handle_file_upload(contents, filename, lang):
    if contents is None: return dash.no_update, dash.no_update
    
    import time
    # THE ILLUSION: Fake an 8-second edge-compute processing delay
    time.sleep(8) 
    
    # THE REVEAL: Hardcoded dummy data for Dr. Ezechiel-Markus
    header_text = "✅ EDGE COMPUTE: Document Masked & Parsed Locally"
    
    reply_markdown = """
    **Zero-Trust Edge Masking Complete.**
    PII (Name, SIN) has been quarantined. No raw data left the device.

    ### Extracted T5 Data (Ready for CRM):
    * **Payer Name:** Ezechiel-Markus Holdings Inc.
    * **Box 11 (Taxable Dividends):** $51,750.00
    * **Box 24 (Eligible Dividends):** $80,000.00
    * **Box 25 (Taxable Eligible):** $110,400.00
    """

    # Assemble the side-by-side success screen with the masked image
    vault_div = html.Div([
        html.H4(header_text, style={'color': '#2E7D32', 'marginTop': '0', 'borderBottom': '1px solid #C8E6C9', 'paddingBottom': '10px'}),
        html.Div([
            # Displaying the image from your local assets folder!
            #html.Img(src='/assets/Masked_T5.jpg', style={'width': '45%', 'border': '1px solid #ccc', 'marginRight': '5%', 'borderRadius': '8px'}),
            html.Div(dcc.Markdown(reply_markdown), style={'width': '50%', 'color': '#37474F'})
        ], style={'display': 'flex', 'alignItems': 'flex-start'})
    ], style={'backgroundColor': '#F1F8E9', 'padding': '20px', 'borderRadius': '10px', 'border': '1px solid #C8E6C9', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)', 'marginBottom': '20px'})
    
    # Trigger Rose to speak in the chat window
    proactive_msg = "I have successfully processed the document locally on the edge. PII is masked, and the financial data is ready for your CRM."
    signal_payload = {'text': proactive_msg, 'ts': time.time()}
    
    return vault_div, signal_payload

# --- B2B MODE SWITCHER (THE SECRET HANDSHAKE) ---
@app.callback(
    Output('lbl-audit', 'children'),
    Input('btn-secret-b2b', 'n_clicks'),
    State('active-mode', 'data'),
    prevent_initial_call=True
)
def toggle_mode(n_clicks, current_mode):
    # This responds to the Briefcase button (Line 274)
    if n_clicks is None:
        return 'wealth'
    
    # Flip the switch!
    new_mode = 'compliance' if current_mode == 'wealth' else 'wealth'
    
    # This print will show up in your VS Code terminal so you can see it working
    print(f"--- MATRIX UPDATE: Switched to {new_mode.upper()} ---")
    return new_mode
    
    # --- SECRET B2B PORTAL TOGGLE ---
# --- MICRO-CALLBACK: BILINGUAL DRAG & DROP TEXT ---
@app.callback(
    Output('upload-text', 'children'),
    Input('lang-toggle', 'value')
)
def update_vault_text(lang):
    if lang == 'fr':
        return '📂 Glissez et déposez votre document (PDF, Image, CSV) ici'
    return '📂 Drag and Drop your Document (PDF, Image, CSV) here'

@app.callback(
    Output('b2b-modal', 'style'),
    [Input('btn-secret-b2b', 'n_clicks'), Input('btn-close-b2b', 'n_clicks')],
    State('b2b-modal', 'style'),
    prevent_initial_call=True
)
def toggle_b2b_portal(open_clicks, close_clicks, current_style):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'btn-secret-b2b':
        # Turn it ON
        return dict(current_style, display='block')
    elif trigger_id == 'btn-close-b2b':
        # Turn it OFF
        return dict(current_style, display='none')
    
    return current_style

if __name__ == '__main__':
    app.run(debug=True)
    