import streamlit as st
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Pro", page_icon="🦁", layout="centered")

# --- 2. TEXTES (FRANÇAIS UNIQUEMENT) ---
TXT = {
    "sub": "L'algorithme de prédiction MMA le plus avancé",
    "btn": "LANCER L'ANALYSE DU COMBAT",
    "win": "VAINQUEUR PRÉDIT",
    "conf": "INDICE DE FIABILITÉ",
    "meth": "SCÉNARIO LE PLUS PROBABLE",
    "tech": "ANALYSE TECHNIQUE",
    "lbl": ["Puissance (KO)", "Lutte (Grappling)", "Menton (Résistance)", "Cardio (Endurance)", "Expérience (QI)", "Défense de Lutte"],
    "cta": "VOIR LA COTE SUR UNIBET",
    "err": "Erreur : Sélectionnez deux combattants différents.",
    "reasons": {
        "style_sambo": "🦅 DOMINATION DAGHESTANI (SAMBO)",
        "style_wrestler": "🤼 DOMINATION LUTTE (CONTROLE)",
        "sniper": "🎯 PRÉCISION CHIRURGICALE (STRIKING)",
        "chin_diff": "⚠️ DIFFÉRENCE DE RÉSISTANCE (MENTON)",
        "cardio_gap": "🫀 AVANTAGE CARDIO (5 ROUNDS)",
        "phys_gap": "🦍 AVANTAGE PHYSIQUE (ALLONGE)",
        "grap_def_gap": "🛡️ DÉFENSE DE LUTTE IMPERMÉABLE"
    }
}

