import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Pro", page_icon="⚡", layout="centered")

# --- 2. GESTION LANGUE & UNITÉS (SESSION STATE) ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'fr' # Français par défaut

def toggle_lang():
    if st.session_state.lang == 'fr': st.session_state.lang = 'en'
    else: st.session_state.lang = 'fr'

# Dictionnaire Textes
T = {
    "fr": {
        "flag": "🇺🇸 EN",
        "sub": "L'outil d'analyse prédictive MMA de référence",
        "sel": "SÉLECTION DU MATCHUP",
        "btn": "LANCER L'ANALYSE",
        "win": "VAINQUEUR PRÉDIT",
        "conf": "CONFIANCE",
        "meth": "PROBABILITÉS DE FINISH",
        "tech": "COMPARATIF TECHNIQUE",
        "lbl": ["Taille", "Allonge", "Frappes/min", "Précision", "Takedowns/15m", "Déf. Lutte"],
        "cta": "PARIER SUR",
        "err": "Veuillez sélectionner deux combattants."
    },
    "en": {
        "flag": "🇫🇷 FR",
        "sub": "The Ultimate MMA Predictive Analytics Tool",
        "sel": "MATCHUP SELECTION",
        "btn": "ANALYZE FIGHT",
        "win": "PREDICTED WINNER",
        "conf": "CONFIDENCE",
        "meth": "FINISH PROBABILITY",
        "tech": "TECHNICAL BREAKDOWN",
        "lbl": ["Height", "Reach", "Strikes/min", "Accuracy", "Takedowns/15m", "Takedown Def"],
        "cta": "BET ON",
        "err": "Please select two fighters."
    }
}
txt = T[st.session_state.lang]

# --- 3. ROSTER ---
ROSTER = [
    "--- SELECT ---",
    "Alex Pereira", "Alexander Volkanovski", "Alexander Volkov", "Alexa Grasso", "Aljamain Sterling", "Amanda Nunes", "Amir Albazi", "Anderson Silva", "Anthony Smith", "Arman Tsarukyan", "Arnold Allen",
    "Belal Muhammad", "Beneil Dariush", "Benoit Saint Denis", "Bobby Green", "Bo Nickal", "Brandon Moreno", "Brandon Royval", "Brendan Allen", "Brian Ortega", "Brock Lesnar",
    "Caio Borralho", "Calvin Kattar", "Charles Oliveira", "Chris Weidman", "Ciryl Gane", "Colby Covington", "Conor McGregor", "Cory Sandhagen", "Curtis Blaydes",
    "Dan Hooker", "Daniel Cormier", "Deiveson Figueiredo", "Derrick Lewis", "Diego Lopes", "Dominick Cruz", "Dominick Reyes", "Dricus Du Plessis", "Dustin Poirier",
    "Edson Barboza", "Erin Blanchfield", "Francis Ngannou", "Georges St-Pierre", "Gilbert Burns",
    "Henry Cejudo", "Holly Holm", "Ian Machado Garry", "Ilia Topuria", "Islam Makhachev", "Israel Adesanya",
    "Jack Della Maddalena", "Jailton Almeida", "Jamahal Hill", "Jan Blachowicz", "Jared Cannonier", "Jessica Andrade", "Jiri Prochazka", "Jon Jones", "Jose Aldo", "Justin Gaethje",
    "Kamaru Usman", "Kayla Harrison", "Kevin Holland", "Khabib Nurmagomedov", "Khalil Rountree Jr.", "Khamzat Chimaev",
    "Leon Edwards", "Lerone Murphy",
    "Mackenzie Dern", "Magomed Ankalaev", "Manon Fiorot", "Marlon Vera", "Marvin Vettori", "Mateusz Gamrot", "Max Holloway", "Merab Dvalishvili", "Michael Chandler", "Michael Morales", "Michel Pereira", "Movsar Evloev", "Muhammad Mokaev",
    "Nassourdine Imavov", "Nate Diaz", "Nick Diaz",
    "Paddy Pimblett", "Paulo Costa", "Petr Yan",
    "Rafael Fiziev", "Raquel Pennington", "Renato Moicano", "Rob Font", "Robert Whittaker", "Roman Dolidze", "Rose Namajunas", "Ronda Rousey",
    "Sean O'Malley", "Sean Strickland", "Sergei Pavlovich", "Shavkat Rakhmonov", "Song Yadong", "Stephen Thompson", "Steve Erceg", "Stipe Miocic",
    "Tai Tuivasa", "Tatiana Suarez", "Tom Aspinall", "Tony Ferguson",
    "Umar Nurmagomedov",
    "Valentina Shevchenko", "Vicente Luque", "Virna Jandiroba", "Volkan Oezdemir",
    "Weili Zhang",
    "Yair Rodriguez", "Yan Xiaonan"
]

