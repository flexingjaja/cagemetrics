import streamlit as st
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Pro", page_icon="🦁", layout="centered")

# --- 2. GESTION SESSION ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'fr'

def toggle_lang():
    if st.session_state.lang == 'fr': st.session_state.lang = 'en'
    else: st.session_state.lang = 'fr'

T = {
    "fr": {
        "sub": "L'outil gratuit d'analyse pour parieurs malins",
        "btn": "LANCER L'ANALYSE",
        "win": "VAINQUEUR PROBABLE",
        "conf": "CONFIANCE",
        "meth": "TYPE DE VICTOIRE",
        "tech": "COMPARATIF",
        "lbl": ["Puissance", "Lutte", "Résistance", "Cardio", "Expérience", "Déf. Lutte"],
        "cta_main": "PARIER SUR",
        "cta_sub": "🎁 100€ de Bonus Offerts ICI",
        "err": "Choisis deux combattants différents.",
        "reasons": {
            "tier": "NIVEAU SUPÉRIEUR (P4P)",
            "style": "STYLE DOMINANT (SAMBO)",
            "str": "AVANTAGE STRIKING",
            "grap": "AVANTAGE LUTTE",
            "cardio": "MEILLEUR CARDIO",
            "phys": "ALLONGE SUPÉRIEURE"
        }
    },
    "en": {
        "sub": "Free Smart Betting Analysis Tool",
        "btn": "GET PREDICTION",
        "win": "PREDICTED WINNER",
        "conf": "CONFIDENCE",
        "meth": "WINNING METHOD",
        "tech": "COMPARISON",
        "lbl": ["Power", "Grappling", "Chin", "Cardio", "Experience", "Takedown Def"],
        "cta_main": "BET ON",
        "cta_sub": "🎁 Get $100 Free Bonus HERE",
        "err": "Select two different fighters.",
        "reasons": {
            "tier": "LEVEL GAP (P4P)",
            "style": "DOMINANT STYLE",
            "str": "STRIKING EDGE",
            "grap": "GRAPPLING EDGE",
            "cardio": "CARDIO EDGE",
            "phys": "REACH ADVANTAGE"
        }
    }
}
txt = T[st.session_state.lang]