# --- 3. BASE DE DONNÉES EXPERTE (STATS PURES) ---
# Str = Striking / Grap = Sol Offensif / Chin = Résistance / DefLutte = Défense d'amendée
DB = {
    # HEAVYWEIGHT
    "Jon Jones":        {"Cat": "HW", "Style": "Complet", "Taille": 193, "Allonge": 215, "Str": 88, "Grap": 98, "Chin": 98, "Cardio": 95, "XP": 100, "DefLutte": 95},
    "Tom Aspinall":     {"Cat": "HW", "Style": "Hybride", "Taille": 196, "Allonge": 198, "Str": 97, "Grap": 90, "Chin": 90, "Cardio": 85, "XP": 88, "DefLutte": 100},
    "Ciryl Gane":       {"Cat": "HW", "Style": "Striker", "Taille": 193, "Allonge": 206, "Str": 96, "Grap": 65, "Chin": 90, "Cardio": 90, "XP": 85, "DefLutte": 50},
    "Stipe Miocic":     {"Cat": "HW", "Style": "Lutteur", "Taille": 193, "Allonge": 203, "Str": 85, "Grap": 88, "Chin": 80, "Cardio": 80, "XP": 98, "DefLutte": 75},
    "Francis Ngannou":  {"Cat": "HW", "Style": "Power",   "Taille": 193, "Allonge": 211, "Str": 99, "Grap": 75, "Chin": 99, "Cardio": 75, "XP": 90, "DefLutte": 75},
    "Jailton Almeida":  {"Cat": "HW", "Style": "BJJ",     "Taille": 191, "Allonge": 201, "Str": 60, "Grap": 96, "Chin": 80, "Cardio": 82, "XP": 85, "DefLutte": 60},
    
    # LIGHT HEAVYWEIGHT
    "Alex Pereira":     {"Cat": "LHW", "Style": "Kickboxer", "Taille": 193, "Allonge": 200, "Str": 99, "Grap": 60, "Chin": 88, "Cardio": 88, "XP": 92, "DefLutte": 70},
    "Jiri Prochazka":   {"Cat": "LHW", "Style": "Chaos",     "Taille": 191, "Allonge": 203, "Str": 94, "Grap": 70, "Chin": 75, "Cardio": 95, "XP": 85, "DefLutte": 68},
    "Magomed Ankalaev": {"Cat": "LHW", "Style": "Dagestani", "Taille": 191, "Allonge": 191, "Str": 88, "Grap": 92, "Chin": 92, "Cardio": 90, "XP": 90, "DefLutte": 86},
    "Jan Blachowicz":   {"Cat": "LHW", "Style": "Complet",   "Taille": 188, "Allonge": 198, "Str": 85, "Grap": 85, "Chin": 92, "Cardio": 80, "XP": 94, "DefLutte": 75},

    # MIDDLEWEIGHT
    "Dricus Du Plessis":{"Cat": "MW", "Style": "Brawler", "Taille": 185, "Allonge": 193, "Str": 88, "Grap": 85, "Chin": 96, "Cardio": 98, "XP": 88, "DefLutte": 65},
    "Sean Strickland":  {"Cat": "MW", "Style": "Boxer",   "Taille": 185, "Allonge": 193, "Str": 90, "Grap": 65, "Chin": 92, "Cardio": 100, "XP": 90, "DefLutte": 90},
    "Israel Adesanya":  {"Cat": "MW", "Style": "Sniper",  "Taille": 193, "Allonge": 203, "Str": 98, "Grap": 60, "Chin": 85, "Cardio": 92, "XP": 98, "DefLutte": 80},
    "Khamzat Chimaev":  {"Cat": "MW", "Style": "Lutteur", "Taille": 188, "Allonge": 191, "Str": 82, "Grap": 99, "Chin": 90, "Cardio": 78, "XP": 85, "DefLutte": 100},
    "Robert Whittaker": {"Cat": "MW", "Style": "Complet", "Taille": 183, "Allonge": 185, "Str": 90, "Grap": 75, "Chin": 75, "Cardio": 90, "XP": 95, "DefLutte": 85},

    # WELTERWEIGHT
    "Belal Muhammad":   {"Cat": "WW", "Style": "Pression", "Taille": 180, "Allonge": 183, "Str": 80, "Grap": 92, "Chin": 92, "Cardio": 99, "XP": 94, "DefLutte": 95},
    "Shavkat Rakhmonov":{"Cat": "WW", "Style": "Finisher", "Taille": 185, "Allonge": 196, "Str": 92, "Grap": 95, "Chin": 95, "Cardio": 95, "XP": 90, "DefLutte": 100},
    "Kamaru Usman":     {"Cat": "WW", "Style": "Lutteur",  "Taille": 183, "Allonge": 193, "Str": 82, "Grap": 94, "Chin": 88, "Cardio": 90, "XP": 96, "DefLutte": 99},
    "Leon Edwards":     {"Cat": "WW", "Style": "Sniper",   "Taille": 183, "Allonge": 188, "Str": 95, "Grap": 80, "Chin": 88, "Cardio": 90, "XP": 92, "DefLutte": 75},
    "Ian Machado Garry":{"Cat": "WW", "Style": "Striker",  "Taille": 191, "Allonge": 188, "Str": 90, "Grap": 65, "Chin": 85, "Cardio": 88, "XP": 82, "DefLutte": 70},

    # LIGHTWEIGHT
    "Islam Makhachev":  {"Cat": "LW", "Style": "Sambo",    "Taille": 178, "Allonge": 178, "Str": 88, "Grap": 99, "Chin": 92, "Cardio": 96, "XP": 98, "DefLutte": 95},
    "Arman Tsarukyan":  {"Cat": "LW", "Style": "Lutteur",  "Taille": 170, "Allonge": 183, "Str": 86, "Grap": 95, "Chin": 90, "Cardio": 95, "XP": 88, "DefLutte": 80},
    "Charles Oliveira": {"Cat": "LW", "Style": "BJJ",      "Taille": 178, "Allonge": 188, "Str": 92, "Grap": 98, "Chin": 75, "Cardio": 85, "XP": 94, "DefLutte": 60},
    "Justin Gaethje":   {"Cat": "LW", "Style": "Brawler",  "Taille": 180, "Allonge": 178, "Str": 96, "Grap": 70, "Chin": 85, "Cardio": 88, "XP": 90, "DefLutte": 75},
    "Dustin Poirier":   {"Cat": "LW", "Style": "Boxer",    "Taille": 175, "Allonge": 183, "Str": 95, "Grap": 65, "Chin": 92, "Cardio": 90, "XP": 96, "DefLutte": 65},
    "Benoit Saint Denis":{"Cat": "LW", "Style": "Guerre",   "Taille": 180, "Allonge": 185, "Str": 85, "Grap": 88, "Chin": 88, "Cardio": 92, "XP": 82, "DefLutte": 70},

    # FEATHERWEIGHT
    "Ilia Topuria":     {"Cat": "FW", "Style": "Boxer",    "Taille": 170, "Allonge": 175, "Str": 98, "Grap": 85, "Chin": 98, "Cardio": 92, "XP": 90, "DefLutte": 95},
    "Max Holloway":     {"Cat": "FW", "Style": "Volume",   "Taille": 180, "Allonge": 175, "Str": 96, "Grap": 70, "Chin": 100, "Cardio": 99, "XP": 98, "DefLutte": 85},
    "Alex Volkanovski": {"Cat": "FW", "Style": "Complet",  "Taille": 168, "Allonge": 180, "Str": 94, "Grap": 88, "Chin": 85, "Cardio": 95, "XP": 99, "DefLutte": 75},
    "Diego Lopes":      {"Cat": "FW", "Style": "BJJ-Power","Taille": 180, "Allonge": 184, "Str": 88, "Grap": 92, "Chin": 88, "Cardio": 85, "XP": 80, "DefLutte": 60},

    # BANTAMWEIGHT
    "Sean O'Malley":    {"Cat": "BW", "Style": "Sniper",   "Taille": 180, "Allonge": 183, "Str": 99, "Grap": 60, "Chin": 88, "Cardio": 90, "XP": 88, "DefLutte": 70},
    "Merab Dvalishvili":{"Cat": "BW", "Style": "Machine",  "Taille": 168, "Allonge": 173, "Str": 75, "Grap": 99, "Chin": 95, "Cardio": 100, "XP": 90, "DefLutte": 80},
    "Umar Nurmagomedov":{"Cat": "BW", "Style": "Dagestani","Taille": 173, "Allonge": 175, "Str": 90, "Grap": 96, "Chin": 90, "Cardio": 92, "XP": 85, "DefLutte": 85},
    "Petr Yan":         {"Cat": "BW", "Style": "Complet",  "Taille": 170, "Allonge": 170, "Str": 95, "Grap": 80, "Chin": 95, "Cardio": 95, "XP": 92, "DefLutte": 88}
}

