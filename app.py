import streamlit as st
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Ultimate", page_icon="🦁", layout="centered")

# --- 2. INITIALISATION SESSION (CORRECTIF CRITIQUE) ---
# C'est ce bloc qui manquait et causait l'erreur
if 'lang' not in st.session_state:
    st.session_state.lang = 'fr'

def toggle_lang():
    if st.session_state.lang == 'fr':
        st.session_state.lang = 'en'
    else:
        st.session_state.lang = 'fr'

# Textes de l'interface
T = {
    "fr": { 
        "sub": "Algorithme Grandmaster : Analyse P4P & Styles", 
        "btn": "LANCER L'ANALYSE TACTIQUE", "win": "VAINQUEUR PRÉDIT", "conf": "INDICE DE CONFIANCE", 
        "meth": "SCÉNARIO DU COMBAT", 
        "tech": "COMPARATIF ELITE", "lbl": ["Puissance", "Menton", "Grappling", "Défense Sol", "Cardio", "XP/IQ"], 
        "cta": "VOIR LA COTE", "err": "Erreur : Sélectionnez deux combattants différents.",
        "keys": "ANALYSE DE L'EXPERT",
        "reasons": {
            "tier_gap": "👑 ÉCART DE NIVEAU (P4P KING)",
            "style_sambo": "🦅 DOMINATION DAGHESTANI (SAMBO)",
            "style_sniper": "🎯 PRÉCISION D'ÉLITE",
            "chin_issue": "⚠️ MENTON FRAGILE DÉTECTÉ",
            "cardio_gap": "🫀 AVANTAGE CARDIO 5 ROUNDS",
            "phys_gap": "🦍 AVANTAGE PHYSIQUE MASSIF",
            "str_gap": "🥊 AVANTAGE STRIKING NET",
            "grap_gap": "🤼 AVANTAGE LUTTE"
        }
    },
    "en": { 
        "sub": "Grandmaster Algorithm: P4P & Style Analysis", 
        "btn": "RUN TACTICAL ANALYSIS", "win": "PREDICTED WINNER", "conf": "CONFIDENCE SCORE", 
        "meth": "FIGHT SCENARIO", 
        "tech": "ELITE COMPARISON", "lbl": ["Power", "Chin", "Grappling", "Ground Def", "Cardio", "XP/IQ"], 
        "cta": "SEE ODDS", "err": "Error: Select two different fighters.",
        "keys": "EXPERT ANALYSIS",
        "reasons": {
            "tier_gap": "👑 LEVEL GAP (P4P KING)",
            "style_sambo": "🦅 DAGESTANI DOMINANCE (SAMBO)",
            "style_sniper": "🎯 ELITE PRECISION",
            "chin_issue": "⚠️ GLASS CHIN DETECTED",
            "cardio_gap": "🫀 5-ROUND CARDIO EDGE",
            "phys_gap": "🦍 MASSIVE PHYSICAL EDGE",
            "str_gap": "🥊 STRIKING ADVANTAGE",
            "grap_gap": "🤼 WRESTLING ADVANTAGE"
        }
    }
}
txt = T[st.session_state.lang]

