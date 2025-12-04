import streamlit as st
import requests
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Ultimate", page_icon="🦁", layout="centered")

# --- 2. GESTION LANGUE ---
if 'lang' not in st.session_state: st.session_state.lang = 'fr'
def toggle(): st.session_state.lang = 'en' if st.session_state.lang == 'fr' else 'fr'

T = {
    "fr": { 
        "sub": "Algorithme Grandmaster : Analyse P4P & Styles", 
        "btn": "LANCER L'ANALYSE TACTIQUE", "win": "VAINQUEUR PRÉDIT", "conf": "INDICE DE CONFIANCE", 
        "meth": "SCÉNARIO DU COMBAT", 
        "tech": "COMPARATIF ELITE", "lbl": ["Puissance", "Menton", "Grappling", "Défense Sol", "Cardio", "XP/IQ"], 
        "cta": "VOIR LA COTE", "err": "Erreur : Sélectionnez deux combattants différents.",
        "keys": "ANALYSE DE L'EXPERTS",
        "reasons": {
            "tier_gap": "👑 ÉCART DE NIVEAU (P4P KING)",
            "style_sambo": "🦅 DOMINATION DAGHESTANI (SAMBO)",
            "style_sniper": "🎯 PRÉCISION D'ÉLITE",
            "chin_issue": "⚠️ MENTON FRAGILE DÉTECTÉ",
            "cardio_gap": "🫀 AVANTAGE CARDIO 5 ROUNDS",
            "phys_gap": "🦍 AVANTAGE PHYSIQUE MASSIF"
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
            "phys_gap": "🦍 MASSIVE PHYSICAL EDGE"
        }
    }
}
txt = T[st.session_state.lang]

