import streamlit as st
import requests
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Elite", page_icon="🩸", layout="centered")

# --- 2. GESTION LANGUE ---
if 'lang' not in st.session_state: st.session_state.lang = 'fr'
def toggle(): st.session_state.lang = 'en' if st.session_state.lang == 'fr' else 'fr'

T = {
    "fr": { 
        "sub": "Moteur de Simulation Réaliste (Stats + Physique + Dégâts)", 
        "btn": "LANCER LA SIMULATION", "win": "VAINQUEUR PRÉDIT", "conf": "INDICE DE CONFIANCE", 
        "meth": "SCÉNARIO DU COMBAT", 
        "tech": "ATTRIBUTS CLÉS", "lbl": ["Puissance KO", "Menton (Résistance)", "Lutte Offensive", "Défense Lutte", "Cardio/Volume", "Allonge"], 
        "cta": "VOIR LA COTE", "err": "Erreur : Sélectionnez deux combattants différents.",
        "keys": "FACTEURS X",
        "reasons": {
            "ko_power": "☠️ PUISSANCE DE KO LÉTALE",
            "chin": "🛡️ MENTON EN GRANITE",
            "glass": "⚠️ MENTON SUSPECT DÉTECTÉ",
            "grap": "🤼 DOMINATION LUTTE",
            "volume": "🥊 VOLUME SUPÉRIEUR",
            "diff_w": "⚖️ AVANTAGE GABARIT"
        }
    },
    "en": { 
        "sub": "Realistic Simulation Engine (Stats + Physics + Damage)", 
        "btn": "RUN SIMULATION", "win": "PREDICTED WINNER", "conf": "CONFIDENCE SCORE", 
        "meth": "FIGHT SCENARIO", 
        "tech": "KEY ATTRIBUTES", "lbl": ["KO Power", "Chin (Durability)", "Wrestling Off", "Wrestling Def", "Cardio/Volume", "Reach"], 
        "cta": "SEE ODDS", "err": "Error: Select two different fighters.",
        "keys": "X-FACTORS",
        "reasons": {
            "ko_power": "☠️ LETHAL KO POWER",
            "chin": "🛡️ GRANITE CHIN",
            "glass": "⚠️ SUSPECT CHIN DETECTED",
            "grap": "🤼 WRESTLING DOMINANCE",
            "volume": "🥊 HIGHER VOLUME",
            "diff_w": "⚖️ SIZE ADVANTAGE"
        }
    }
}
txt = T[st.session_state.lang]