# --- 3. DATABASE (STATS FIABLES) ---
DB = {
    # HW
    "Jon Jones":        {"Cat": "HW", "Tier": 1, "Style": "GOAT", "Taille": "193", "Allonge": "215", "Str": 88, "Grap": 98, "Chin": 98, "Cardio": 95, "XP": 100},
    "Tom Aspinall":     {"Cat": "HW", "Tier": 2, "Style": "Hybrid", "Taille": "196", "Allonge": "198", "Str": 96, "Grap": 85, "Chin": 90, "Cardio": 85, "XP": 88},
    "Ciryl Gane":       {"Cat": "HW", "Tier": 3, "Style": "Striker", "Taille": "193", "Allonge": "206", "Str": 95, "Grap": 60, "Chin": 90, "Cardio": 90, "XP": 85},
    "Stipe Miocic":     {"Cat": "HW", "Tier": 2, "Style": "Wrestler", "Taille": "193", "Allonge": "203", "Str": 85, "Grap": 88, "Chin": 80, "Cardio": 80, "XP": 98},
    "Francis Ngannou":  {"Cat": "HW", "Tier": 1, "Style": "Power", "Taille": "193", "Allonge": "211", "Str": 98, "Grap": 75, "Chin": 99, "Cardio": 75, "XP": 90},
    
    # LHW
    "Alex Pereira":     {"Cat": "LHW", "Tier": 1, "Style": "Kickboxer", "Taille": "193", "Allonge": "200", "Str": 99, "Grap": 60, "Chin": 85, "Cardio": 88, "XP": 92},
    "Jiri Prochazka":   {"Cat": "LHW", "Tier": 2, "Style": "Chaos", "Taille": "191", "Allonge": "203", "Str": 94, "Grap": 70, "Chin": 75, "Cardio": 95, "XP": 85},
    "Magomed Ankalaev": {"Cat": "LHW", "Tier": 2, "Style": "Dagestani", "Taille": "191", "Allonge": "191", "Str": 85, "Grap": 92, "Chin": 90, "Cardio": 90, "XP": 88},

    # MW
    "Dricus Du Plessis":{"Cat": "MW", "Tier": 2, "Style": "Brawler", "Taille": "185", "Allonge": "193", "Str": 88, "Grap": 85, "Chin": 95, "Cardio": 98, "XP": 88},
    "Sean Strickland":  {"Cat": "MW", "Tier": 2, "Style": "Boxer", "Taille": "185", "Allonge": "193", "Str": 90, "Grap": 70, "Chin": 92, "Cardio": 100, "XP": 90},
    "Israel Adesanya":  {"Cat": "MW", "Tier": 1, "Style": "Sniper", "Taille": "193", "Allonge": "203", "Str": 98, "Grap": 65, "Chin": 85, "Cardio": 92, "XP": 98},
    "Robert Whittaker": {"Cat": "MW", "Tier": 2, "Style": "Complete", "Taille": "183", "Allonge": "185", "Str": 90, "Grap": 80, "Chin": 75, "Cardio": 90, "XP": 94},
    "Khamzat Chimaev":  {"Cat": "MW", "Tier": 1, "Style": "Wrestler", "Taille": "188", "Allonge": "191", "Str": 80, "Grap": 99, "Chin": 90, "Cardio": 80, "XP": 85},

    # WW
    "Belal Muhammad":   {"Cat": "WW", "Tier": 2, "Style": "Pressure", "Taille": "180", "Allonge": "183", "Str": 78, "Grap": 92, "Chin": 92, "Cardio": 98, "XP": 94},
    "Shavkat Rakhmonov":{"Cat": "WW", "Tier": 1, "Style": "Finisher", "Taille": "185", "Allonge": "196", "Str": 90, "Grap": 95, "Chin": 95, "Cardio": 95, "XP": 90},
    "Kamaru Usman":     {"Cat": "WW", "Tier": 2, "Style": "Wrestler", "Taille": "183", "Allonge": "193", "Str": 82, "Grap": 94, "Chin": 88, "Cardio": 90, "XP": 96},
    "Leon Edwards":     {"Cat": "WW", "Tier": 2, "Style": "Sniper", "Taille": "183", "Allonge": "188", "Str": 94, "Grap": 80, "Chin": 88, "Cardio": 90, "XP": 92},

    # LW
    "Islam Makhachev":  {"Cat": "LW", "Tier": 1, "Style": "Sambo", "Taille": "178", "Allonge": "178", "Str": 85, "Grap": 99, "Chin": 92, "Cardio": 96, "XP": 98},
    "Arman Tsarukyan":  {"Cat": "LW", "Tier": 2, "Style": "Wrestler", "Taille": "170", "Allonge": "183", "Str": 85, "Grap": 94, "Chin": 90, "Cardio": 95, "XP": 88},
    "Charles Oliveira": {"Cat": "LW", "Tier": 2, "Style": "BJJ", "Taille": "178", "Allonge": "188", "Str": 90, "Grap": 98, "Chin": 75, "Cardio": 85, "XP": 94},
    "Justin Gaethje":   {"Cat": "LW", "Tier": 2, "Style": "Brawler", "Taille": "180", "Allonge": "178", "Str": 96, "Grap": 75, "Chin": 80, "Cardio": 88, "XP": 90},
    "Dustin Poirier":   {"Cat": "LW", "Tier": 2, "Style": "Boxer", "Taille": "175", "Allonge": "183", "Str": 94, "Grap": 70, "Chin": 88, "Cardio": 90, "XP": 96},
    "Conor McGregor":   {"Cat": "LW", "Tier": 3, "Style": "Sniper", "Taille": "175", "Allonge": "188", "Str": 95, "Grap": 60, "Chin": 80, "Cardio": 60, "XP": 92},
    "Benoit Saint Denis":{"Cat": "LW", "Tier": 3, "Style": "War", "Taille": "180", "Allonge": "185", "Str": 85, "Grap": 88, "Chin": 85, "Cardio": 90, "XP": 80},

    # FW
    "Ilia Topuria":     {"Cat": "FW", "Tier": 1, "Style": "Boxer-Wrestler", "Taille": "170", "Allonge": "175", "Str": 97, "Grap": 88, "Chin": 98, "Cardio": 92, "XP": 90},
    "Max Holloway":     {"Cat": "FW", "Tier": 1, "Style": "Volume", "Taille": "180", "Allonge": "175", "Str": 95, "Grap": 75, "Chin": 100, "Cardio": 99, "XP": 98},
    "Alex Volkanovski": {"Cat": "FW", "Tier": 2, "Style": "Complete", "Taille": "168", "Allonge": "180", "Str": 92, "Grap": 88, "Chin": 85, "Cardio": 95, "XP": 99},
    
    # BW
    "Sean O'Malley":    {"Cat": "BW", "Tier": 2, "Style": "Sniper", "Taille": "180", "Allonge": "183", "Str": 98, "Grap": 65, "Chin": 88, "Cardio": 90, "XP": 88},
    "Merab Dvalishvili":{"Cat": "BW", "Tier": 1, "Style": "Machine", "Taille": "168", "Allonge": "173", "Str": 75, "Grap": 99, "Chin": 92, "Cardio": 100, "XP": 90},
    "Umar Nurmagomedov":{"Cat": "BW", "Tier": 2, "Style": "Dagestani", "Taille": "173", "Allonge": "175", "Str": 88, "Grap": 95, "Chin": 90, "Cardio": 92, "XP": 85}
}