# --- 3. DATABASE GRANDMASTER (TIERS & STYLES) ---
# Tier 1 = GOAT/P4P | Tier 2 = Champ | Tier 3 = Top 5
DB = {
    # HW
    "Jon Jones": {"Cat": "HW", "Tier": 1, "Style": "Complete", "Taille": "193 cm", "Allonge": "215 cm", "Str": 88, "Grap": 98, "Chin": 99, "Cardio": 95, "IQ": 100},
    "Tom Aspinall": {"Cat": "HW", "Tier": 2, "Style": "Hybrid", "Taille": "196 cm", "Allonge": "198 cm", "Str": 96, "Grap": 85, "Chin": 90, "Cardio": 88, "IQ": 90},
    "Ciryl Gane": {"Cat": "HW", "Tier": 3, "Style": "Striker", "Taille": "193 cm", "Allonge": "206 cm", "Str": 95, "Grap": 60, "Chin": 92, "Cardio": 90, "IQ": 88},
    "Stipe Miocic": {"Cat": "HW", "Tier": 2, "Style": "Wrestler-Boxer", "Taille": "193 cm", "Allonge": "203 cm", "Str": 85, "Grap": 88, "Chin": 80, "Cardio": 85, "IQ": 95},
    "Alexander Volkov": {"Cat": "HW", "Tier": 3, "Style": "Striker", "Taille": "201 cm", "Allonge": "203 cm", "Str": 88, "Grap": 75, "Chin": 85, "Cardio": 88, "IQ": 85},
    "Sergei Pavlovich": {"Cat": "HW", "Tier": 3, "Style": "Brawler", "Taille": "191 cm", "Allonge": "213 cm", "Str": 98, "Grap": 65, "Chin": 88, "Cardio": 70, "IQ": 80},
    "Jailton Almeida": {"Cat": "HW", "Tier": 3, "Style": "BJJ", "Taille": "191 cm", "Allonge": "201 cm", "Str": 65, "Grap": 95, "Chin": 80, "Cardio": 82, "IQ": 85},
    
    # LHW
    "Alex Pereira": {"Cat": "LHW", "Tier": 1, "Style": "Kickboxer", "Taille": "193 cm", "Allonge": "200 cm", "Str": 99, "Grap": 65, "Chin": 88, "Cardio": 88, "IQ": 92},
    "Magomed Ankalaev": {"Cat": "LHW", "Tier": 2, "Style": "Dagestani", "Taille": "191 cm", "Allonge": "191 cm", "Str": 85, "Grap": 92, "Chin": 92, "Cardio": 90, "IQ": 88},
    "Jiri Prochazka": {"Cat": "LHW", "Tier": 2, "Style": "Chaos", "Taille": "191 cm", "Allonge": "203 cm", "Str": 94, "Grap": 70, "Chin": 80, "Cardio": 92, "IQ": 82},
    "Jamahal Hill": {"Cat": "LHW", "Taille": "193 cm", "Allonge": "201 cm", "Tier": 3, "Style": "Striker", "Str": 92, "Grap": 65, "Chin": 85, "Cardio": 85, "IQ": 85},
    
    # MW
    "Dricus Du Plessis": {"Cat": "MW", "Tier": 2, "Style": "Brawler-Grap", "Taille": "185 cm", "Allonge": "193 cm", "Str": 88, "Grap": 85, "Chin": 95, "Cardio": 98, "IQ": 88},
    "Sean Strickland": {"Cat": "MW", "Tier": 2, "Style": "Boxer", "Taille": "185 cm", "Allonge": "193 cm", "Str": 90, "Grap": 70, "Chin": 92, "Cardio": 99, "IQ": 90},
    "Israel Adesanya": {"Cat": "MW", "Tier": 1, "Style": "Sniper", "Taille": "193 cm", "Allonge": "203 cm", "Str": 97, "Grap": 68, "Chin": 85, "Cardio": 92, "IQ": 98},
    "Robert Whittaker": {"Cat": "MW", "Tier": 2, "Style": "Complete", "Taille": "183 cm", "Allonge": "185 cm", "Str": 90, "Grap": 82, "Chin": 80, "Cardio": 90, "IQ": 92},
    "Khamzat Chimaev": {"Cat": "MW", "Tier": 1, "Style": "Wrestler", "Taille": "188 cm", "Allonge": "191 cm", "Str": 85, "Grap": 99, "Chin": 90, "Cardio": 80, "IQ": 88},
    "Nassourdine Imavov": {"Cat": "MW", "Tier": 3, "Style": "Striker", "Taille": "191 cm", "Allonge": "191 cm", "Str": 88, "Grap": 75, "Chin": 88, "Cardio": 85, "IQ": 85},

    # WW
    "Belal Muhammad": {"Cat": "WW", "Tier": 2, "Style": "Wrestler-Pressure", "Taille": "180 cm", "Allonge": "183 cm", "Str": 82, "Grap": 90, "Chin": 92, "Cardio": 98, "IQ": 95},
    "Shavkat Rakhmonov": {"Cat": "WW", "Tier": 1, "Style": "Complete", "Taille": "185 cm", "Allonge": "196 cm", "Str": 90, "Grap": 95, "Chin": 98, "Cardio": 95, "IQ": 92},
    "Leon Edwards": {"Cat": "WW", "Tier": 2, "Style": "Sniper", "Taille": "183 cm", "Allonge": "188 cm", "Str": 94, "Grap": 80, "Chin": 88, "Cardio": 90, "IQ": 90},
    "Kamaru Usman": {"Cat": "WW", "Tier": 2, "Style": "Wrestler", "Taille": "183 cm", "Allonge": "193 cm", "Str": 85, "Grap": 94, "Chin": 88, "Cardio": 90, "IQ": 95},
    "Jack Della Maddalena": {"Cat": "WW", "Tier": 3, "Style": "Boxer", "Taille": "180 cm", "Allonge": "185 cm", "Str": 93, "Grap": 65, "Chin": 92, "Cardio": 90, "IQ": 88},
    "Ian Machado Garry": {"Cat": "WW", "Tier": 3, "Style": "Striker", "Taille": "191 cm", "Allonge": "188 cm", "Str": 89, "Grap": 65, "Chin": 85, "Cardio": 88, "IQ": 85},

    # LW
    "Islam Makhachev": {"Cat": "LW", "Tier": 1, "Style": "Sambo", "Taille": "178 cm", "Allonge": "178 cm", "Str": 88, "Grap": 99, "Chin": 92, "Cardio": 96, "IQ": 98},
    "Arman Tsarukyan": {"Cat": "LW", "Tier": 2, "Style": "Wrestler", "Taille": "170 cm", "Allonge": "183 cm", "Str": 85, "Grap": 94, "Chin": 90, "Cardio": 95, "IQ": 90},
    "Charles Oliveira": {"Cat": "LW", "Tier": 2, "Style": "BJJ", "Taille": "178 cm", "Allonge": "188 cm", "Str": 90, "Grap": 98, "Chin": 78, "Cardio": 85, "IQ": 92},
    "Justin Gaethje": {"Cat": "LW", "Tier": 2, "Style": "Brawler", "Taille": "180 cm", "Allonge": "178 cm", "Str": 96, "Grap": 75, "Chin": 85, "Cardio": 88, "IQ": 85},
    "Dustin Poirier": {"Cat": "LW", "Tier": 2, "Style": "Boxer", "Taille": "175 cm", "Allonge": "183 cm", "Str": 94, "Grap": 70, "Chin": 90, "Cardio": 90, "IQ": 95},
    "Benoit Saint Denis": {"Cat": "LW", "Tier": 3, "Style": "Aggressive", "Taille": "180 cm", "Allonge": "185 cm", "Str": 85, "Grap": 88, "Chin": 85, "Cardio": 90, "IQ": 80},
    "Michael Chandler": {"Cat": "LW", "Tier": 3, "Style": "Explosive", "Taille": "173 cm", "Allonge": "180 cm", "Str": 88, "Grap": 85, "Chin": 80, "Cardio": 80, "IQ": 75},
    
    # FW
    "Ilia Topuria": {"Cat": "FW", "Tier": 1, "Style": "Complete", "Taille": "170 cm", "Allonge": "175 cm", "Str": 97, "Grap": 90, "Chin": 98, "Cardio": 92, "IQ": 95},
    "Max Holloway": {"Cat": "FW", "Tier": 1, "Style": "Boxer", "Taille": "180 cm", "Allonge": "175 cm", "Str": 95, "Grap": 75, "Chin": 100, "Cardio": 99, "IQ": 96},
    "Alexander Volkanovski": {"Cat": "FW", "Tier": 2, "Style": "Complete", "Taille": "168 cm", "Allonge": "180 cm", "Str": 92, "Grap": 88, "Chin": 88, "Cardio": 95, "IQ": 98},
    "Yair Rodriguez": {"Cat": "FW", "Tier": 3, "Style": "Kicker", "Taille": "180 cm", "Allonge": "180 cm", "Str": 92, "Grap": 60, "Chin": 85, "Cardio": 85, "IQ": 85},
    "Diego Lopes": {"Cat": "FW", "Tier": 3, "Style": "BJJ-Power", "Taille": "180 cm", "Allonge": "183 cm", "Str": 88, "Grap": 92, "Chin": 88, "Cardio": 85, "IQ": 85},

    # BW
    "Sean O'Malley": {"Cat": "BW", "Tier": 2, "Style": "Sniper", "Taille": "180 cm", "Allonge": "183 cm", "Str": 98, "Grap": 65, "Chin": 88, "Cardio": 90, "IQ": 92},
    "Merab Dvalishvili": {"Cat": "BW", "Tier": 1, "Style": "Machine", "Taille": "168 cm", "Allonge": "173 cm", "Str": 75, "Grap": 99, "Chin": 95, "Cardio": 100, "IQ": 90},
    "Petr Yan": {"Cat": "BW", "Tier": 2, "Style": "Complete", "Taille": "170 cm", "Allonge": "170 cm", "Str": 94, "Grap": 85, "Chin": 95, "Cardio": 95, "IQ": 92},
    "Umar Nurmagomedov": {"Cat": "BW", "Tier": 2, "Style": "Dagestani", "Taille": "173 cm", "Allonge": "175 cm", "Str": 88, "Grap": 95, "Chin": 90, "Cardio": 92, "IQ": 92},
    "Cory Sandhagen": {"Cat": "BW", "Tier": 3, "Style": "Creative", "Taille": "180 cm", "Allonge": "178 cm", "Str": 92, "Grap": 75, "Chin": 88, "Cardio": 92, "IQ": 90}
}