# --- 3. DATABASE (DATA FIABLES) ---
DB = {
    "Jon Jones":        {"Cat": "HW", "Tier": 1, "Style": "GOAT", "Taille": 193, "Allonge": 215, "Str": 88, "Grap": 98, "Chin": 98, "Cardio": 95, "XP": 100, "DefLutte": 95},
    "Tom Aspinall":     {"Cat": "HW", "Tier": 2, "Style": "Hybrid", "Taille": 196, "Allonge": 198, "Str": 96, "Grap": 85, "Chin": 90, "Cardio": 85, "XP": 88, "DefLutte": 100},
    "Ciryl Gane":       {"Cat": "HW", "Tier": 3, "Style": "Striker", "Taille": 193, "Allonge": 206, "Str": 95, "Grap": 60, "Chin": 90, "Cardio": 90, "XP": 85, "DefLutte": 45},
    "Stipe Miocic":     {"Cat": "HW", "Tier": 2, "Style": "Wrestler", "Taille": 193, "Allonge": 203, "Str": 85, "Grap": 88, "Chin": 80, "Cardio": 80, "XP": 98, "DefLutte": 70},
    "Francis Ngannou":  {"Cat": "HW", "Tier": 1, "Style": "Power", "Taille": 193, "Allonge": 211, "Str": 98, "Grap": 75, "Chin": 99, "Cardio": 75, "XP": 90, "DefLutte": 70},
    
    "Alex Pereira":     {"Cat": "LHW", "Tier": 1, "Style": "Kickboxer", "Taille": 193, "Allonge": 200, "Str": 99, "Grap": 60, "Chin": 85, "Cardio": 88, "XP": 92, "DefLutte": 70},
    "Jiri Prochazka":   {"Cat": "LHW", "Tier": 2, "Style": "Chaos", "Taille": 191, "Allonge": 203, "Str": 94, "Grap": 70, "Chin": 75, "Cardio": 95, "XP": 85, "DefLutte": 68},
    "Magomed Ankalaev": {"Cat": "LHW", "Tier": 2, "Style": "Dagestani", "Taille": 191, "Allonge": 191, "Str": 85, "Grap": 92, "Chin": 90, "Cardio": 90, "XP": 88, "DefLutte": 86},

    "Dricus Du Plessis":{"Cat": "MW", "Tier": 2, "Style": "Brawler", "Taille": 185, "Allonge": 193, "Str": 88, "Grap": 85, "Chin": 95, "Cardio": 98, "XP": 88, "DefLutte": 55},
    "Sean Strickland":  {"Cat": "MW", "Tier": 2, "Style": "Boxer", "Taille": 185, "Allonge": 193, "Str": 90, "Grap": 70, "Chin": 92, "Cardio": 100, "XP": 90, "DefLutte": 85},
    "Israel Adesanya":  {"Cat": "MW", "Tier": 1, "Style": "Sniper", "Taille": 193, "Allonge": 203, "Str": 98, "Grap": 65, "Chin": 85, "Cardio": 92, "XP": 98, "DefLutte": 77},
    "Khamzat Chimaev":  {"Cat": "MW", "Tier": 1, "Style": "Wrestler", "Taille": 188, "Allonge": 191, "Str": 80, "Grap": 99, "Chin": 90, "Cardio": 80, "XP": 85, "DefLutte": 100},

    "Belal Muhammad":   {"Cat": "WW", "Tier": 2, "Style": "Pressure", "Taille": 180, "Allonge": 183, "Str": 78, "Grap": 92, "Chin": 92, "Cardio": 98, "XP": 94, "DefLutte": 93},
    "Shavkat Rakhmonov":{"Cat": "WW", "Tier": 1, "Style": "Finisher", "Taille": 185, "Allonge": 196, "Str": 90, "Grap": 95, "Chin": 95, "Cardio": 95, "XP": 90, "DefLutte": 100},
    "Kamaru Usman":     {"Cat": "WW", "Tier": 2, "Style": "Wrestler", "Taille": 183, "Allonge": 193, "Str": 82, "Grap": 94, "Chin": 88, "Cardio": 90, "XP": 96, "DefLutte": 97},
    "Leon Edwards":     {"Cat": "WW", "Tier": 2, "Style": "Sniper", "Taille": 183, "Allonge": 188, "Str": 94, "Grap": 80, "Chin": 88, "Cardio": 90, "XP": 92, "DefLutte": 70},

    "Islam Makhachev":  {"Cat": "LW", "Tier": 1, "Style": "Sambo", "Taille": 178, "Allonge": 178, "Str": 85, "Grap": 99, "Chin": 92, "Cardio": 96, "XP": 98, "DefLutte": 90},
    "Arman Tsarukyan":  {"Cat": "LW", "Tier": 2, "Style": "Wrestler", "Taille": 170, "Allonge": "183", "Str": 85, "Grap": 94, "Chin": 90, "Cardio": 95, "XP": 88, "DefLutte": 75},
    "Charles Oliveira": {"Cat": "LW", "Tier": 2, "Style": "BJJ", "Taille": 178, "Allonge": 188, "Str": 90, "Grap": 98, "Chin": 75, "Cardio": 85, "XP": 94, "DefLutte": 55},
    "Justin Gaethje":   {"Cat": "LW", "Tier": 2, "Style": "Brawler", "Taille": 180, "Allonge": "178", "Str": 96, "Grap": 75, "Chin": 80, "Cardio": 88, "XP": 90, "DefLutte": 75},
    "Dustin Poirier":   {"Cat": "LW", "Tier": 2, "Style": "Boxer", "Taille": 175, "Allonge": "183", "Str": 94, "Grap": 70, "Chin": 88, "Cardio": 90, "XP": 96, "DefLutte": 63},
    "Conor McGregor":   {"Cat": "LW", "Tier": 3, "Style": "Sniper", "Taille": 175, "Allonge": "188", "Str": 95, "Grap": 60, "Chin": 80, "Cardio": 60, "XP": 92, "DefLutte": 66},
    "Benoit Saint Denis":{"Cat": "LW", "Tier": 3, "Style": "War", "Taille": 180, "Allonge": "185", "Str": 85, "Grap": 88, "Chin": 85, "Cardio": 90, "XP": 80, "DefLutte": 68},

    "Ilia Topuria":     {"Cat": "FW", "Tier": 1, "Style": "Boxer-Wrestler", "Taille": 170, "Allonge": 175, "Str": 97, "Grap": 88, "Chin": 98, "Cardio": 92, "XP": 90, "DefLutte": 92},
    "Max Holloway":     {"Cat": "FW", "Tier": 1, "Style": "Volume", "Taille": 180, "Allonge": "175", "Str": 95, "Grap": 75, "Chin": 100, "Cardio": 99, "XP": 98, "DefLutte": 84},
    "Alex Volkanovski": {"Cat": "FW", "Tier": 2, "Style": "Complete", "Taille": 168, "Allonge": "180", "Str": 92, "Grap": 88, "Chin": 85, "Cardio": 95, "XP": 99, "DefLutte": 70},
    
    "Sean O'Malley":    {"Cat": "BW", "Tier": 2, "Style": "Sniper", "Taille": 180, "Allonge": "183", "Str": 98, "Grap": 65, "Chin": 88, "Cardio": 90, "XP": 88, "DefLutte": 65},
    "Merab Dvalishvili":{"Cat": "BW", "Tier": 1, "Style": "Machine", "Taille": 168, "Allonge": "173", "Str": 75, "Grap": 99, "Chin": 95, "Cardio": 100, "XP": 90, "DefLutte": 80},
    "Umar Nurmagomedov":{"Cat": "BW", "Tier": 2, "Style": "Dagestani", "Taille": 173, "Allonge": "175", "Str": 88, "Grap": 95, "Chin": 90, "Cardio": 92, "XP": 85, "DefLutte": 80}
}

