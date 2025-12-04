import streamlit as st
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Ultimate", page_icon="🦁", layout="centered")

# --- 2. BASE DE DONNÉES UNIFIÉE (ZERO ERREUR) ---
# T1 = P4P King / T2 = Champion / T3 = Top Contender
# Str = Striking / Grap = Lutte-Sol / Chin = Résistance / Cardio = Endurance / XP = Intelligence de combat
DB = {
    # HEAVYWEIGHT
    "Jon Jones":        {"Cat": "HW", "Tier": 1, "Style": "GOAT", "Taille": "193", "Allonge": "215", "Str": 88, "Grap": 98, "Chin": 98, "Cardio": 95, "XP": 100},
    "Tom Aspinall":     {"Cat": "HW", "Tier": 2, "Style": "Hybrid", "Taille": "196", "Allonge": "198", "Str": 96, "Grap": 85, "Chin": 90, "Cardio": 85, "XP": 88},
    "Ciryl Gane":       {"Cat": "HW", "Tier": 3, "Style": "Striker", "Taille": "193", "Allonge": "206", "Str": 95, "Grap": 60, "Chin": 90, "Cardio": 90, "XP": 85},
    "Stipe Miocic":     {"Cat": "HW", "Tier": 2, "Style": "Wrestler", "Taille": "193", "Allonge": "203", "Str": 85, "Grap": 88, "Chin": 80, "Cardio": 80, "XP": 98},
    "Francis Ngannou":  {"Cat": "HW", "Tier": 1, "Style": "Power", "Taille": "193", "Allonge": "211", "Str": 98, "Grap": 75, "Chin": 99, "Cardio": 75, "XP": 90},
    "Sergei Pavlovich": {"Cat": "HW", "Tier": 3, "Style": "Brawler", "Taille": "191", "Allonge": "213", "Str": 95, "Grap": 60, "Chin": 85, "Cardio": 70, "XP": 80},
    
    # LIGHT HEAVYWEIGHT
    "Alex Pereira":     {"Cat": "LHW", "Tier": 1, "Style": "Kickboxer", "Taille": "193", "Allonge": "200", "Str": 99, "Grap": 60, "Chin": 85, "Cardio": 88, "XP": 92},
    "Jiri Prochazka":   {"Cat": "LHW", "Tier": 2, "Style": "Chaos", "Taille": "191", "Allonge": "203", "Str": 94, "Grap": 70, "Chin": 75, "Cardio": 95, "XP": 85},
    "Magomed Ankalaev": {"Cat": "LHW", "Tier": 2, "Style": "Dagestani", "Taille": "191", "Allonge": "191", "Str": 85, "Grap": 92, "Chin": 90, "Cardio": 90, "XP": 88},
    "Jan Blachowicz":   {"Cat": "LHW", "Tier": 3, "Style": "Polish", "Taille": "188", "Allonge": "198", "Str": 85, "Grap": 85, "Chin": 90, "Cardio": 80, "XP": 92},

    # MIDDLEWEIGHT
    "Dricus Du Plessis":{"Cat": "MW", "Tier": 2, "Style": "Brawler", "Taille": "185", "Allonge": "193", "Str": 88, "Grap": 85, "Chin": 95, "Cardio": 98, "XP": 88},
    "Sean Strickland":  {"Cat": "MW", "Tier": 2, "Style": "Boxer", "Taille": "185", "Allonge": "193", "Str": 90, "Grap": 70, "Chin": 92, "Cardio": 100, "XP": 90},
    "Israel Adesanya":  {"Cat": "MW", "Tier": 1, "Style": "Sniper", "Taille": "193", "Allonge": "203", "Str": 98, "Grap": 65, "Chin": 85, "Cardio": 92, "XP": 98},
    "Robert Whittaker": {"Cat": "MW", "Tier": 2, "Style": "Complete", "Taille": "183", "Allonge": "185", "Str": 90, "Grap": 80, "Chin": 75, "Cardio": 90, "XP": 94},
    "Khamzat Chimaev":  {"Cat": "MW", "Tier": 1, "Style": "Wrestler", "Taille": "188", "Allonge": "191", "Str": 80, "Grap": 99, "Chin": 90, "Cardio": 80, "XP": 85},

    # WELTERWEIGHT
    "Belal Muhammad":   {"Cat": "WW", "Tier": 2, "Style": "Pressure", "Taille": "180", "Allonge": "183", "Str": 78, "Grap": 92, "Chin": 92, "Cardio": 98, "XP": 94},
    "Shavkat Rakhmonov":{"Cat": "WW", "Tier": 1, "Style": "Finisher", "Taille": "185", "Allonge": "196", "Str": 90, "Grap": 95, "Chin": 95, "Cardio": 95, "XP": 90},
    "Kamaru Usman":     {"Cat": "WW", "Tier": 2, "Style": "Wrestler", "Taille": "183", "Allonge": "193", "Str": 82, "Grap": 94, "Chin": 88, "Cardio": 90, "XP": 96},
    "Leon Edwards":     {"Cat": "WW", "Tier": 2, "Style": "Sniper", "Taille": "183", "Allonge": "188", "Str": 94, "Grap": 80, "Chin": 88, "Cardio": 90, "XP": 92},
    "Ian Machado Garry":{"Cat": "WW", "Tier": 3, "Style": "Striker", "Taille": "191", "Allonge": "188", "Str": 88, "Grap": 70, "Chin": 85, "Cardio": 88, "XP": 82},

    # LIGHTWEIGHT
    "Islam Makhachev":  {"Cat": "LW", "Tier": 1, "Style": "Sambo", "Taille": "178", "Allonge": "178", "Str": 85, "Grap": 99, "Chin": 92, "Cardio": 96, "XP": 98},
    "Arman Tsarukyan":  {"Cat": "LW", "Tier": 2, "Style": "Wrestler", "Taille": "170", "Allonge": "183", "Str": 85, "Grap": 94, "Chin": 90, "Cardio": 95, "XP": 88},
    "Charles Oliveira": {"Cat": "LW", "Tier": 2, "Style": "BJJ", "Taille": "178", "Allonge": "188", "Str": 90, "Grap": 98, "Chin": 75, "Cardio": 85, "XP": 94},
    "Justin Gaethje":   {"Cat": "LW", "Tier": 2, "Style": "Brawler", "Taille": "180", "Allonge": "178", "Str": 96, "Grap": 75, "Chin": 80, "Cardio": 88, "XP": 90},
    "Dustin Poirier":   {"Cat": "LW", "Tier": 2, "Style": "Boxer", "Taille": "175", "Allonge": "183", "Str": 94, "Grap": 70, "Chin": 88, "Cardio": 90, "XP": 96},
    "Conor McGregor":   {"Cat": "LW", "Tier": 3, "Style": "Sniper", "Taille": "175", "Allonge": "188", "Str": 95, "Grap": 60, "Chin": 80, "Cardio": 60, "XP": 92},
    "Benoit Saint Denis":{"Cat": "LW", "Tier": 3, "Style": "War", "Taille": "180", "Allonge": "185", "Str": 85, "Grap": 88, "Chin": 85, "Cardio": 90, "XP": 80},

    # FEATHERWEIGHT
    "Ilia Topuria":     {"Cat": "FW", "Tier": 1, "Style": "Boxer-Wrestler", "Taille": "170", "Allonge": "175", "Str": 97, "Grap": 88, "Chin": 98, "Cardio": 92, "XP": 90},
    "Max Holloway":     {"Cat": "FW", "Tier": 1, "Style": "Volume", "Taille": "180", "Allonge": "175", "Str": 95, "Grap": 75, "Chin": 100, "Cardio": 99, "XP": 98},
    "Alex Volkanovski": {"Cat": "FW", "Tier": 2, "Style": "Complete", "Taille": "168", "Allonge": "180", "Str": 92, "Grap": 88, "Chin": 85, "Cardio": 95, "XP": 99},
    
    # BANTAMWEIGHT
    "Sean O'Malley":    {"Cat": "BW", "Tier": 2, "Style": "Sniper", "Taille": "180", "Allonge": "183", "Str": 98, "Grap": 65, "Chin": 88, "Cardio": 90, "XP": 88},
    "Merab Dvalishvili":{"Cat": "BW", "Tier": 1, "Style": "Machine", "Taille": "168", "Allonge": "173", "Str": 75, "Grap": 99, "Chin": 92, "Cardio": 100, "XP": 90},
    "Umar Nurmagomedov":{"Cat": "BW", "Tier": 2, "Style": "Dagestani", "Taille": "173", "Allonge": "175", "Str": 88, "Grap": 95, "Chin": 90, "Cardio": 92, "XP": 85}
}