# --- 4. DATA & CONVERSION ---
BACKUP = {
    "Jon Jones": {"Taille": "6' 4\"", "Allonge": "84\"", "Coups": 4.30, "TD": 1.85, "DefLutte": 95, "Preci": 58},
    "Tom Aspinall": {"Taille": "6' 5\"", "Allonge": "78\"", "Coups": 7.72, "TD": 3.50, "DefLutte": 100, "Preci": 66},
    "Ciryl Gane": {"Taille": "6' 4\"", "Allonge": "81\"", "Coups": 5.11, "TD": 0.60, "DefLutte": 45, "Preci": 59},
    "Alex Pereira": {"Taille": "6' 4\"", "Allonge": "79\"", "Coups": 5.10, "TD": 0.20, "DefLutte": 70, "Preci": 62},
    "Ilia Topuria": {"Taille": "5' 7\"", "Allonge": "69\"", "Coups": 4.40, "TD": 1.92, "DefLutte": 92, "Preci": 46},
    "Max Holloway": {"Taille": "5' 11\"", "Allonge": "69\"", "Coups": 7.17, "TD": 0.30, "DefLutte": 84, "Preci": 48},
    "Islam Makhachev": {"Taille": "5' 10\"", "Allonge": "70\"", "Coups": 2.46, "TD": 3.17, "DefLutte": 90, "Preci": 60},
    "Benoit Saint Denis": {"Taille": "5' 11\"", "Allonge": "73\"", "Coups": 5.70, "TD": 4.55, "DefLutte": 68, "Preci": 54},
    "Dustin Poirier": {"Taille": "5' 9\"", "Allonge": "72\"", "Coups": 5.45, "TD": 1.36, "DefLutte": 63, "Preci": 51},
    "Sean O'Malley": {"Taille": "5' 11\"", "Allonge": "72\"", "Coups": 7.25, "TD": 0.40, "DefLutte": 65, "Preci": 61},
    "Conor McGregor": {"Taille": "5' 9\"", "Allonge": "74\"", "Coups": 5.32, "TD": 0.67, "DefLutte": 66, "Preci": 49},
    "Khamzat Chimaev": {"Taille": "6' 2\"", "Allonge": "75\"", "Coups": 5.72, "TD": 4.00, "DefLutte": 100, "Preci": 59}
}

def convert_to_cm(imperial_str):
    """Convertit 6' 4\" en 193 cm"""
    if not imperial_str or imperial_str == "N/A": return "-"
    try:
        clean = imperial_str.replace('"', '')
        parts = clean.split("'")
        feet = int(parts[0])
        inches = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        cm = int((feet * 30.48) + (inches * 2.54))
        return f"{cm} cm"
    except: return imperial_str