# --- 3. DATABASE AVANCÉE (STATS + HIDDEN ATTRIBUTES) ---
# Pow = Puissance (0-100), Chin = Résistance (0-100)
DB = {
    # HW
    "Jon Jones": {"Cat": "HW", "Taille": "193 cm", "Allonge": "213 cm", "Coups": 4.30, "TD": 1.9, "DefLutte": 95, "Preci": 58, "Pow": 85, "Chin": 98},
    "Tom Aspinall": {"Cat": "HW", "Taille": "196 cm", "Allonge": "198 cm", "Coups": 7.72, "TD": 3.5, "DefLutte": 100, "Preci": 66, "Pow": 96, "Chin": 90},
    "Ciryl Gane": {"Cat": "HW", "Taille": "193 cm", "Allonge": "206 cm", "Coups": 5.11, "TD": 0.6, "DefLutte": 45, "Preci": 59, "Pow": 88, "Chin": 92},
    "Stipe Miocic": {"Cat": "HW", "Taille": "193 cm", "Allonge": "203 cm", "Coups": 4.82, "TD": 1.9, "DefLutte": 70, "Preci": 53, "Pow": 90, "Chin": 85},
    "Alexander Volkov": {"Cat": "HW", "Taille": "201 cm", "Allonge": "203 cm", "Coups": 5.10, "TD": 0.6, "DefLutte": 75, "Preci": 57, "Pow": 88, "Chin": 82},
    "Sergei Pavlovich": {"Cat": "HW", "Taille": "191 cm", "Allonge": "213 cm", "Coups": 8.20, "TD": 0.0, "DefLutte": 75, "Preci": 48, "Pow": 99, "Chin": 88},
    "Jailton Almeida": {"Cat": "HW", "Taille": "191 cm", "Allonge": "201 cm", "Coups": 2.50, "TD": 6.4, "DefLutte": 75, "Preci": 55, "Pow": 75, "Chin": 85},
    
    # LHW
    "Alex Pereira": {"Cat": "LHW", "Taille": "193 cm", "Allonge": "200 cm", "Coups": 5.10, "TD": 0.2, "DefLutte": 70, "Preci": 62, "Pow": 99, "Chin": 88},
    "Jiri Prochazka": {"Cat": "LHW", "Taille": "191 cm", "Allonge": "203 cm", "Coups": 5.75, "TD": 0.6, "DefLutte": 68, "Preci": 56, "Pow": 94, "Chin": 80},
    "Magomed Ankalaev": {"Cat": "LHW", "Taille": "191 cm", "Allonge": "191 cm", "Coups": 3.60, "TD": 1.1, "DefLutte": 86, "Preci": 53, "Pow": 89, "Chin": 92},
    "Jan Blachowicz": {"Cat": "LHW", "Taille": "188 cm", "Allonge": "198 cm", "Coups": 3.41, "TD": 1.2, "DefLutte": 70, "Preci": 49, "Pow": 92, "Chin": 93},
    "Jamahal Hill": {"Cat": "LHW", "Taille": "193 cm", "Allonge": "201 cm", "Coups": 7.31, "TD": 0.0, "DefLutte": 65, "Preci": 54, "Pow": 93, "Chin": 85},
    "Khalil Rountree Jr.": {"Cat": "LHW", "Taille": "185 cm", "Allonge": "194 cm", "Coups": 3.80, "TD": 0.0, "DefLutte": 58, "Preci": 39, "Pow": 95, "Chin": 82},

    # MW
    "Dricus Du Plessis": {"Cat": "MW", "Taille": "185 cm", "Allonge": "193 cm", "Coups": 6.49, "TD": 2.7, "DefLutte": 55, "Preci": 50, "Pow": 92, "Chin": 94},
    "Sean Strickland": {"Cat": "MW", "Taille": "185 cm", "Allonge": "193 cm", "Coups": 5.82, "TD": 1.0, "DefLutte": 85, "Preci": 41, "Pow": 78, "Chin": 92},
    "Israel Adesanya": {"Cat": "MW", "Taille": "193 cm", "Allonge": "203 cm", "Coups": 3.90, "TD": 0.1, "DefLutte": 77, "Preci": 49, "Pow": 88, "Chin": 85},
    "Robert Whittaker": {"Cat": "MW", "Taille": "183 cm", "Allonge": "185 cm", "Coups": 4.50, "TD": 0.8, "DefLutte": 82, "Preci": 42, "Pow": 85, "Chin": 80},
    "Khamzat Chimaev": {"Cat": "MW", "Taille": "188 cm", "Allonge": "191 cm", "Coups": 5.72, "TD": 4.0, "DefLutte": 100, "Preci": 59, "Pow": 90, "Chin": 90},
    "Nassourdine Imavov": {"Cat": "MW", "Taille": "191 cm", "Allonge": "191 cm", "Coups": 4.60, "TD": 1.1, "DefLutte": 76, "Preci": 54, "Pow": 82, "Chin": 88},

    # WW
    "Belal Muhammad": {"Cat": "WW", "Taille": "180 cm", "Allonge": "183 cm", "Coups": 4.55, "TD": 2.2, "DefLutte": 93, "Preci": 43, "Pow": 70, "Chin": 92},
    "Leon Edwards": {"Cat": "WW", "Taille": "183 cm", "Allonge": "188 cm", "Coups": 2.80, "TD": 1.3, "DefLutte": 70, "Preci": 53, "Pow": 85, "Chin": 88},
    "Kamaru Usman": {"Cat": "WW", "Taille": "183 cm", "Allonge": "193 cm", "Coups": 4.46, "TD": 2.8, "DefLutte": 97, "Preci": 52, "Pow": 86, "Chin": 90},
    "Shavkat Rakhmonov": {"Cat": "WW", "Taille": "185 cm", "Allonge": "196 cm", "Coups": 4.45, "TD": 1.5, "DefLutte": 100, "Preci": 59, "Pow": 91, "Chin": 95},
    "Ian Machado Garry": {"Cat": "WW", "Taille": "191 cm", "Allonge": "188 cm", "Coups": 6.67, "TD": 0.0, "DefLutte": 69, "Preci": 56, "Pow": 82, "Chin": 85},

    # LW
    "Islam Makhachev": {"Cat": "LW", "Taille": "178 cm", "Allonge": "178 cm", "Coups": 2.46, "TD": 3.2, "DefLutte": 90, "Preci": 60, "Pow": 84, "Chin": 92},
    "Charles Oliveira": {"Cat": "LW", "Taille": "178 cm", "Allonge": "188 cm", "Coups": 3.50, "TD": 2.3, "DefLutte": 55, "Preci": 53, "Pow": 90, "Chin": 78},
    "Justin Gaethje": {"Cat": "LW", "Taille": "180 cm", "Allonge": "178 cm", "Coups": 7.35, "TD": 0.1, "DefLutte": 75, "Preci": 60, "Pow": 96, "Chin": 85},
    "Dustin Poirier": {"Cat": "LW", "Taille": "175 cm", "Allonge": "183 cm", "Coups": 5.45, "TD": 1.4, "DefLutte": 63, "Preci": 51, "Pow": 91, "Chin": 88},
    "Benoit Saint Denis": {"Cat": "LW", "Taille": "180 cm", "Allonge": "185 cm", "Coups": 5.70, "TD": 4.6, "DefLutte": 68, "Preci": 54, "Pow": 86, "Chin": 85},
    "Conor McGregor": {"Cat": "LW", "Taille": "175 cm", "Allonge": "188 cm", "Coups": 5.32, "TD": 0.7, "DefLutte": 66, "Preci": 49, "Pow": 95, "Chin": 80},
    "Arman Tsarukyan": {"Cat": "LW", "Taille": "170 cm", "Allonge": "183 cm", "Coups": 3.80, "TD": 3.4, "DefLutte": 75, "Preci": 48, "Pow": 85, "Chin": 90},

    # FW
    "Ilia Topuria": {"Cat": "FW", "Taille": "170 cm", "Allonge": "175 cm", "Coups": 4.40, "TD": 1.9, "DefLutte": 92, "Preci": 46, "Pow": 97, "Chin": 95},
    "Max Holloway": {"Cat": "FW", "Taille": "180 cm", "Allonge": "175 cm", "Coups": 7.17, "TD": 0.3, "DefLutte": 84, "Preci": 48, "Pow": 75, "Chin": 99},
    "Alexander Volkanovski": {"Cat": "FW", "Taille": "168 cm", "Allonge": "180 cm", "Coups": 6.19, "TD": 1.8, "DefLutte": 70, "Preci": 57, "Pow": 86, "Chin": 90},
    "Diego Lopes": {"Cat": "FW", "Taille": "180 cm", "Allonge": "183 cm", "Coups": 3.20, "TD": 1.0, "DefLutte": 45, "Preci": 52, "Pow": 90, "Chin": 85},

    # BW
    "Sean O'Malley": {"Cat": "BW", "Taille": "180 cm", "Allonge": "183 cm", "Coups": 7.25, "TD": 0.4, "DefLutte": 65, "Preci": 61, "Pow": 93, "Chin": 88},
    "Merab Dvalishvili": {"Cat": "BW", "Taille": "168 cm", "Allonge": "173 cm", "Coups": 4.50, "TD": 6.5, "DefLutte": 80, "Preci": 45, "Pow": 70, "Chin": 95},
    "Petr Yan": {"Cat": "BW", "Taille": "170 cm", "Allonge": "170 cm", "Coups": 5.03, "TD": 1.7, "DefLutte": 85, "Preci": 53, "Pow": 87, "Chin": 95},
    "Umar Nurmagomedov": {"Cat": "BW", "Taille": "173 cm", "Allonge": "175 cm", "Coups": 4.80, "TD": 4.5, "DefLutte": 80, "Preci": 68, "Pow": 75, "Chin": 90}
}