WEIGHT_MAP = ["BW", "FW", "LW", "WW", "MW", "LHW", "HW"]

# --- 4. ALGORITHME GRANDMASTER ---
def grandmaster_algo(f1, f2):
    score = 0
    reasons = []
    
    # 1. TIER GAP (Level Check)
    tier_diff = f2['Tier'] - f1['Tier'] 
    if tier_diff > 0:
        score += 20
        reasons.append(f"{txt['reasons']['tier_gap']} ({f1['Nom']})")
    elif tier_diff < 0:
        score -= 20
        reasons.append(f"{txt['reasons']['tier_gap']} ({f2['Nom']})")

    # 2. STYLE CHECK (Le facteur Islam/Khabib)
    if ("Sambo" in f1['Style'] or "Dagestani" in f1['Style']) and f2['Grap'] < 95:
        score += 18
        reasons.append(f"{txt['reasons']['style_sambo']} ({f1['Nom']})")
    
    if ("Sambo" in f2['Style'] or "Dagestani" in f2['Style']) and f1['Grap'] < 95:
        score -= 18
        reasons.append(f"{txt['reasons']['style_sambo']} ({f2['Nom']})")

    # 3. ATTRIBUTS
    diff_str = f1['Str'] - f2['Str']
    diff_grap = f1['Grap'] - f2['Grap']
    
    if diff_str > 10: 
        score += 5
        reasons.append(f"{txt['reasons']['str_gap']} ({f1['Nom']})")
    elif diff_str < -10:
        score -= 5
        reasons.append(f"{txt['reasons']['str_gap']} ({f2['Nom']})")
        
    if diff_grap > 12: 
        score += 10
        reasons.append(f"{txt['reasons']['grap_gap']} ({f1['Nom']})")
    elif diff_grap < -12: 
        score -= 10
        reasons.append(f"{txt['reasons']['grap_gap']} ({f2['Nom']})")
    
    # 4. ALLONGE
    try:
        r1 = int(f1['Allonge'])
        r2 = int(f2['Allonge'])
        if r1 > r2 + 8: 
            score += 5
            reasons.append(f"{txt['reasons']['phys_gap']} ({f1['Nom']})")
        elif r2 > r1 + 8:
            score -= 5
            reasons.append(f"{txt['reasons']['phys_gap']} ({f2['Nom']})")
    except: pass

    # CALCUL FINAL
    final_score = 50 + score
    final_score = max(10, min(90, final_score))
    
    # FINISH LOGIC
    if abs(diff_grap) > 15:
        ko = 10; sub = 45; dec = 45
    elif f1['Str'] > 90 and f2['Str'] > 90:
        ko = 60; sub = 5; dec = 35
    else:
        ko = 25; sub = 15; dec = 60
        
    return int(final_score), ko, sub, dec, reasons[:3]