@st.cache_data
def get_data(name):
    d = None
    if name in BACKUP:
        d = BACKUP[name].copy()
        d['Nom'] = name
    else:
        try:
            url = f"http://ufcstats.com/statistics/fighters/search?query={name.replace(' ', '+')}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(r.content, 'html.parser')
            target = None
            rows = soup.find_all('tr', class_='b-statistics__table-row')
            if len(rows) > 1:
                for row in rows[1:6]:
                    link = row.find('a', href=True)
                    if link and name.lower() in link.text.strip().lower(): target = link['href']; break
                if not target: target = rows[1].find('a', href=True)['href']

            if target:
                r2 = requests.get(target, headers=headers, timeout=5)
                s2 = BeautifulSoup(r2.content, 'html.parser')
                stats = {'Nom': name, 'Taille': 'N/A', 'Allonge': 'N/A', 'Coups': 0.0, 'TD': 0.0, 'DefLutte': 0, 'Preci': 0}
                info = s2.find_all('li', class_='b-list__box-list-item')
                for i in info:
                    t = i.text.strip()
                    if "Height:" in t: stats['Taille'] = t.split(':')[1].strip()
                    if "Reach:" in t: stats['Allonge'] = t.split(':')[1].strip()
                    if "SLpM:" in t: stats['Coups'] = float(t.split(':')[1])
                    if "TD Avg.:" in t: stats['TD'] = float(t.split(':')[1])
                    if "TD Def.:" in t: stats['DefLutte'] = int(t.split(':')[1].replace('%', ''))
                    if "Str. Acc.:" in t: stats['Preci'] = int(t.split(':')[1].replace('%', ''))
                d = stats
        except: pass
    
    # Gestion Conversion Langue
    if d and st.session_state.lang == 'fr':
        d['Taille'] = convert_to_cm(d['Taille'])
        # Allonge est souvent juste en inches "84.0" ou "84"
        try:
            reach_clean = d['Allonge'].replace('"', '')
            d['Allonge'] = f"{int(float(reach_clean) * 2.54)} cm"
        except: pass
    
    return d

def calc_algo(f1, f2):
    score = 50 + (f1['Coups'] - f2['Coups']) * 5
    if f1['TD'] > 2 and f2['DefLutte'] < 60: score += 12
    if f2['TD'] > 2 and f1['DefLutte'] < 60: score -= 12
    score = max(10, min(90, score))
    
    violence = (f1['Coups'] + f2['Coups']) + (f1['TD'] + f2['TD'])*1.5
    finish = min(92, 25 + violence * 4.5)
    
    strike_r = (f1['Coups'] + f2['Coups']) / max(1, violence)
    ko = int(finish * strike_r)
    sub = int(finish * (1 - strike_r))
    dec = 100 - ko - sub
    return int(score), ko, sub, dec