WEIGHT_MAP = ["BW", "FW", "LW", "WW", "MW", "LHW", "HW"]

# --- 4. ALGO ---
def analyze_fight(f1, f2):
    score = 0
    reasons = []
    
    # 1. TIER
    tier_diff = f2['Tier'] - f1['Tier'] 
    if tier_diff > 0: score += 20; reasons.append(f"{txt['reasons']['tier']} ({f1['Nom']})")
    elif tier_diff < 0: score -= 20; reasons.append(f"{txt['reasons']['tier']} ({f2['Nom']})")

    # 2. STYLE
    if ("Sambo" in f1['Style'] or "Dagestani" in f1['Style']) and f2['DefLutte'] < 95:
        score += 15; reasons.append(f"{txt['reasons']['style']} ({f1['Nom']})")
    elif ("Sambo" in f2['Style'] or "Dagestani" in f2['Style']) and f1['DefLutte'] < 95:
        score -= 15; reasons.append(f"{txt['reasons']['style']} ({f2['Nom']})")

    # 3. STATS
    if f1['Str'] > f2['Str'] + 8: score += 5; reasons.append(f"{txt['reasons']['str']} ({f1['Nom']})")
    elif f2['Str'] > f1['Str'] + 8: score -= 5; reasons.append(f"{txt['reasons']['str']} ({f2['Nom']})")
    
    if f1['Grap'] > f2['Grap'] + 10: score += 8; reasons.append(f"{txt['reasons']['grap']} ({f1['Nom']})")
    elif f2['Grap'] > f1['Grap'] + 10: score -= 8; reasons.append(f"{txt['reasons']['grap']} ({f2['Nom']})")
    
    if f1['Cardio'] > f2['Cardio'] + 10: score += 5; reasons.append(f"{txt['reasons']['cardio']} ({f1['Nom']})")
    elif f2['Cardio'] > f1['Cardio'] + 10: score -= 5; reasons.append(f"{txt['reasons']['cardio']} ({f2['Nom']})")

    # 4. PHYSIQUE
    if f1['Allonge'] > f2['Allonge'] + 7: score += 5; reasons.append(f"{txt['reasons']['phys']} (+{f1['Allonge']-f2['Allonge']}cm)")
    elif f2['Allonge'] > f1['Allonge'] + 7: score -= 5; reasons.append(f"{txt['reasons']['phys']} (+{f2['Allonge']-f1['Allonge']}cm)")

    final_score = max(10, min(90, 50 + score))
    
    # Method
    diff_grap = f1['Grap'] - f2['Grap']
    if abs(diff_grap) > 15: ko=10; sub=50; dec=40
    elif f1['Str']>90 and f2['Str']>90: ko=65; sub=5; dec=30
    else: ko=30; sub=15; dec=55
        
    return int(final_score), ko, sub, dec, reasons[:3]