WEIGHT_CLASSES = {"HW": 265, "LHW": 205, "MW": 185, "WW": 170, "LW": 155, "FW": 145, "BW": 135}

# --- 4. HELPERS ---
def get_filtered_roster(category_code):
    if category_code == "ALL": return sorted(list(DB.keys()))
    try:
        idx = list(WEIGHT_CLASSES.keys()).index(category_code)
        keys = list(WEIGHT_CLASSES.keys())
        allowed = [keys[i] for i in range(max(0, idx-1), min(len(keys), idx+2))]
    except: allowed = [category_code]
    return sorted([name for name, data in DB.items() if data['Cat'] in allowed])

def get_data(name):
    if name in DB: d = DB[name].copy(); d['Nom'] = name; return d
    return None

# --- 5. ALGORITHME GRANDMASTER (LE COEUR DU PROJET) ---
def grandmaster_algo(f1, f2):
    score = 0
    reasons = []
    
    # A. TIER SYSTEM (P4P Difference)
    # Tier 1 vs Tier 2 = Avantage net
    # Tier 1 vs Tier 3 = Massacre
    tier_diff = f2['Tier'] - f1['Tier'] # Si f1 est 1 et f2 est 2, diff = 1 (F1 advantage)
    
    if tier_diff > 0: 
        score += tier_diff * 15 
        reasons.append(f"{txt['reasons']['tier_gap']} ({f1['Nom']})")
    elif tier_diff < 0: 
        score += tier_diff * 15 
        reasons.append(f"{txt['reasons']['tier_gap']} ({f2['Nom']})")

    # B. STYLE CHECK (Dagestani Handcuff)
    # Si Islam (Sambo) vs Striker sans défense d'élite -> Islam win auto
    if f1['Style'] in ["Sambo", "Dagestani"] and f2['Grap'] < 90:
        score += 20
        reasons.append(f"{txt['reasons']['style_sambo']} ({f1['Nom']})")
    elif f2['Style'] in ["Sambo", "Dagestani"] and f1['Grap'] < 90:
        score -= 20
        reasons.append(f"{txt['reasons']['style_sambo']} ({f2['Nom']})")

    # C. STRIKING & PUISSANCE
    # Sean O'Malley (Sniper) vs Wrestler lent
    str_diff = f1['Str'] - f2['Str']
    if str_diff > 10 and f1['Style'] == "Sniper":
        score += 10
        reasons.append(f"{txt['reasons']['style_sniper']} ({f1['Nom']})")
    elif str_diff < -10 and f2['Style'] == "Sniper":
        score -= 10
        reasons.append(f"{txt['reasons']['style_sniper']} ({f2['Nom']})")

    # D. POIDS (Si catégories différentes)
    w1 = WEIGHT_CLASSES.get(f1['Cat'], 155)
    w2 = WEIGHT_CLASSES.get(f2['Cat'], 155)
    diff_w = w1 - w2
    if abs(diff_w) > 15:
        w_bonus = diff_w * 0.5
        score += w_bonus
        if diff_w > 0: reasons.append(f"{txt['reasons']['phys_gap']} (+{diff_w} lbs)")
        else: reasons.append(f"{txt['reasons']['phys_gap']} (+{abs(diff_w)} lbs)")

    # E. CARDIO (5 Rounds)
    if f1['Cardio'] > f2['Cardio'] + 10:
        score += 5
        reasons.append(f"{txt['reasons']['cardio_gap']} ({f1['Nom']})")
    elif f2['Cardio'] > f1['Cardio'] + 10:
        score -= 5
        reasons.append(f"{txt['reasons']['cardio_gap']} ({f2['Nom']})")

    # FINALISATION
    final_score = 50 + score
    final_score = max(5, min(95, final_score))
    
    # Finish Logic
    grap_factor = max(f1['Grap'], f2['Grap'])
    pow_factor = max(f1['Str'], f2['Str'])
    
    # Si écart poids énorme -> KO
    if abs(diff_w) > 25:
        ko = 95; sub = 2; dec = 3
    # Si Dagestani dominant -> SUB/DEC
    elif "Dagestani" in [f1['Style'], f2['Style']] or "Sambo" in [f1['Style'], f2['Style']]:
        ko = 15; sub = 55; dec = 30
    # Si Sniper vs Chin faible -> KO
    elif (f1['Str'] > 95 and f2['Chin'] < 85) or (f2['Str'] > 95 and f1['Chin'] < 85):
        ko = 80; sub = 5; dec = 15
    else:
        # Standard
        ko = 30; sub = 20; dec = 50
        
    return int(final_score), ko, sub, dec, reasons[:3]

