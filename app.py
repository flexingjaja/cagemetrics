import streamlit as st
import requests
from bs4 import BeautifulSoup
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Pro", page_icon="⚡", layout="centered")

# --- 2. SESSION & LANGUE ---
if 'lang' not in st.session_state: st.session_state.lang = 'fr'
def toggle(): st.session_state.lang = 'en' if st.session_state.lang == 'fr' else 'fr'

T = {
    "fr": { 
        "sub": "Intelligence Artificielle de Prédiction MMA", 
        "btn": "LANCER L'ANALYSE TACTIQUE", "win": "VAINQUEUR PRÉDIT", "conf": "INDICE DE CONFIANCE", 
        "meth": "SCÉNARIO DU COMBAT", 
        "tech": "COMPARATIF TECHNIQUE", "lbl": ["Taille", "Allonge", "Frappes/min", "Précision", "Takedowns/15m", "Déf. Lutte"], 
        "cta": "VOIR LA COTE DE", "err": "Veuillez sélectionner deux combattants différents.",
        "keys": "CLÉS DU COMBAT", "adv": "Avantage", "more_acc": "Plus Précis", "more_vol": "Volume Supérieur", "grap_adv": "Menace Lutte", "phys_adv": "Avantage Allonge"
    },
    "en": { 
        "sub": "AI-Powered MMA Predictive Analytics", 
        "btn": "RUN TACTICAL ANALYSIS", "win": "PREDICTED WINNER", "conf": "CONFIDENCE SCORE", 
        "meth": "FIGHT SCENARIO", 
        "tech": "TECHNICAL BREAKDOWN", "lbl": ["Height", "Reach", "Strikes/min", "Accuracy", "Takedowns/15m", "Takedown Def"], 
        "cta": "SEE ODDS FOR", "err": "Please select two different fighters.",
        "keys": "KEY FACTORS", "adv": "Advantage", "more_acc": "More Accurate", "more_vol": "Higher Volume", "grap_adv": "Grappling Threat", "phys_adv": "Reach Advantage"
    }
}
txt = T[st.session_state.lang]