# --- 5. CSS CLEAN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    
    .stApp {
        background-color: #0f172a;
        background-image: radial-gradient(at 50% 0%, rgba(34, 197, 94, 0.1) 0px, transparent 60%);
        font-family: 'Montserrat', sans-serif;
    }
    
    h1, h2, div, p, span { font-family: 'Montserrat', sans-serif !important; }

    /* INPUTS */
    .stSelectbox > div > div { background: transparent !important; border: none !important; }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        border-radius: 12px;
    }

    /* CARDS & BUTTONS */
    .glass-card { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); border-radius: 20px; padding: 24px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 10px 30px -5px rgba(0,0,0,0.4); margin-bottom: 20px; }
    div.stButton>button { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important; color: #020617 !important; border-radius: 12px; padding: 18px; font-weight: 900; text-transform: uppercase; border: none; width: 100%; letter-spacing: 1px; transition: 0.3s; }
    div.stButton>button:hover { transform: scale(1.02); filter: brightness(1.1); }

    /* BARS */
    .bar-bg { width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; display: flex; margin-top: 5px; }
    .bar-l { height: 100%; background: #38bdf8; } 
    .bar-r { height: 100%; background: #f43f5e; }
    .finish-cont { width: 100%; height: 14px; background: #1e293b; border-radius: 7px; overflow: hidden; display: flex; margin-top: 10px; }
    .tag-reason { background: rgba(255,255,255,0.1); padding: 5px 10px; border-radius: 8px; font-size: 0.75rem; color: #cbd5e1; display: block; margin: 4px auto; border: 1px solid rgba(255,255,255,0.1); width: fit-content; }
</style>
""", unsafe_allow_html=True)

# --- 6. INTERFACE ---

# HEADER
c_emp, c_logo, c_lang = st.columns([1, 6, 1])
with c_logo:
    # Utilisation de st.image pour un centrage simple via la colonne
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align:center; color:white;'>CAGEMETRICS <span style='color:#22c55e'>ULTIMATE</span></h1>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-top:-10px;'>{txt['sub']}</div>", unsafe_allow_html=True)

with c_lang:
    if st.button("🇺🇸" if st.session_state.lang == 'fr' else "🇫🇷", key="lang"): 
        toggle()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# SELECTEURS
cats_map = {"Heavyweight (HW)": "HW", "Light Heavyweight (LHW)": "LHW", "Middleweight (MW)": "MW", "Welterweight (WW)": "WW", "Lightweight (LW)": "LW", "Featherweight (FW)": "FW", "Bantamweight (BW)": "BW", "Show All / Fantasy": "ALL"}
cat_name = st.selectbox("", list(cats_map.keys()), label_visibility="collapsed")
cat_code = cats_map[cat_name]

# Filtre Roster
if cat_code == "ALL": roster = sorted(list(DB.keys()))
else:
    try:
        idx = WEIGHT_MAP.index(cat_code)
        allowed = [WEIGHT_MAP[i] for i in range(max(0, idx-1), min(len(WEIGHT_MAP), idx+2))]
    except: allowed = [cat_code]
    roster = sorted([n for n, d in DB.items() if d['Cat'] in allowed])

c1, c2, c3 = st.columns([1, 0.1, 1])
idx_a = roster.index("Jon Jones") if "Jon Jones" in roster else 0
f_a = c1.selectbox("Combattant A", roster, index=idx_a, label_visibility="collapsed", key="fa")
c2.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:white;'>VS</div>", unsafe_allow_html=True)
f_b = c3.selectbox("Combattant B", roster, index=1 if len(roster)>1 else 0, label_visibility="collapsed", key="fb")

st.markdown("<br>", unsafe_allow_html=True)

# BOUTON
_, c_btn, _ = st.columns([1, 2, 1])
analyze = c_btn.button(txt['btn'], use_container_width=True)

if analyze:
    if f_a == f_b:
        st.warning(txt['err'])
    else:
        # Récupération données
        d1 = DB[f_a].copy(); d1['Nom'] = f_a
        d2 = DB[f_b].copy(); d2['Nom'] = f_b
        
        # Calcul
        sc, k, s, d, reasons = grandmaster_algo(d1, d2)
        winner = d1['Nom'] if sc >= 50 else d2['Nom']
        conf = sc if sc >= 50 else 100 - sc
        
        # Affichage Winner
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; border:2px solid #22c55e; background:rgba(34, 197, 94, 0.05);">
            <div style="color:#94a3b8; font-size:0.7rem; font-weight:700; letter-spacing:1px; margin-bottom:5px;">{txt['win']}</div>
            <div style="font-size:2.5rem; font-weight:900; color:white; line-height:1; margin-bottom:10px; text-transform:uppercase;">{winner}</div>
            <span style="background:#22c55e; color:#020617; padding:5px 15px; border-radius:50px; font-weight:800; font-size:0.9rem;">{conf}% {txt['conf']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if reasons:
            html_r = "".join([f"<div class='tag-reason'>{r}</div>" for r in reasons])
            st.markdown(f"""<div class="glass-card"><div style="text-align:center; font-weight:800; color:white; margin-bottom:10px;">{txt['keys']}</div>{html_r}</div>""", unsafe_allow_html=True)
        
        # Scenario
        st.markdown(f"""
        <div class="glass-card">
            <div style="text-align:center; font-weight:800; color:white;">{txt['meth']}</div>
            <div class="finish-cont">
                <div style="width:{k}%; background:#ef4444;"></div>
                <div style="width:{s}%; background:#eab308;"></div>
                <div style="width:{d}%; background:#3b82f6;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.7rem; font-weight:700;">
                <span style="color:#ef4444">KO {k}%</span>
                <span style="color:#eab308">SUB {s}%</span>
                <span style="color:#3b82f6">DEC {d}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats
        st.markdown(f'<div class="glass-card"><div style="text-align:center; color:#94a3b8; font-weight:700; margin-bottom:15px;">{txt["tech"]}</div>', unsafe_allow_html=True)
        def draw_bar(label, v1, v2, max_v=100):
            p1 = (v1 / max_v) * 100
            p2 = (v2 / max_v) * 100
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
                <div style="text-align:center; font-size:0.65rem; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-top:2px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)
            
        l = txt['lbl']
        draw_bar(l[0], int(d1['Str']), int(d2['Str']))
        draw_bar(l[1], int(d1['Chin']), int(d2['Chin']))
        draw_bar(l[2], int(d1['Grap']), int(d2['Grap']))
        draw_bar(l[3], int(d1['Cardio']), int(d2['Cardio']))
        draw_bar(l[5], int(d1['XP']), int(d2['XP']))
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"""<a href="https://www.unibet.fr/sport/mma" target="_blank" style="text-decoration:none;"><button>{txt['cta']} {winner}</button></a>""", unsafe_allow_html=True)