WEIGHT_MAP = ["BW", "FW", "LW", "WW", "MW", "LHW", "HW"]

# --- 4. ALGORITHME DE SIMULATION (LOGIQUE PURE) ---
def analyze_fight(f1, f2):
    score = 0
    reasons = []
    
    # A. STYLE : LE CAUCHEMAR DU STRIKER (Lutte vs Défense)
    # Si F1 a une lutte d'élite (>90) et F2 une défense moyenne (<85)
    grap_threat_1 = f1['Grap'] - f2['DefLutte']
    grap_threat_2 = f2['Grap'] - f1['DefLutte']
    
    if grap_threat_1 > 10: 
        score += 15
        if "Dagestani" in f1['Style'] or "Sambo" in f1['Style']: reasons.append(f"{TXT['reasons']['style_sambo']} ({f1['Nom']})")
        else: reasons.append(f"{TXT['reasons']['style_wrestler']} ({f1['Nom']})")
    
    if grap_threat_2 > 10: 
        score -= 15
        if "Dagestani" in f2['Style'] or "Sambo" in f2['Style']: reasons.append(f"{TXT['reasons']['style_sambo']} ({f2['Nom']})")
        else: reasons.append(f"{TXT['reasons']['style_wrestler']} ({f2['Nom']})")

    # B. STRIKING : PRÉCISION & PUISSANCE
    # Si le striking est bien meilleur, avantage
    str_diff = f1['Str'] - f2['Str']
    if str_diff > 8: 
        score += 8
        reasons.append(f"{TXT['reasons']['sniper']} ({f1['Nom']})")
    elif str_diff < -8: 
        score -= 8
        reasons.append(f"{TXT['reasons']['sniper']} ({f2['Nom']})")

    # C. PHYSIQUE (ALLONGE)
    # L'allonge compte surtout si on est un striker
    try:
        r1 = int(f1['Allonge'])
        r2 = int(f2['Allonge'])
        if r1 > r2 + 7: score += 5; reasons.append(f"{TXT['reasons']['phys_gap']} ({f1['Nom']})")
        elif r2 > r1 + 7: score -= 5; reasons.append(f"{TXT['reasons']['phys_gap']} ({f2['Nom']})")
    except: pass

    # D. CARDIO (5 ROUNDS)
    if f1['Cardio'] > f2['Cardio'] + 10: score += 5; reasons.append(f"{TXT['reasons']['cardio_gap']} ({f1['Nom']})")
    elif f2['Cardio'] > f1['Cardio'] + 10: score -= 5; reasons.append(f"{TXT['reasons']['cardio_gap']} ({f2['Nom']})")

    # E. FACTEUR X : MENTON
    chin_diff = f1['Chin'] - f2['Chin']
    if chin_diff > 15: score += 5
    elif chin_diff < -15: score -= 5

    # SCORE FINAL
    final_score = 50 + score
    final_score = max(5, min(95, final_score))
    
    # SCENARIO DE FINISH
    # Si gros écart de lutte -> Soumission / Décision
    if abs(grap_threat_1) > 15 or abs(grap_threat_2) > 15:
        ko = 15; sub = 45; dec = 40
    # Si deux gros strikers -> KO
    elif f1['Str'] > 90 and f2['Str'] > 90:
        ko = 60; sub = 5; dec = 35
    else:
        ko = 25; sub = 15; dec = 60
        
    return int(final_score), ko, sub, dec, reasons[:3]