WEIGHT_CLASSES = {"HW": 265, "LHW": 205, "MW": 185, "WW": 170, "LW": 155, "FW": 145, "BW": 135}

# --- 4. MOTEUR REALISTE (V23) ---
def get_roster(cat):
    if cat == "ALL": return sorted(list(DB.keys()))
    allowed = ["HW", "LHW"] if cat == "HW" else [cat] # Simplification filtres
    # Logique poids proches pour filtrage auto
    idx = list(WEIGHT_CLASSES.keys()).index(cat) if cat in WEIGHT_CLASSES else 0
    return sorted([k for k, v in DB.items()]) # On renvoie tout pour la version Fantasy, sinon filtrer

def fight_logic(f1, f2):
    score = 0
    reasons = []
    
    # 1. ATTRIBUTS CACHÉS (LE "TOUCH OF DEATH")
    # Pereira (99 Pow) vs Volkov (82 Chin) -> Diff 17 -> KO Danger
    ko_threat_1 = f1['Pow'] - f2['Chin']
    ko_threat_2 = f2['Pow'] - f1['Chin']
    
    if ko_threat_1 > 10: 
        score += 25 # Gros bonus pour le tueur
        reasons.append(f"{txt['reasons']['ko_power']} ({f1['Nom']})")
    elif ko_threat_1 > 0:
        score += 10
        
    if ko_threat_2 > 10:
        score -= 25
        reasons.append(f"{txt['reasons']['ko_power']} ({f2['Nom']})")
    elif ko_threat_2 > 0:
        score -= 10

    # 2. FACTEUR POIDS (REALISME)
    w1 = WEIGHT_CLASSES.get(f1['Cat'], 155)
    w2 = WEIGHT_CLASSES.get(f2['Cat'], 155)
    diff_w = w1 - w2
    
    # Si le plus léger a une puissance monstrueuse (Pereira), on ignore la pénalité de poids
    ignore_weight = (f1['Pow'] > 95 and diff_w < 0 and diff_w > -65)
    
    if not ignore_weight:
        if diff_w > 15: score += 15; reasons.append(f"{txt['reasons']['diff_w']} (+{diff_w} lbs)")
        elif diff_w < -15: score -= 15; reasons.append(f"{txt['reasons']['diff_w']} (+{abs(diff_w)} lbs)")

    # 3. LUTTE (STYLES MAKE FIGHTS)
    grap_1 = f1['TD'] * ((100 - f2['DefLutte']) / 100.0)
    grap_2 = f2['TD'] * ((100 - f1['DefLutte']) / 100.0)
    
    if grap_1 > 2.5: score += 15; reasons.append(f"{txt['reasons']['grap']} ({f1['Nom']})")
    if grap_2 > 2.5: score -= 15; reasons.append(f"{txt['reasons']['grap']} ({f2['Nom']})")

    # 4. VOLUME (Seulement si pas de danger KO immédiat)
    if abs(score) < 20: # Si combat serré, le volume compte
        vol_diff = (f1['Coups'] * f1['Preci']) - (f2['Coups'] * f2['Preci'])
        score += vol_diff * 0.5
        if vol_diff > 150: reasons.append(f"{txt['reasons']['volume']} ({f1['Nom']})")

    # RESULTAT
    final_score = 50 + score
    final_score = max(5, min(95, final_score))
    
    # CALCUL FINISH
    # Si écart puissance/menton > 10 -> KO très probable
    if ko_threat_1 > 10 or ko_threat_2 > 10: 
        ko_prob = 85
        sub_prob = 5
    elif grap_1 > 3 or grap_2 > 3:
        ko_prob = 15
        sub_prob = 60
    else:
        ko_prob = 25; sub_prob = 10
        
    dec_prob = 100 - ko_prob - sub_prob
    return int(final_score), ko_prob, sub_prob, dec_prob, reasons[:3]