# --- 3. DATA BASE (TOP TIER) ---
DB = {
    "Jon Jones": {"Cat": "HW", "Taille": "6' 4\"", "Allonge": "84\"", "Coups": 4.30, "TD": 1.85, "DefLutte": 95, "Preci": 58},
    "Tom Aspinall": {"Cat": "HW", "Taille": "6' 5\"", "Allonge": "78\"", "Coups": 7.72, "TD": 3.50, "DefLutte": 100, "Preci": 66},
    "Ciryl Gane": {"Cat": "HW", "Taille": "6' 4\"", "Allonge": "81\"", "Coups": 5.11, "TD": 0.60, "DefLutte": 45, "Preci": 59},
    "Stipe Miocic": {"Cat": "HW", "Taille": "6' 4\"", "Allonge": "80\"", "Coups": 4.82, "TD": 1.86, "DefLutte": 70, "Preci": 53},
    "Alexander Volkov": {"Cat": "HW", "Taille": "6' 7\"", "Allonge": "80\"", "Coups": 5.10, "TD": 0.60, "DefLutte": 75, "Preci": 57},
    "Sergei Pavlovich": {"Cat": "HW", "Taille": "6' 3\"", "Allonge": "84\"", "Coups": 8.20, "TD": 0.00, "DefLutte": 75, "Preci": 48},
    "Curtis Blaydes": {"Cat": "HW", "Taille": "6' 4\"", "Allonge": "80\"", "Coups": 3.50, "TD": 5.80, "DefLutte": 33, "Preci": 50},
    "Jailton Almeida": {"Cat": "HW", "Taille": "6' 3\"", "Allonge": "79\"", "Coups": 2.50, "TD": 6.40, "DefLutte": 75, "Preci": 55},
    "Alex Pereira": {"Cat": "LHW", "Taille": "6' 4\"", "Allonge": "79\"", "Coups": 5.10, "TD": 0.20, "DefLutte": 70, "Preci": 62},
    "Jiri Prochazka": {"Cat": "LHW", "Taille": "6' 3\"", "Allonge": "80\"", "Coups": 5.75, "TD": 0.60, "DefLutte": 68, "Preci": 56},
    "Magomed Ankalaev": {"Cat": "LHW", "Taille": "6' 3\"", "Allonge": "75\"", "Coups": 3.60, "TD": 1.10, "DefLutte": 86, "Preci": 53},
    "Jan Blachowicz": {"Cat": "LHW", "Taille": "6' 2\"", "Allonge": "78\"", "Coups": 3.41, "TD": 1.15, "DefLutte": 70, "Preci": 49},
    "Jamahal Hill": {"Cat": "LHW", "Taille": "6' 4\"", "Allonge": "79\"", "Coups": 7.31, "TD": 0.00, "DefLutte": 65, "Preci": 54},
    "Khalil Rountree Jr.": {"Cat": "LHW", "Taille": "6' 1\"", "Allonge": "76\"", "Coups": 3.80, "TD": 0.00, "DefLutte": 58, "Preci": 39},
    "Dricus Du Plessis": {"Cat": "MW", "Taille": "6' 1\"", "Allonge": "76\"", "Coups": 6.49, "TD": 2.72, "DefLutte": 55, "Preci": 50},
    "Sean Strickland": {"Cat": "MW", "Taille": "6' 1\"", "Allonge": "76\"", "Coups": 5.82, "TD": 1.00, "DefLutte": 85, "Preci": 41},
    "Israel Adesanya": {"Cat": "MW", "Taille": "6' 4\"", "Allonge": "80\"", "Coups": 3.90, "TD": 0.10, "DefLutte": 77, "Preci": 49},
    "Robert Whittaker": {"Cat": "MW", "Taille": "6' 0\"", "Allonge": "73\"", "Coups": 4.50, "TD": 0.80, "DefLutte": 82, "Preci": 42},
    "Nassourdine Imavov": {"Cat": "MW", "Taille": "6' 3\"", "Allonge": "75\"", "Coups": 4.60, "TD": 1.10, "DefLutte": 76, "Preci": 54},
    "Khamzat Chimaev": {"Cat": "MW", "Taille": "6' 2\"", "Allonge": "75\"", "Coups": 5.72, "TD": 4.00, "DefLutte": 100, "Preci": 59},
    "Caio Borralho": {"Cat": "MW", "Taille": "6' 1\"", "Allonge": "75\"", "Coups": 2.90, "TD": 2.10, "DefLutte": 65, "Preci": 60},
    "Belal Muhammad": {"Cat": "WW", "Taille": "5' 11\"", "Allonge": "72\"", "Coups": 4.55, "TD": 2.20, "DefLutte": 93, "Preci": 43},
    "Leon Edwards": {"Cat": "WW", "Taille": "6' 0\"", "Allonge": "74\"", "Coups": 2.80, "TD": 1.25, "DefLutte": 70, "Preci": 53},
    "Kamaru Usman": {"Cat": "WW", "Taille": "6' 0\"", "Allonge": "76\"", "Coups": 4.46, "TD": 2.82, "DefLutte": 97, "Preci": 52},
    "Shavkat Rakhmonov": {"Cat": "WW", "Taille": "6' 1\"", "Allonge": "77\"", "Coups": 4.45, "TD": 1.49, "DefLutte": 100, "Preci": 59},
    "Jack Della Maddalena": {"Cat": "WW", "Taille": "5' 11\"", "Allonge": "73\"", "Coups": 7.20, "TD": 0.30, "DefLutte": 67, "Preci": 53},
    "Ian Machado Garry": {"Cat": "WW", "Taille": "6' 3\"", "Allonge": "74\"", "Coups": 6.67, "TD": 0.00, "DefLutte": 69, "Preci": 56},
    "Colby Covington": {"Cat": "WW", "Taille": "5' 11\"", "Allonge": "72\"", "Coups": 4.00, "TD": 4.05, "DefLutte": 79, "Preci": 39},
    "Islam Makhachev": {"Cat": "LW", "Taille": "5' 10\"", "Allonge": "70\"", "Coups": 2.46, "TD": 3.17, "DefLutte": 90, "Preci": 60},
    "Arman Tsarukyan": {"Cat": "LW", "Taille": "5' 7\"", "Allonge": "72\"", "Coups": 3.80, "TD": 3.40, "DefLutte": 75, "Preci": 48},
    "Charles Oliveira": {"Cat": "LW", "Taille": "5' 10\"", "Allonge": "74\"", "Coups": 3.50, "TD": 2.30, "DefLutte": 55, "Preci": 53},
    "Justin Gaethje": {"Cat": "LW", "Taille": "5' 11\"", "Allonge": "70\"", "Coups": 7.35, "TD": 0.13, "DefLutte": 75, "Preci": 60},
    "Dustin Poirier": {"Cat": "LW", "Taille": "5' 9\"", "Allonge": "72\"", "Coups": 5.45, "TD": 1.36, "DefLutte": 63, "Preci": 51},
    "Michael Chandler": {"Cat": "LW", "Taille": "5' 8\"", "Allonge": "71\"", "Coups": 5.10, "TD": 1.70, "DefLutte": 71, "Preci": 45},
    "Benoit Saint Denis": {"Cat": "LW", "Taille": "5' 11\"", "Allonge": "73\"", "Coups": 5.70, "TD": 4.55, "DefLutte": 68, "Preci": 54},
    "Dan Hooker": {"Cat": "LW", "Taille": "6' 0\"", "Allonge": "75\"", "Coups": 4.90, "TD": 0.90, "DefLutte": 80, "Preci": 48},
    "Conor McGregor": {"Cat": "LW", "Taille": "5' 9\"", "Allonge": "74\"", "Coups": 5.32, "TD": 0.67, "DefLutte": 66, "Preci": 49},
    "Paddy Pimblett": {"Cat": "LW", "Taille": "5' 10\"", "Allonge": "73\"", "Coups": 4.20, "TD": 1.80, "DefLutte": 56, "Preci": 46},
    "Ilia Topuria": {"Cat": "FW", "Taille": "5' 7\"", "Allonge": "69\"", "Coups": 4.40, "TD": 1.92, "DefLutte": 92, "Preci": 46},
    "Max Holloway": {"Cat": "FW", "Taille": "5' 11\"", "Allonge": "69\"", "Coups": 7.17, "TD": 0.30, "DefLutte": 84, "Preci": 48},
    "Alexander Volkanovski": {"Cat": "FW", "Taille": "5' 6\"", "Allonge": "71\"", "Coups": 6.19, "TD": 1.84, "DefLutte": 70, "Preci": 57},
    "Brian Ortega": {"Cat": "FW", "Taille": "5' 8\"", "Allonge": "69\"", "Coups": 4.19, "TD": 0.95, "DefLutte": 57, "Preci": 38},
    "Yair Rodriguez": {"Cat": "FW", "Taille": "5' 11\"", "Allonge": "71\"", "Coups": 4.63, "TD": 0.73, "DefLutte": 59, "Preci": 45},
    "Movsar Evloev": {"Cat": "FW", "Taille": "5' 7\"", "Allonge": "72\"", "Coups": 4.50, "TD": 4.70, "DefLutte": 71, "Preci": 49},
    "Diego Lopes": {"Cat": "FW", "Taille": "5' 11\"", "Allonge": "72\"", "Coups": 3.20, "TD": 1.00, "DefLutte": 45, "Preci": 52},
    "Merab Dvalishvili": {"Cat": "BW", "Taille": "5' 6\"", "Allonge": "68\"", "Coups": 4.50, "TD": 6.50, "DefLutte": 80, "Preci": 45},
    "Sean O'Malley": {"Cat": "BW", "Taille": "5' 11\"", "Allonge": "72\"", "Coups": 7.25, "TD": 0.40, "DefLutte": 65, "Preci": 61},
    "Petr Yan": {"Cat": "BW", "Taille": "5' 7\"", "Allonge": "67\"", "Coups": 5.03, "TD": 1.70, "DefLutte": 85, "Preci": 53},
    "Umar Nurmagomedov": {"Cat": "BW", "Taille": "5' 8\"", "Allonge": "69\"", "Coups": 4.80, "TD": 4.50, "DefLutte": 80, "Preci": 68},
    "Cory Sandhagen": {"Cat": "BW", "Taille": "5' 11\"", "Allonge": "70\"", "Coups": 5.33, "TD": 1.30, "DefLutte": 64, "Preci": 44},
    "Deiveson Figueiredo": {"Cat": "BW", "Taille": "5' 5\"", "Allonge": "68\"", "Coups": 3.00, "TD": 1.60, "DefLutte": 58, "Preci": 55},
    "Marlon Vera": {"Cat": "BW", "Taille": "5' 8\"", "Allonge": "70\"", "Coups": 4.30, "TD": 0.60, "DefLutte": 70, "Preci": 49},
    "Henry Cejudo": {"Cat": "BW", "Taille": "5' 4\"", "Allonge": "64\"", "Coups": 3.90, "TD": 2.00, "DefLutte": 90, "Preci": 45}
}