# --- 5. CSS (STYLE PREMIUM & BOUTON BG) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    
    /* FOND */
    .stApp { background-color: #0f172a; background-image: radial-gradient(at 50% 0%, rgba(46, 204, 113, 0.1) 0px, transparent 60%); font-family: 'Montserrat', sans-serif; }
    h1, h2, div, p { font-family: 'Montserrat', sans-serif !important; }

    /* LOGO */
    .logo-container { display: flex; justify-content: center; padding-bottom: 20px; }
    
    /* CARTES */
    .glass-card { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); border-radius: 20px; padding: 20px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px; box-shadow: 0 10px 30px -5px rgba(0,0,0,0.4); }
    
    /* BOUTON ANALYSE (Bleu/Standard) */
    div.stButton > button { background: #3b82f6; color: white; border-radius: 12px; padding: 16px; font-weight: 800; border: none; width: 100%; text-transform: uppercase; transition:0.3s; }
    div.stButton > button:hover { transform: translateY(-2px); filter: brightness(1.1); }
    
    /* BOUTON AFFILIATION (GOLDEN TICKET) */
    .affiliate-btn {
        display: block; width: 100%; text-align: center;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); /* Gold Gradient */
        color: white !important; 
        padding: 22px; border-radius: 16px; text-decoration: none; font-weight: 900;
        text-transform: uppercase; letter-spacing: 1px; 
        box-shadow: 0 0 25px rgba(245, 158, 11, 0.4); /* Glowing Gold Shadow */
        border: 2px solid rgba(255,255,255,0.2);
        margin-top: 15px; transition: all 0.3s ease-in-out;
        position: relative; overflow: hidden;
    }
    .affiliate-btn:hover { 
        transform: scale(1.03) translateY(-3px); 
        box-shadow: 0 0 40px rgba(245, 158, 11, 0.6);
        background: linear-gradient(135deg, #fbbf24 0%, #b45309 100%);
    }
    .affiliate-btn::before {
        content: ""; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: 0.5s;
    }
    .affiliate-btn:hover::before { left: 100%; }
    
    .cta-title { font-size: 1.3rem; display: block; margin-bottom: 5px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .cta-sub { font-size: 0.85rem; font-weight: 600; display: block; opacity: 0.95; background: rgba(0,0,0,0.15); padding: 4px 10px; border-radius: 20px; width: fit-content; margin: 0 auto; }

    /* STATS BARS */
    .bar-bg { width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; display: flex; margin-top: 5px; }
    .bar-l { height: 100%; background: #38bdf8; } .bar-r { height: 100%; background: #f43f5e; }
    .finish-cont { width: 100%; height: 14px; background: #1e293b; border-radius: 7px; overflow: hidden; display: flex; margin-top: 10px; }
    .tag-reason { background: rgba(255,255,255,0.1); padding: 5px 10px; border-radius: 8px; font-size: 0.75rem; color: #cbd5e1; display: inline-block; margin: 3px; border: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 6. UI ---

# 1. HEADER (LOGO CENTRÉ)
if os.path.exists("logo.png"):
    st.markdown("""<div class="logo-container">""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("logo.png", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align:center; color:white;'>CAGEMETRICS</h1>", unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-top:-20px;'>{txt['sub']}</div>", unsafe_allow_html=True)

# Bouton Langue
c_void, c_lang = st.columns([6, 1])
with c_lang:
    if st.button("🇫🇷/🇺🇸", key="btn_lang"): toggle_lang(); st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# 2. SELECTEURS
cats_map = {"Heavyweight": "HW", "Light Heavyweight": "LHW", "Middleweight": "MW", "Welterweight": "WW", "Lightweight": "LW", "Featherweight": "FW", "Bantamweight": "BW", "Show All": "ALL"}
cat_name = st.selectbox("", list(cats_map.keys()), label_visibility="collapsed")
cat_code = cats_map[cat_name]

WEIGHT_MAP = ["BW", "FW", "LW", "WW", "MW", "LHW", "HW"]
if cat_code == "ALL": roster = sorted(list(DB.keys()))
else:
    try: idx = WEIGHT_MAP.index(cat_code); allowed = [WEIGHT_MAP[i] for i in range(max(0,idx-1), min(len(WEIGHT_MAP),idx+2))]
    except: allowed = [cat_code]
    roster = sorted([n for n, d in DB.items() if d['Cat'] in allowed])

c_a, c_vs, c_b = st.columns([1, 0.1, 1])
f_a = c_a.selectbox("A", roster, index=0, label_visibility="collapsed", key="fa")
c_vs.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:white;'>VS</div>", unsafe_allow_html=True)
f_b = c_b.selectbox("B", roster, index=1 if len(roster)>1 else 0, label_visibility="collapsed", key="fb")

st.markdown("<br>", unsafe_allow_html=True)

# 3. ACTION
_, c_run, _ = st.columns([1, 2, 1])
run = c_run.button(txt['btn'], use_container_width=True)

if run:
    if f_a == f_b: st.warning(txt['err'])
    else:
        with st.spinner("Analyse des datas..."):
            d1 = DB[f_a].copy(); d1['Nom'] = f_a
            d2 = DB[f_b].copy(); d2['Nom'] = f_b
            
            sc, k, s, d, reasons = analyze_fight(d1, d2)
            w = d1['Nom'] if sc >= 50 else d2['Nom']
            cf = sc if sc >= 50 else 100 - sc
            
            # WINNER
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; border:2px solid #2ecc71; background:rgba(46, 204, 113, 0.05);">
                <div style="color:#94a3b8; font-size:0.7rem; font-weight:700; letter-spacing:1px; margin-bottom:5px;">{txt['win']}</div>
                <div style="font-size:2.5rem; font-weight:900; color:white; line-height:1; margin-bottom:10px; text-transform:uppercase;">{w}</div>
                <span style="background:#2ecc71; color:#020617; padding:5px 15px; border-radius:50px; font-weight:800; font-size:0.9rem;">{cf}% {txt['conf']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # REASONS
            if reasons:
                html_r = "".join([f"<div class='tag-reason'>{r}</div>" for r in reasons])
                st.markdown(f"""<div class="glass-card" style="text-align:center;">{html_r}</div>""", unsafe_allow_html=True)
            
            # METHODE
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
            
            # STATS
            st.markdown(f'<div class="glass-card"><div style="text-align:center; color:#94a3b8; font-weight:700; margin-bottom:15px;">{txt["tech"]}</div>', unsafe_allow_html=True)
            def draw_bar(label, v1, v2, max_v=100):
                p1 = (v1 / max_v) * 100; p2 = (v2 / max_v) * 100
                st.markdown(f"""<div style="margin-bottom:12px;"><div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.9rem;"><span style="color:#38bdf8">{v1}</span><span style="color:#f43f5e">{v2}</span></div><div class="bar-bg"><div class="bar-l" style="width:{p1}%"></div><div class="bar-r" style="width:{p2}%"></div></div><div style="text-align:center; font-size:0.65rem; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-top:2px;">{label}</div></div>""", unsafe_allow_html=True)
            
            l = txt['lbl']
            # MAPPING OK
            draw_bar(l[0], d1['Str'], d2['Str'])
            draw_bar(l[1], d1['Grap'], d2['Grap'])
            draw_bar(l[2], d1['Chin'], d2['Chin'])
            draw_bar(l[3], d1['Cardio'], d2['Cardio'])
            draw_bar(l[4], d1['XP'], d2['XP'])
            draw_bar(l[5], d1['DefLutte'], d2['DefLutte'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # CTA AFFILIATION (GOLDEN TICKET)
            st.markdown(f"""
            <a href="https://www.unibet.fr/sport/mma" target="_blank" class="affiliate-btn">
                <span class="cta-title">{txt['cta_main']} {w}</span>
                <span class="cta-sub">{txt['cta_sub']}</span>
            </a>
            """, unsafe_allow_html=True)