# --- 5. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    .stApp { background-color: #0f172a; background-image: radial-gradient(at 50% 0%, rgba(46, 204, 113, 0.1) 0px, transparent 60%); font-family: 'Montserrat', sans-serif; }
    h1,h2,div,p{font-family:'Montserrat',sans-serif!important;}
    
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

# --- 6. UI ---
c_emp, c_logo, c_lang = st.columns([1, 6, 1])
with c_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=300)
    else:
        st.markdown("<h1 style='text-align:center; color:white;'>CAGEMETRICS <span style='color:#2ecc71'>ELITE</span></h1>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-top:-10px;'>{txt['sub']}</div>", unsafe_allow_html=True)

with c_lang:
    if st.button("🇫🇷" if st.session_state.lang == 'en' else "🇺🇸"): toggle(); st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# SELECTION
roster_list = sorted(list(DB.keys()))
c1,c2,c3=st.columns([1,0.1,1])
idx_a = roster_list.index("Alex Pereira") if "Alex Pereira" in roster_list else 0
f_a = c1.selectbox("A", roster_list, index=idx_a, label_visibility="collapsed", key="fa")
c2.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:white;'>VS</div>",unsafe_allow_html=True)
f_b = c3.selectbox("B", roster_list, index=0, label_visibility="collapsed", key="fb") # Volkov