# --- 5. STYLE CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    .stApp { background-color: #0f172a; font-family: 'Montserrat', sans-serif; }
    h1, h2, div, p { font-family: 'Montserrat', sans-serif !important; }
    
    /* Header Clean */
    .head-cont { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .main-title { font-weight: 900; font-size: 2rem; color: white; letter-spacing: -1px; margin:0; padding:0; }
    .lang-btn { background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; padding: 5px 10px; cursor: pointer; text-decoration: none; font-size: 0.8rem; font-weight: 700; }
    
    /* Cards */
    .glass-card { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); border-radius: 20px; padding: 24px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px; }
    
    /* Bouton */
    div.stButton > button { background: #2ecc71 !important; color: #020617 !important; border-radius: 12px; padding: 18px; font-weight: 900; text-transform: uppercase; border: none; width: 100%; }
    
    /* Bars */
    .bar-bg { width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; display: flex; margin-top: 5px; }
    .bar-l { height: 100%; background: #38bdf8; }
    .bar-r { height: 100%; background: #f43f5e; }
    .finish-cont { width: 100%; height: 14px; background: #1e293b; border-radius: 7px; overflow: hidden; display: flex; margin-top: 10px; }

</style>
""", unsafe_allow_html=True)

# --- 6. INTERFACE ---

# Header avec bouton langue manuel (Hack Streamlit)
c_title, c_lang = st.columns([5, 1])
with c_title:
    st.markdown(f"<div class='main-title'>CAGEMETRICS <span style='color:#2ecc71'>PRO</span></div>", unsafe_allow_html=True)
    st.caption(txt['sub'])
with c_lang:
    if st.button(txt['flag']):
        toggle_lang()
        st.rerun()

# Sélection
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.caption(txt['sel'])
c1, c2, c3 = st.columns([1, 0.1, 1])
idx_a = ROSTER.index("Jon Jones") if "Jon Jones" in ROSTER else 0
f_a = c1.selectbox("A", ROSTER, index=idx_a, label_visibility="collapsed")
c2.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:white;'>VS</div>", unsafe_allow_html=True)
idx_b = ROSTER.index("Tom Aspinall") if "Tom Aspinall" in ROSTER else 0
f_b = c3.selectbox("B", ROSTER, index=idx_b, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if st.button(txt['btn']):
    if f_a == "--- SELECT ---" or f_a == f_b:
        st.warning(txt['err'])
    else:
        with st.spinner("..."):
            s1 = get_data(f_a)
            s2 = get_data(f_b)
            
            if s1 and s2:
                sc, ko, sub, dec = calc_algo(s1, s2)
                winner = s1['Nom'] if sc >= 50 else s2['Nom']
                cf = sc if sc >= 50 else 100 - sc
                
                # 1. Prediction
                st.markdown(f"""
                <div class="glass-card" style="text-align:center; border:2px solid #2ecc71; background:rgba(46, 204, 113, 0.05);">
                    <div style="color:#94a3b8; font-size:0.7rem; font-weight:700; letter-spacing:1px; margin-bottom:5px;">{txt['win']}</div>
                    <div style="font-size:2.2rem; font-weight:900; color:white; line-height:1; margin-bottom:10px;">{winner}</div>
                    <span style="background:#2ecc71; color:#020617; padding:4px 12px; border-radius:20px; font-weight:800; font-size:0.8rem;">{cf}% {txt['conf']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # 2. Finish
                st.markdown(f"""
                <div class="glass-card">
                    <div style="text-align:center; font-weight:800; color:white;">{txt['meth']}</div>
                    <div class="finish-cont">
                        <div style="width:{ko}%; background:#ef4444; height:100%;"></div>
                        <div style="width:{sub}%; background:#eab308; height:100%;"></div>
                        <div style="width:{dec}%; background:#3b82f6; height:100%;"></div>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.7rem; font-weight:700;">
                        <span style="color:#ef4444">{txt['ko']} {ko}%</span>
                        <span style="color:#eab308">{txt['sub']} {sub}%</span>
                        <span style="color:#3b82f6">{txt['dec']} {dec}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 3. Stats Visuelles
                st.markdown(f'<div class="glass-card"><div style="text-align:center; color:#94a3b8; font-weight:700; margin-bottom:15px;">{txt["tech"]}</div>', unsafe_allow_html=True)
                
                def stat_vis(lbl, v1, v2, max_v):
                    # Calcul largeur barre (Blue vs Red)
                    try: 
                        v1_safe = float(v1) if isinstance(v1, (int, float)) else 0
                        v2_safe = float(v2) if isinstance(v2, (int, float)) else 0
                        tot = max(v1_safe + v2_safe, 0.1)
                        p1 = (v1_safe / tot) * 100
                        p2 = (v2_safe / tot) * 100
                    except: p1, p2 = 50, 50 # Fallback pour les strings (cm)
                    
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
                    </div>""", unsafe_allow_html=True)

                l = txt['lbl']
                stat_vis(l[0], s1['Taille'], s2['Taille'], 0) # Taille
                stat_vis(l[1], s1['Allonge'], s2['Allonge'], 0) # Allonge
                stat_vis(l[2], s1['Coups'], s2['Coups'], 10)
                stat_vis(l[3], f"{s1['Preci']}%", f"{s2['Preci']}%", 100)
                stat_vis(l[4], s1['TD'], s2['TD'], 5)
                stat_vis(l[5], f"{s1['DefLutte']}%", f"{s2['DefLutte']}%", 100)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # CTA
                st.markdown(f"""
                <a href="https://www.unibet.fr/sport/mma" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background:#fc4c02; color:white; border:none; padding:16px; border-radius:12px; font-weight:800; cursor:pointer;">
                        {txt['cta']} {winner}
                    </button>
                </a>
                """, unsafe_allow_html=True)

            else: st.error("Data error.")