# --- 5. CSS (STYLE PREMIUM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    
    .stApp { background-color: #0f172a; background-image: radial-gradient(at 50% 0%, rgba(46, 204, 113, 0.1) 0px, transparent 60%); font-family: 'Montserrat', sans-serif; }
    h1, h2, div, p { font-family: 'Montserrat', sans-serif !important; }

    /* LOGO & HEADER */
    .logo-container { display: flex; justify-content: center; padding: 20px 0; }
    
    /* INPUTS */
    .stSelectbox > div > div { background: transparent !important; border: none !important; }
    .stSelectbox div[data-baseweb="select"] > div { background-color: #1e293b !important; border: 1px solid rgba(255,255,255,0.1) !important; color: white !important; border-radius: 12px; }

    /* CARDS */
    .glass-card { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); border-radius: 20px; padding: 24px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 10px 30px -5px rgba(0,0,0,0.4); margin-bottom: 20px; }
    
    /* BOUTON ANALYSE */
    div.stButton > button { background: #3b82f6; color: white; border-radius: 12px; padding: 16px; font-weight: 800; border: none; width: 100%; text-transform: uppercase; transition:0.3s; }
    div.stButton > button:hover { transform: scale(1.02); }
    
    /* BOUTON AFFILIATION */
    .affiliate-btn {
        display: block; width: 100%; text-align: center;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white !important; padding: 20px; border-radius: 16px; text-decoration: none; font-weight: 900;
        text-transform: uppercase; letter-spacing: 1px; 
        box-shadow: 0 0 25px rgba(245, 158, 11, 0.4);
        margin-top: 15px; transition: all 0.3s ease-in-out;
    }
    .affiliate-btn:hover { transform: scale(1.03); box-shadow: 0 0 40px rgba(245, 158, 11, 0.6); }

    /* BARS */
    .bar-bg { width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; display: flex; margin-top: 5px; }
    .bar-l { height: 100%; background: #38bdf8; } .bar-r { height: 100%; background: #f43f5e; }
    .finish-cont { width: 100%; height: 14px; background: #1e293b; border-radius: 7px; overflow: hidden; display: flex; margin-top: 10px; }
    .tag-reason { background: rgba(255,255,255,0.1); padding: 5px 10px; border-radius: 8px; font-size: 0.75rem; color: #cbd5e1; display: inline-block; margin: 3px; border: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 6. UI ---

# HEADER AVEC LOGO
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align:center; color:white;'>CAGEMETRICS</h1>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-top:-10px;'>{TXT['sub']}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# FILTRES
cats_map = {"Heavyweight": "HW", "Light Heavyweight": "LHW", "Middleweight": "MW", "Welterweight": "WW", "Lightweight": "LW", "Featherweight": "FW", "Bantamweight": "BW", "Show All": "ALL"}
cat_name = st.selectbox("", list(cats_map.keys()), label_visibility="collapsed")
cat_code = cats_map[cat_name]

if cat_code == "ALL": roster = sorted(list(DB.keys()))
else:
    try: idx = WEIGHT_MAP.index(cat_code); allowed = [WEIGHT_MAP[i] for i in range(max(0,idx-1), min(len(WEIGHT_MAP),idx+2))]
    except: allowed = [cat_code]
    roster = sorted([n for n, d in DB.items() if d['Cat'] in allowed])

# SELECTION
c_a, c_vs, c_b = st.columns([1, 0.1, 1])
f_a = c_a.selectbox("A", roster, index=0, label_visibility="collapsed", key="fa")
c_vs.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:white;'>VS</div>", unsafe_allow_html=True)
f_b = c_b.selectbox("B", roster, index=1 if len(roster)>1 else 0, label_visibility="collapsed", key="fb")

st.markdown("<br>", unsafe_allow_html=True)

# BOUTON ANALYSE
_, c_run, _ = st.columns([1, 2, 1])
run = c_run.button(TXT['btn'], use_container_width=True)

if run:
    if f_a == f_b: st.warning(TXT['err'])
    else:
        with st.spinner("Analyse du style, cardio, data en cours..."):
            d1 = DB[f_a].copy(); d1['Nom'] = f_a
            d2 = DB[f_b].copy(); d2['Nom'] = f_b
            
            sc, k, s, d, reasons = analyze_fight(d1, d2)
            w = d1['Nom'] if sc >= 50 else d2['Nom']
            cf = sc if sc >= 50 else 100 - sc
            
            # WINNER
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; border:2px solid #2ecc71; background:rgba(34, 197, 94, 0.05);">
                <div style="color:#94a3b8; font-size:0.7rem; font-weight:700; letter-spacing:1px; margin-bottom:5px;">{TXT['win']}</div>
                <div style="font-size:2.5rem; font-weight:900; color:white; line-height:1; margin-bottom:10px; text-transform:uppercase;">{w}</div>
                <span style="background:#2ecc71; color:#020617; padding:5px 15px; border-radius:50px; font-weight:800; font-size:0.9rem;">{cf}% {TXT['conf']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # REASONS
            if reasons:
                html_r = "".join([f"<div class='tag-reason'>{r}</div>" for r in reasons])
                st.markdown(f"""<div class="glass-card" style="text-align:center;">{html_r}</div>""", unsafe_allow_html=True)
            
            # SCENARIO
            st.markdown(f"""
            <div class="glass-card">
                <div style="text-align:center; font-weight:800; color:white;">{TXT['meth']}</div>
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
            
            # STATS
            st.markdown(f'<div class="glass-card"><div style="text-align:center; color:#94a3b8; font-weight:700; margin-bottom:15px;">{TXT["tech"]}</div>', unsafe_allow_html=True)
            def draw_bar(label, v1, v2, max_v=100):
                p1 = (v1 / max_v) * 100; p2 = (v2 / max_v) * 100
                st.markdown(f"""<div style="margin-bottom:12px;"><div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.9rem;"><span style="color:#38bdf8">{v1}</span><span style="color:#f43f5e">{v2}</span></div><div class="bar-bg"><div class="bar-l" style="width:{p1}%"></div><div class="bar-r" style="width:{p2}%"></div></div><div style="text-align:center; font-size:0.65rem; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-top:2px;">{label}</div></div>""", unsafe_allow_html=True)
            
            l = TXT['lbl']
            draw_bar(l[0], d1['Str'], d2['Str'])
            draw_bar(l[1], d1['Grap'], d2['Grap'])
            draw_bar(l[2], d1['Chin'], d2['Chin'])
            draw_bar(l[3], d1['Cardio'], d2['Cardio'])
            draw_bar(l[4], d1['XP'], d2['XP'])
            draw_bar(l[5], d1['DefLutte'], d2['DefLutte'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # AFFILIATION
            st.markdown(f"""
            <a href="https://www.unibet.fr/sport/mma" target="_blank" class="affiliate-btn">
                {TXT['cta']} {w}
            </a>
            <div style="text-align:center; font-size:0.6rem; color:#64748b; margin-top:10px;">
                18+ | Jouer comporte des risques...
            </div>
            """, unsafe_allow_html=True)