st.markdown("<br>", unsafe_allow_html=True)

col_x, col_y, col_z = st.columns([1, 4, 1])
with col_y:
    analyze = st.button(txt['btn'], use_container_width=True)

if analyze:
    if f_a==f_b: st.warning(txt['err'])
    else:
        with st.spinner("Simulation..."):
            d1 = DB[f_a]; d1['Nom'] = f_a
            d2 = DB[f_b]; d2['Nom'] = f_b
            
            sc,k,sb,d, reasons = fight_logic(d1, d2)
            w = d1['Nom'] if sc>=50 else d2['Nom']
            cf = sc if sc>=50 else 100-sc
            
            st.markdown(f"""<div class="glass-card" style="text-align:center; border:2px solid #2ecc71; background:rgba(46, 204, 113, 0.05);"><div style="color:#94a3b8; font-size:0.7rem; font-weight:700; letter-spacing:1px; margin-bottom:5px;">{txt['win']}</div><div style="font-size:2.5rem; font-weight:900; color:white; line-height:1; margin-bottom:10px; text-transform:uppercase;">{w}</div><span style="background:#2ecc71; color:#020617; padding:4px 12px; border-radius:20px; font-weight:800; font-size:0.8rem;">{cf}% {txt['conf']}</span></div>""",unsafe_allow_html=True)
            
            if reasons:
                html_reasons = "".join([f"<span class='reason-tag'>{r}</span>" for r in reasons])
                st.markdown(f"""<div class="glass-card"><div style="text-align:center; font-weight:800; color:white; margin-bottom:10px;">{txt['keys']}</div><div style="text-align:center;">{html_reasons}</div></div>""", unsafe_allow_html=True)

            st.markdown(f"""<div class="glass-card"><div style="text-align:center; font-weight:800; color:white;">{txt['meth']}</div><div class="finish-cont"><div style="width:{k}%; background:#ef4444;"></div><div style="width:{sb}%; background:#eab308;"></div><div style="width:{d}%; background:#3b82f6;"></div></div><div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.7rem; font-weight:700;"><span style="color:#ef4444">KO/TKO {k}%</span><span style="color:#eab308">SUB {sb}%</span><span style="color:#3b82f6">DEC {d}%</span></div></div>""",unsafe_allow_html=True)
            
            st.markdown(f'<div class="glass-card"><div style="text-align:center; color:#94a3b8; font-weight:700; margin-bottom:15px;">{txt["tech"]}</div>',unsafe_allow_html=True)
            def stat_vis(l,v1,v2, max_v):
                st.markdown(f"""<div style="margin-bottom:12px;"><div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.9rem;"><span style="color:#38bdf8">{v1}</span><span style="color:#f43f5e">{v2}</span></div><div class="bar-bg"><div class="bar-l" style="width:{(v1/max_v)*100}%"></div><div class="bar-r" style="width:{(v2/max_v)*100}%"></div></div><div style="text-align:center; font-size:0.7rem; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-top:2px;">{l}</div></div>""",unsafe_allow_html=True)
            
            l=txt['lbl']
            stat_vis(l[0],d1['Pow'],d2['Pow'], 100)
            stat_vis(l[1],d1['Chin'],d2['Chin'], 100)
            stat_vis(l[2],d1['TD'],d2['TD'], 8)
            stat_vis(l[3],d1['DefLutte'],d2['DefLutte'], 100)
            stat_vis(l[4],d1['Coups'],d2['Coups'], 10)
            st.markdown('</div>',unsafe_allow_html=True)
            
            st.markdown(f"""<a href="https://www.unibet.fr/sport/mma" target="_blank" style="text-decoration:none;"><button style="width:100%; background:#fc4c02; color:white; border:none; padding:16px; border-radius:12px; font-weight:800; cursor:pointer;">{txt['cta']} {w}</button></a>""",unsafe_allow_html=True)