WEIGHT_MAP = ["BW", "FW", "LW", "WW", "MW", "LHW", "HW"]

# --- 3. ALGORITHME GRANDMASTER (LOGIQUE CORRIGÉE) ---
def grandmaster_algo(f1, f2):
    score = 0
    reasons = []
    
    # 1. TIER GAP (Level Check)
    # Tier 1 > Tier 2 (Ex: Islam > Belal)
    tier_diff = f2['Tier'] - f1['Tier'] # Si F1 est T1 (1) et F2 est T2 (2) -> Diff = 1 -> Avantage F1
    if tier_diff > 0:
        score += 20
        reasons.append(f"👑 ÉCART DE NIVEAU (P4P) : {f1['Nom']}")
    elif tier_diff < 0:
        score -= 20
        reasons.append(f"👑 ÉCART DE NIVEAU (P4P) : {f2['Nom']}")

    # 2. STYLE CHECK (Le "Cauchemar Stylistique")
    # Sambo/Dagestani vs Pas de Grappling Elite (<90)
    if "Sambo" in f1['Style'] or "Dagestani" in f1['Style']:
        if f2['Grap'] < 90:
            score += 15
            reasons.append(f"🦅 DOMINATION LUTTE/SAMBO : {f1['Nom']}")
    
    if "Sambo" in f2['Style'] or "Dagestani" in f2['Style']:
        if f1['Grap'] < 90:
            score -= 15
            reasons.append(f"🦅 DOMINATION LUTTE/SAMBO : {f2['Nom']}")

    # 3. ATTRIBUTS (Str, Grap, Cardio)
    diff_str = f1['Str'] - f2['Str']
    diff_grap = f1['Grap'] - f2['Grap']
    diff_cardio = f1['Cardio'] - f2['Cardio']
    
    if diff_str > 10: 
        score += 5
        reasons.append(f"🥊 AVANTAGE STRIKING : {f1['Nom']}")
    elif diff_str < -10:
        score -= 5
        reasons.append(f"🥊 AVANTAGE STRIKING : {f2['Nom']}")
        
    if diff_grap > 10: score += 8
    elif diff_grap < -10: score -= 8
    
    # 4. PHYSIQUE (Allonge)
    try:
        r1 = int(f1['Allonge'])
        r2 = int(f2['Allonge'])
        if r1 > r2 + 8: # +8cm significatif
            score += 5
            reasons.append(f"📏 AVANTAGE ALLONGE (+{r1-r2}cm)")
        elif r2 > r1 + 8:
            score -= 5
            reasons.append(f"📏 AVANTAGE ALLONGE (+{r2-r1}cm)")
    except: pass

    # CALCUL FINAL
    final_score = 50 + score
    final_score = max(10, min(90, final_score))
    
    # MÉTHODE DE VICTOIRE
    # Si écart de grappling énorme -> Soumission/Décision
    if abs(diff_grap) > 15:
        ko = 10; sub = 40; dec = 50
    # Si gros strikers -> KO
    elif f1['Str'] > 90 and f2['Str'] > 90:
        ko = 60; sub = 5; dec = 35
    else:
        ko = 25; sub = 15; dec = 60
        
    return int(final_score), ko, sub, dec, reasons[:3]