WEIGHT_MAP = ["BW", "FW", "LW", "WW", "MW", "LHW", "HW"]

def get_filtered_roster(category_code):
    if category_code == "ALL": return sorted(list(DB.keys()))
    try:
        idx = WEIGHT_MAP.index(category_code)
        allowed = [WEIGHT_MAP[i] for i in range(max(0, idx-1), min(len(WEIGHT_MAP), idx+2))]
    except: allowed = [category_code]
    return sorted([name for name, data in DB.items() if data['Cat'] in allowed])

# --- 4. HELPERS ---
def clean_num(val):
    if isinstance(val, (int, float)): return val
    try: return float(str(val).replace('%','').replace(' cm','').strip())
    except: return 0

def to_cm(imp):
    if not imp or imp=="N/A": return "-"
    try:
        p = imp.replace('"','').split("'")
        inches = int(p[0])*30.48 + (int(p[1]) if len(p)>1 and p[1] else 0)*2.54
        return f"{int(inches)} cm"
    except: return imp

def get_data(name):
    if name in DB:
        d = DB[name].copy(); d['Nom'] = name
        return d
    return None

def process_units(d, lang):
    if not d: return None
    new_d = d.copy()
    if lang == 'fr':
        new_d['Taille'] = to_cm(new_d['Taille'])
        try: new_d['Allonge'] = f"{int(float(new_d['Allonge'].replace('\"',''))*2.54)} cm"
        except: pass
    return new_d