# --- 6. CSS (LOGO CENTRÉ ABSOLU) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    .stApp { background-color: #0f172a; background-image: radial-gradient(at 50% 0%, rgba(46, 204, 113, 0.1) 0px, transparent 60%); font-family: 'Montserrat', sans-serif; }
    h1,h2,div,p{font-family:'Montserrat',sans-serif!important;}
    
    /* LOGO CENTERING HACK */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    .logo-container img {
        max-width: 300px;
        height: auto;
    }

    .stSelectbox > div > div { background: transparent !important; border: none !important; }
    .stSelectbox div[data-baseweb="select"] > div { background-color: #1e293b !important; border: 1px solid rgba(255,255,255,0.1) !important; color: white !important; border-radius: 12px; }
    .glass-card { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); border-radius: 20px; padding: 24px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 10px 30px -5px rgba(0,0,0,0.4); margin-bottom: 20px; }
    div.stButton>button { background: #2ecc71!important; color: #020617!important; border-radius: 12px; padding: 18px; font-weight: 900; text-transform: uppercase; border: none; width: 100%; transition: 0.3s; }
    div.stButton>button:hover { transform: scale(1.02); }
    .bar-bg { width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; display: flex; margin-top: 5px; }
    .bar-l { height: 100%; background: #38bdf8; } .bar-r { height: 100%; background: #f43f5e; }
    .finish-cont { width: 100%; height: 14px; background: #1e293b; border-radius: 7px; overflow: hidden; display: flex; margin-top: 10px; }
    .reason-tag { background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 8px; font-size: 0.75rem; color: #cbd5e1; display: block; margin: 4px auto; border: 1px solid rgba(255,255,255,0.1); width: fit-content; }
</style>
""", unsafe_allow_html=True)

# --- 7. UI ---

# HEADER AVEC LOGO PARFAITEMENT CENTRÉ
if os.path.exists("logo.png"):
    st.markdown(
        f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{st.image("logo.png", output_format="PNG")}" style="display:none;">
        </div>
        """, unsafe_allow_html=True
    )
    st.image("logo.png", use_column_width=False, width=300) # Simple centering fallback
else:
    st.markdown("<h1 style='text-align:center; color:white;'>CAGEMETRICS <span style='color:#2ecc71'>ELITE</span></h1>", unsafe_allow_html=True)

c_1, c_2, c_3 = st.columns([1, 10, 1])
with c_2:
    st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-top:-10px;'>{txt['sub']}</div>", unsafe_allow_html=True)
with c_3:
    if st.button("🇫🇷" if st.session_state.lang == 'en' else "🇺🇸", key="lang"): toggle(); st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# SELECTION
cats_map = {"Heavyweight (HW)": "HW", "Light Heavyweight (LHW)": "LHW", "Middleweight (MW)": "MW", "Welterweight (WW)": "WW", "Lightweight (LW)": "LW", "Featherweight (FW)": "FW", "Bantamweight (BW)": "BW", "Show All / Fantasy": "ALL"}
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

# BOUTON
col_x, col_y, col_z = st.columns([1, 4, 1])
with col_y:
    analyze = st.button(txt['btn'], use_container_width=True)

if analyze:
    if f_a==f_b: st.warning(txt['err'])
    else:
        with st.spinner("Simulation..."):
            d1 = get_data(f_a); d2 = get_data(f_b)
            
            sc,k,sb,d, reasons = grandmaster_algo(d1, d2)
            w = d1['Nom'] if sc>=50 else d2['Nom']
            cf = sc if sc>=50 else 100-sc
            
            # WINNER
            st.markdown(f"""<div class="glass-card" style="text-align:center; border:2px solid #2ecc71; background:rgba(46, 204, 113, 0.05);"><div style="color:#94a3b8; font-size:0.7rem; font-weight:700; letter-spacing:1px; margin-bottom:5px;">{txt['win']}</div><div style="font-size:2.5rem; font-weight:900; color:white; line-height:1; margin-bottom:10px; text-transform:uppercase;">{w}</div><span style="background:#2ecc71; color:#020617; padding:4px 12px; border-radius:20px; font-weight:800; font-size:0.8rem;">{cf}% {txt['conf']}</span></div>""",unsafe_allow_html=True)
            
            if reasons:
                html_reasons = "".join([f"<span class='reason-tag'>{r}</span>" for r in reasons])
                st.markdown(f"""<div class="glass-card"><div style="text-align:center; font-weight:800; color:white; margin-bottom:10px;">{txt['keys']}</div><div style="text-align:center;">{html_reasons}</div></div>""", unsafe_allow_html=True)

            # SCENARIO
            st.markdown(f"""<div class="glass-card"><div style="text-align:center; font-weight:800; color:white;">{txt['meth']}</div><div class="finish-cont"><div style="width:{k}%; background:#ef4444;"></div><div style="width:{sb}%; background:#eab308;"></div><div style="width:{d}%; background:#3b82f6;"></div></div><div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.7rem; font-weight:700;"><span style="color:#ef4444">KO/TKO {k}%</span><span style="color:#eab308">SUB {sb}%</span><span style="color:#3b82f6">DEC {d}%</span></div></div>""",unsafe_allow_html=True)
            
            # STATS
            st.markdown(f'<div class="glass-card"><div style="text-align:center; color:#94a3b8; font-weight:700; margin-bottom:15px;">{txt["tech"]}</div>',unsafe_allow_html=True)
            def stat_vis(l,v1,v2, max_v):
                st.markdown(f"""<div style="margin-bottom:12px;"><div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.9rem;"><span style="color:#38bdf8">{v1}</span><span style="color:#f43f5e">{v2}</span></div><div class="bar-bg"><div class="bar-l" style="width:{(v1/max_v)*100}%"></div><div class="bar-r" style="width:{(v2/max_v)*100}%"></div></div><div style="text-align:center; font-size:0.7rem; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-top:2px;">{l}</div></div>""",unsafe_allow_html=True)
            
            l=txt['lbl']
            stat_vis(l[0],d1['Str'],d2['Str'], 100) # Puissance
            stat_vis(l[1],d1['Chin'],d2['Chin'], 100) # Menton
            stat_vis(l[2],d1['Grap'],d2['Grap'], 100) # Grap
            stat_vis(l[4],d1['Cardio'],d2['Cardio'], 100) # Cardio
            st.markdown('</div>',unsafe_allow_html=True)
            
            st.markdown(f"""<a href="https://www.unibet.fr/sport/mma" target="_blank" style="text-decoration:none;"><button style="width:100%; background:#fc4c02; color:white; border:none; padding:16px; border-radius:12px; font-weight:800; cursor:pointer;">{txt['cta']} {w}</button></a>""",unsafe_allow_html=True)