# --- 4. CSS (DESIGN CLEAN & LOGO CENTRÉ) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    
    .stApp {
        background-color: #020617;
        background-image: radial-gradient(at 50% 0%, rgba(34, 197, 94, 0.1) 0px, transparent 60%);
        font-family: 'Montserrat', sans-serif;
    }
    
    h1, h2, div, p, span { font-family: 'Montserrat', sans-serif !important; }

    /* LOGO CENTERING */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px 0;
    }
    .logo-container img {
        max-width: 280px;
        height: auto;
        filter: drop-shadow(0 0 10px rgba(34, 197, 94, 0.3));
    }

    /* CARDS */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 30px -5px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }

    /* INPUTS */
    .stSelectbox > div > div { background: transparent !important; border: none !important; }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        border-radius: 12px;
    }

    /* BUTTON */
    div.stButton > button {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: #020617 !important;
        border-radius: 12px;
        padding: 18px;
        font-weight: 900;
        text-transform: uppercase;
        border: none;
        width: 100%;
        letter-spacing: 1px;
        box-shadow: 0 5px 15px rgba(34, 197, 94, 0.3);
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.02); filter: brightness(1.1); }

    /* BARS */
    .bar-bg { width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; margin-top: 5px; display: flex;}
    .bar-l { height: 100%; background: #38bdf8; } 
    .bar-r { height: 100%; background: #f43f5e; }
    
    .finish-bar { width: 100%; height: 14px; background: #1e293b; border-radius: 7px; overflow: hidden; display: flex; margin-top: 10px; }
    .tag-reason { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.1); color: #cbd5e1; padding: 5px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 700; margin: 4px auto; display: table; }

</style>
""", unsafe_allow_html=True)

# --- 8. FRONTEND ---

# 1. HEADER (LOGO)
if os.path.exists("logo.png"):
    st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{st.image("logo.png", output_format="PNG")}" style="display:none;">
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("logo.png", use_column_width=True) 
else:
    st.markdown("<h1 style='text-align:center; color:white;'>CAGEMETRICS <span style='color:#22c55e'>ULTIMATE</span></h1>", unsafe_allow_html=True)

# 2. LANGUE
c_a, c_b = st.columns([6, 1])
with c_b:
    if st.button("🇺🇸" if st.session_state.lang == 'fr' else "🇫🇷", key="lang"): 
        st.session_state.lang = 'en' if st.session_state.lang == 'fr' else 'fr'
        st.rerun()

# 3. SELECTEURS
st.markdown("<br>", unsafe_allow_html=True)

# Filtre Catégorie
cats_map = {"Show All": "ALL", "Heavyweight (HW)": "HW", "Light Heavyweight (LHW)": "LHW", "Middleweight (MW)": "MW", "Welterweight (WW)": "WW", "Lightweight (LW)": "LW", "Featherweight (FW)": "FW", "Bantamweight (BW)": "BW"}
cat_select = st.selectbox("", list(cats_map.keys()), label_visibility="collapsed")

# Filtrage Roster
if cats_map[cat_select] == "ALL":
    roster = sorted(list(DB.keys()))
else:
    target = cats_map[cat_select]
    # Logique +1/-1 Catégorie
    idx = list(WEIGHT_MAP).index(target) if target in WEIGHT_MAP else 0
    allowed = [target]
    if idx > 0: allowed.append(WEIGHT_MAP[idx-1])
    if idx < len(WEIGHT_MAP)-1: allowed.append(WEIGHT_MAP[idx+1])
    roster = sorted([n for n, d in DB.items() if d['Cat'] in allowed])

# Combattants
c1, c2, c3 = st.columns([1, 0.1, 1])
f_a = c1.selectbox("Combattant A", roster, index=0, label_visibility="collapsed", key="a")
c2.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:white;'>VS</div>", unsafe_allow_html=True)
f_b = c3.selectbox("Combattant B", roster, index=1 if len(roster)>1 else 0, label_visibility="collapsed", key="b")

st.markdown("<br>", unsafe_allow_html=True)

# 4. ACTION
_, c_btn, _ = st.columns([1, 2, 1])
run = c_btn.button("LANCER L'ANALYSE", use_container_width=True)

if run:
    if f_a == f_b:
        st.warning("Veuillez sélectionner deux combattants différents.")
    else:
        with st.spinner("Analyse du style, cardio, data en cours..."):
            d1 = DB[f_a]; d1['Nom'] = f_a
            d2 = DB[f_b]; d2['Nom'] = f_b
            
            sc, k, s, d, reasons = grandmaster_algo(d1, d2)
            winner = d1['Nom'] if sc >= 50 else d2['Nom']
            conf = sc if sc >= 50 else 100 - sc
            
            # RESULTAT
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; border:2px solid #22c55e; background:rgba(34, 197, 94, 0.05);">
                <div style="color:#94a3b8; font-size:0.75rem; font-weight:800; letter-spacing:1px; margin-bottom:5px;">VAINQUEUR PRÉDIT</div>
                <div style="font-size:2.5rem; font-weight:900; color:white; line-height:1; margin-bottom:10px; text-transform:uppercase;">{winner}</div>
                <span style="background:#22c55e; color:#020617; padding:5px 15px; border-radius:50px; font-weight:800; font-size:0.9rem;">{conf}% DE CONFIANCE</span>
            </div>
            """, unsafe_allow_html=True)
            
            # RAISONS
            if reasons:
                html_r = "".join([f"<div class='tag-reason'>{r}</div>" for r in reasons])
                st.markdown(f"""<div class="glass-card"><div style="text-align:center; font-weight:800; color:white; margin-bottom:10px;">ANALYSE EXPERTE</div>{html_r}</div>""", unsafe_allow_html=True)
            
            # METHODE
            st.markdown(f"""
            <div class="glass-card">
                <div style="text-align:center; font-weight:800; color:white;">SCÉNARIO PROBABLE</div>
                <div class="finish-bar">
                    <div style="width:{k}%; background:#ef4444;"></div>
                    <div style="width:{s}%; background:#eab308;"></div>
                    <div style="width:{d}%; background:#3b82f6;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.75rem; font-weight:700;">
                    <span style="color:#ef4444">KO {k}%</span>
                    <span style="color:#eab308">SUB {s}%</span>
                    <span style="color:#3b82f6">DEC {d}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # STATS VISUELLES
            st.markdown('<div class="glass-card"><div style="text-align:center; color:#94a3b8; font-weight:700; margin-bottom:15px;">COMPARATIF TECHNIQUE</div>', unsafe_allow_html=True)
            
            def bar(lbl, v1, v2):
                tot = v1 + v2
                p1 = (v1 / tot) * 100
                p2 = (v2 / tot) * 100
                st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.9rem;">
                        <span style="color:#38bdf8">{v1}</span>
                        <span style="color:#f43f5e">{v2}</span>
                    </div>
                    <div class="bar-bg">
                        <div class="bar-l" style="width:{p1}%"></div>
                        <div class="bar-r" style="width:{p2}%"></div>
                    </div>
                    <div style="text-align:center; font-size:0.7rem; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-top:2px;">{lbl}</div>
                </div>
                """, unsafe_allow_html=True)
            
            bar("Puissance / Striking", d1['Str'], d2['Str'])
            bar("Grappling / Sol", d1['Grap'], d2['Grap'])
            bar("Menton / Résistance", d1['Chin'], d2['Chin'])
            bar("Cardio / Endurance", d1['Cardio'], d2['Cardio'])
            bar("Experience / Fight IQ", d1['XP'], d2['XP'])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # CTA
            st.markdown(f"""<a href="https://www.unibet.fr/sport/mma" target="_blank" style="text-decoration:none;"><button>VOIR LA COTE DE {winner}</button></a>""", unsafe_allow_html=True)