# --- 5. ALGORITHME AVANCÉ ---
def advanced_algo(f1, f2):
    score = 0
    reasons = []
    
    # 1. STRIKING EFFECTIF (Volume x Précision) -> L'efficacité compte plus que le volume brut
    # Score d'efficacité (ex: 7.0 coups * 0.60 precision = 4.2 coups connectés/min)
    eff_1 = f1['Coups'] * (f1['Preci'] / 100.0)
    eff_2 = f2['Coups'] * (f2['Preci'] / 100.0)
    
    diff_eff = eff_1 - eff_2
    score += diff_eff * 10 # Poids important
    
    if diff_eff > 0.5: reasons.append(f"👊 {txt['more_acc']} ({f1['Nom']})")
    elif diff_eff < -0.5: reasons.append(f"👊 {txt['more_acc']} ({f2['Nom']})")
    
    # 2. LUTTE (Menace vs Défense)
    # Si F1 a un gros TD rate et F2 une mauvaise défense, gros avantage.
    threat_1 = f1['TD'] * ((100 - f2['DefLutte']) / 100.0)
    threat_2 = f2['TD'] * ((100 - f1['DefLutte']) / 100.0)
    
    diff_grap = threat_1 - threat_2
    score += diff_grap * 8 # Poids grappling
    
    if threat_1 > 1.5: reasons.append(f"🤼 {txt['grap_adv']} ({f1['Nom']})")
    elif threat_2 > 1.5: reasons.append(f"🤼 {txt['grap_adv']} ({f2['Nom']})")
    
    # 3. PHYSIQUE (Allonge)
    # Convertir allonge en cm pour comparer (approx 1 inch = 2.54)
    try:
        r1 = float(f1['Allonge'].replace('"',''))
        r2 = float(f2['Allonge'].replace('"',''))
        if r1 > r2 + 2: 
            score += 5
            reasons.append(f"📏 {txt['phys_adv']} (+{int((r1-r2)*2.54)}cm)")
        elif r2 > r1 + 2:
            score -= 5
            reasons.append(f"📏 {txt['phys_adv']} (+{int((r2-r1)*2.54)}cm)")
    except: pass

    # Normalisation Score (50 = 50/50)
    final_score = 50 + score
    final_score = max(10, min(90, final_score))
    
    # Calcul Finish
    violence = (eff_1 + eff_2) + (threat_1 + threat_2)*1.5
    finish_prob = min(95, 20 + violence * 8)
    
    # Répartition méthode
    strike_ratio = (eff_1 + eff_2) / max(0.1, (eff_1 + eff_2 + threat_1 + threat_2))
    ko = int(finish_prob * strike_ratio)
    sub = int(finish_prob * (1 - strike_ratio))
    dec = 100 - ko - sub
    
    return int(final_score), ko, sub, dec, reasons

# --- 6. CSS (CENTRÉ & CLEAN) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    .stApp { background-color: #0f172a; background-image: radial-gradient(at 50% 0%, rgba(46, 204, 113, 0.1) 0px, transparent 60%); font-family: 'Montserrat', sans-serif; }
    h1,h2,div,p{font-family:'Montserrat',sans-serif!important;}
    
    /* Centrage Logo & Titre */
    .header-container { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 20px; }
    .logo-img { max-height: 80px; margin-bottom: 10px; }
    
    /* Inputs sans cadre */
    .stSelectbox > div > div { background-color: transparent !important; border: none !important; }
    .stSelectbox div[data-baseweb="select"] > div { background-color: #1e293b !important; border: 1px solid rgba(255,255,255,0.1) !important; color: white !important; border-radius: 12px; }

    /* Cards */
    .glass-card { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); border-radius: 20px; padding: 24px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 10px 30px -5px rgba(0,0,0,0.4); margin-bottom: 20px; }
    
    div.stButton>button { background: #2ecc71!important; color: #020617!important; border-radius: 12px; padding: 18px; font-weight: 900; text-transform: uppercase; border: none; width: 100%; transition: 0.3s; }
    div.stButton>button:hover { transform: scale(1.02); }
    
    .bar-bg { width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; display: flex; margin-top: 5px; }
    .bar-l { height: 100%; background: #38bdf8; } .bar-r { height: 100%; background: #f43f5e; }
    .finish-cont { width: 100%; height: 14px; background: #1e293b; border-radius: 7px; overflow: hidden; display: flex; margin-top: 10px; }
    
    .reason-tag { background: rgba(255,255,255,0.1); padding: 5px 10px; border-radius: 8px; font-size: 0.75rem; color: #cbd5e1; display: inline-block; margin: 2px; border: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 7. UI ---

# HEADER CENTRÉ
c_empty, c_mid, c_lang = st.columns([1, 6, 1])
with c_mid:
    if os.path.exists("logo.png"):
        st.markdown(
            f"""
            <div class="header-container">
                <img src="data:image/png;base64,{st.image("logo.png", output_format="PNG")}" class="logo-img" style="display:none;"> </div>
            """, unsafe_allow_html=True
        )
        st.image("logo.png", width=300) # Simple Streamlit Image centree par colonne
    else:
        st.markdown("<h1 style='text-align:center; color:white;'>CAGEMETRICS <span style='color:#2ecc71'>PRO</span></h1>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-top:-10px;'>{txt['sub']}</div>", unsafe_allow_html=True)

with c_lang:
    if st.button("🇫🇷" if st.session_state.lang == 'en' else "🇺🇸"): toggle(); st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# INPUTS
cats_map = {"Heavyweight (HW)": "HW", "Light Heavyweight (LHW)": "LHW", "Middleweight (MW)": "MW", "Welterweight (WW)": "WW", "Lightweight (LW)": "LW", "Featherweight (FW)": "FW", "Bantamweight (BW)": "BW", "Show All": "ALL"}
cat_name = st.selectbox("", list(cats_map.keys()), label_visibility="collapsed")
cat_code = cats_map[cat_name]

filtered_roster = get_filtered_roster(cat_code)

c1,c2,c3=st.columns([1,0.1,1])
idx_a = 0
idx_b = 1 if len(filtered_roster) > 1 else 0
f_a = c1.selectbox("A", filtered_roster, index=idx_a, label_visibility="collapsed", key="fa")
c2.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:white;'>VS</div>",unsafe_allow_html=True)
f_b = c3.selectbox("B", filtered_roster, index=idx_b, label_visibility="collapsed", key="fb")

st.markdown("<br>", unsafe_allow_html=True)

# BOUTON CENTRÉ
col_x, col_y, col_z = st.columns([1, 4, 1])
with col_y:
    analyze = st.button(txt['btn'], use_container_width=True)

if analyze:
    if f_a==f_b: st.warning(txt['err'])
    else:
        with st.spinner("..."):
            raw_s1 = get_data(f_a)
            raw_s2 = get_data(f_b)
            s1 = process_units(raw_s1, st.session_state.lang)
            s2 = process_units(raw_s2, st.session_state.lang)
            
            if s1 and s2:
                sc,k,sb,d, reasons = advanced_algo(raw_s1, raw_s2) # Use raw data for calc
                w = s1['Nom'] if sc>=50 else s2['Nom']
                cf = sc if sc>=50 else 100-sc
                
                # 1. WINNER
                st.markdown(f"""<div class="glass-card" style="text-align:center; border:2px solid #2ecc71; background:rgba(46, 204, 113, 0.05);"><div style="color:#94a3b8; font-size:0.7rem; font-weight:700; letter-spacing:1px; margin-bottom:5px;">{txt['win']}</div><div style="font-size:2.5rem; font-weight:900; color:white; line-height:1; margin-bottom:10px; text-transform:uppercase;">{w}</div><span style="background:#2ecc71; color:#020617; padding:4px 12px; border-radius:20px; font-weight:800; font-size:0.8rem;">{cf}% {txt['conf']}</span></div>""",unsafe_allow_html=True)
                
                # 2. TACTICAL KEYS (ARGUMENTS)
                if reasons:
                    html_reasons = "".join([f"<span class='reason-tag'>{r}</span>" for r in reasons])
                    st.markdown(f"""<div class="glass-card"><div style="text-align:center; font-weight:800; color:white; margin-bottom:10px;">{txt['keys']}</div><div style="text-align:center;">{html_reasons}</div></div>""", unsafe_allow_html=True)

                # 3. SCENARIO
                st.markdown(f"""<div class="glass-card"><div style="text-align:center; font-weight:800; color:white;">{txt['meth']}</div><div class="finish-cont"><div style="width:{k}%; background:#ef4444;"></div><div style="width:{sb}%; background:#eab308;"></div><div style="width:{d}%; background:#3b82f6;"></div></div><div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.7rem; font-weight:700;"><span style="color:#ef4444">KO/TKO {k}%</span><span style="color:#eab308">SUB {sb}%</span><span style="color:#3b82f6">DEC {d}%</span></div></div>""",unsafe_allow_html=True)
                
                # 4. TECH
                st.markdown(f'<div class="glass-card"><div style="text-align:center; color:#94a3b8; font-weight:700; margin-bottom:15px;">{txt["tech"]}</div>',unsafe_allow_html=True)
                def stat_vis(l,v1,v2):
                    n1=clean_num(v1); n2=clean_num(v2); tot=max(n1+n2,0.1); p1=(n1/tot)*100; p2=(n2/tot)*100
                    st.markdown(f"""<div style="margin-bottom:12px;"><div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.9rem;"><span style="color:#38bdf8">{v1}</span><span style="color:#f43f5e">{v2}</span></div><div class="bar-bg"><div class="bar-l" style="width:{p1}%"></div><div class="bar-r" style="width:{p2}%"></div></div><div style="text-align:center; font-size:0.7rem; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-top:2px;">{l}</div></div>""",unsafe_allow_html=True)
                l=txt['lbl']
                stat_vis(l[0],s1['Taille'],s2['Taille']); stat_vis(l[1],s1['Allonge'],s2['Allonge']); stat_vis(l[2],s1['Coups'],s2['Coups'])
                stat_vis(l[3],f"{s1['Preci']}%",f"{s2['Preci']}%"); stat_vis(l[4],s1['TD'],s2['TD']); stat_vis(l[5],f"{s1['DefLutte']}%",f"{s2['DefLutte']}%")
                st.markdown('</div>',unsafe_allow_html=True)
                
                st.markdown(f"""<a href="https://www.unibet.fr/sport/mma" target="_blank" style="text-decoration:none;"><button style="width:100%; background:#fc4c02; color:white; border:none; padding:16px; border-radius:12px; font-weight:800; cursor:pointer;">{txt['cta']} {w}</button></a>""",unsafe_allow_html=True)
            else: st.error("Data error.")
