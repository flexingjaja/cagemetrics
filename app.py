import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURATION DU SAAS ---
st.set_page_config(page_title="CageMetrics Pro", page_icon="📈", layout="centered")

# --- 2. GESTION DES LANGUES (INTERNATIONALISATION) ---
# Dictionnaire de traduction
TRANS = {
    "fr": {
        "title_sub": "Outil d'analyse prédictive MMA",
        "sidebar_lang": "Langue / Language",
        "select_label": "SÉLECTION DES COMBATTANTS",
        "fighter_a": "Combattant A (Coin Bleu)",
        "fighter_b": "Combattant B (Coin Rouge)",
        "analyze_btn": "ANALYSER LE MATCHUP",
        "loading": "Récupération des données officielles...",
        "error_same": "Veuillez sélectionner deux combattants différents.",
        "error_fetch": "Données introuvables pour l'un des combattants.",
        "res_title": "PRÉDICTION DE L'ALGORITHME",
        "res_conf": "DE CONFIANCE",
        "stats_title": "COMPARATIF TECHNIQUE",
        "bar_title": "PROBABILITÉS DE FINISH",
        "ko": "KO/TKO",
        "sub": "SOUMISSION",
        "dec": "DÉCISION",
        "cta": "PARIER SUR",
        "ad_disclaimer": "Les cotes peuvent varier. Jouez responsablement.",
        "stats_labels": ["Taille", "Allonge", "Frappes/min", "Précision", "Takedowns/15m", "Défense Lutte"]
    },
    "en": {
        "title_sub": "Professional MMA Predictive Analytics",
        "sidebar_lang": "Language",
        "select_label": "FIGHTER SELECTION",
        "fighter_a": "Fighter A (Blue Corner)",
        "fighter_b": "Fighter B (Red Corner)",
        "analyze_btn": "ANALYZE MATCHUP",
        "loading": "Fetching official data...",
        "error_same": "Please select two different fighters.",
        "error_fetch": "Data unavailable for one of the fighters.",
        "res_title": "ALGORITHM PREDICTION",
        "res_conf": "CONFIDENCE SCORE",
        "stats_title": "TECHNICAL BREAKDOWN",
        "bar_title": "FINISH PROBABILITIES",
        "ko": "KO/TKO",
        "sub": "SUBMISSION",
        "dec": "DECISION",
        "cta": "BET ON",
        "ad_disclaimer": "Odds subject to change. Gamble responsibly.",
        "stats_labels": ["Height", "Reach", "Strikes/min", "Accuracy", "Takedowns/15m", "Takedown Def"]
    }
}

# Sélecteur de langue dans la Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    lang_choice = st.radio("Language", ["English 🇺🇸", "Français 🇫🇷"], index=0) # Anglais par défaut pour le business
    lang = "en" if "English" in lang_choice else "fr"
    t = TRANS[lang] # On charge le dictionnaire de la langue choisie

# --- 3. ROSTER UNIFIÉ (Ordre Alphabétique) ---
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

# --- 4. DATA BACKEND (MOTEUR) ---
# Backup Data pour éviter les crashs sur les stars
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

@st.cache_data
def get_fighter_data(name):
    if name in BACKUP:
        d = BACKUP[name]
        d['Nom'] = name
        return d
    
    try:
        url = f"http://ufcstats.com/statistics/fighters/search?query={name.replace(' ', '+')}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        target = None
        rows = soup.find_all('tr', class_='b-statistics__table-row')
        if len(rows) > 1:
            for row in rows[1:6]:
                link = row.find('a', href=True)
                if link and name.lower() in link.text.strip().lower():
                    target = link['href']; break
            if not target: target = rows[1].find('a', href=True)['href']

        if target:
            r2 = requests.get(target, headers=headers, timeout=5)
            s2 = BeautifulSoup(r2.content, 'html.parser')
            stats = {'Nom': name, 'Taille': '-', 'Allonge': '-', 'Coups': 0.0, 'TD': 0.0, 'DefLutte': 0, 'Preci': 0}
            
            info = s2.find_all('li', class_='b-list__box-list-item')
            for i in info:
                txt = i.text.strip()
                if "Height:" in txt: stats['Taille'] = txt.split(':')[1].strip()
                if "Reach:" in txt: stats['Allonge'] = txt.split(':')[1].strip()
                if "SLpM:" in txt: stats['Coups'] = float(txt.split(':')[1])
                if "TD Avg.:" in txt: stats['TD'] = float(txt.split(':')[1])
                if "TD Def.:" in txt: stats['DefLutte'] = int(txt.split(':')[1].replace('%', ''))
                if "Str. Acc.:" in txt: stats['Preci'] = int(txt.split(':')[1].replace('%', ''))
            return stats
    except: return None
    return None

def calculate_algorithm(s1, s2):
    # Score de base
    score = 50 + (s1['Coups'] - s2['Coups']) * 5
    # Bonus Lutte
    if s1['TD'] > 2.0 and s2['DefLutte'] < 60: score += 12
    if s2['TD'] > 2.0 and s1['DefLutte'] < 60: score -= 12
    # Bornage
    score = max(10, min(90, score))
    
    # Finish Probs
    violence = (s1['Coups'] + s2['Coups']) + (s1['TD'] + s2['TD'])*1.5
    finish_chance = min(92, 25 + violence * 4.5)
    
    strike_ratio = (s1['Coups'] + s2['Coups']) / max(1, violence)
    ko = int(finish_chance * strike_ratio)
    sub = int(finish_chance * (1 - strike_ratio))
    dec = 100 - ko - sub
    
    return int(score), ko, sub, dec

# --- 5. CSS STYLING (THEME RUNNATIC) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    
    .stApp {
        background-color: #0f172a;
        background-image: radial-gradient(at 50% 0%, rgba(46, 204, 113, 0.1) 0px, transparent 60%);
        font-family: 'Montserrat', sans-serif;
    }
    
    h1, h2, div, span, p { font-family: 'Montserrat', sans-serif !important; }

    /* Inputs */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px;
    }

    /* Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 30px -5px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }

    /* Bouton */
    div.stButton > button {
        background: #2ecc71 !important;
        color: #020617 !important;
        border-radius: 12px !important;
        padding: 18px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        border: none !important;
        box-shadow: 0 5px 15px rgba(46, 204, 113, 0.3) !important;
        transition: 0.2s !important;
    }
    div.stButton > button:hover { transform: translateY(-2px); filter: brightness(1.1); }

    /* Prediction */
    .winner-text { font-size: 2.2rem; font-weight: 900; color: white; text-transform: uppercase; margin: 10px 0; line-height: 1; }
    .conf-badge { background: #2ecc71; color: #020617; padding: 5px 15px; border-radius: 50px; font-weight: 800; font-size: 0.8rem; }

    /* Stats Bars */
    .bar-container { width: 100%; height: 12px; background: #334155; border-radius: 6px; overflow: hidden; display: flex; margin-top: 10px; }
    .legend-text { display: flex; justify-content: space-between; font-size: 0.7rem; color: #94a3b8; font-weight: 700; margin-top: 5px; }
    
    /* Betting Button */
    .bet-btn {
        display: block; width: 100%; text-align: center; background: #fc4c02; color: white;
        padding: 16px; border-radius: 12px; font-weight: 800; text-decoration: none; text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(252, 76, 2, 0.4); transition: 0.2s;
    }
    .bet-btn:hover { background: #ea4402; transform: translateY(-2px); color: white; }

</style>
""", unsafe_allow_html=True)

# --- 6. FRONTEND ---

st.markdown(f"<h1 style='text-align:center; color:white; margin-bottom:5px;'>CAGEMETRICS <span style='color:#2ecc71'>PRO</span></h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-bottom:25px;'>{t['title_sub']}</p>", unsafe_allow_html=True)

# SÉLECTION
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown(f"<div style='font-size:0.75rem; color:#94a3b8; font-weight:700; margin-bottom:15px; letter-spacing:1px;'>{t['select_label']}</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 0.1, 1])
with c1: 
    # Index par défaut sur Jon Jones (si dispo) sinon 0
    idx_a = ROSTER.index("Jon Jones") if "Jon Jones" in ROSTER else 0
    f_a = st.selectbox(t['fighter_a'], ROSTER, index=idx_a, key="fa")
with c3: 
    # Index par défaut sur Tom Aspinall
    idx_b = ROSTER.index("Tom Aspinall") if "Tom Aspinall" in ROSTER else 1
    f_b = st.selectbox(t['fighter_b'], ROSTER, index=idx_b, key="fb")
st.markdown('</div>', unsafe_allow_html=True)

# BOUTON ANALYSE
if st.button(t['analyze_btn'], use_container_width=True):
    if f_a == "--- SELECT ---" or f_b == "--- SELECT ---":
        st.warning(t['error_same'])
    elif f_a == f_b:
        st.warning(t['error_same'])
    else:
        with st.spinner(t['loading']):
            s1 = get_fighter_data(f_a)
            s2 = get_fighter_data(f_b)
            
            if s1 and s2:
                # --- CALCULS ---
                score, ko, sub, dec = calculate_algorithm(s1, s2)
                winner = s1['Nom'] if score >= 50 else s2['Nom']
                conf = score if score >= 50 else 100 - score
                
                # --- RÉSULTATS ---
                
                # 1. Prediction Card
                st.markdown(f"""
                <div class="glass-card" style="text-align:center; border:2px solid #2ecc71; background:rgba(46, 204, 113, 0.05);">
                    <div style="color:#94a3b8; font-size:0.7rem; font-weight:700; letter-spacing:1px; margin-bottom:5px;">{t['res_title']}</div>
                    <div class="winner-text">{winner}</div>
                    <span class="conf-badge">{conf}% {t['res_conf']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # 2. Finish Probabilities
                st.markdown(f"""
                <div class="glass-card">
                    <div style="text-align:center; font-weight:800; color:white; margin-bottom:5px;">{t['bar_title']}</div>
                    <div class="bar-container">
                        <div style="width:{ko}%; background:#ef4444; height:100%;"></div>
                        <div style="width:{sub}%; background:#eab308; height:100%;"></div>
                        <div style="width:{dec}%; background:#3b82f6; height:100%;"></div>
                    </div>
                    <div class="legend-text">
                        <span style="color:#ef4444">{t['ko']} {ko}%</span>
                        <span style="color:#eab308">{t['sub']} {sub}%</span>
                        <span style="color:#3b82f6">{t['dec']} {dec}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 3. Stats Compare
                st.markdown(f'<div class="glass-card"><div style="text-align:center; font-weight:700; color:#94a3b8; margin-bottom:15px;">{t["stats_title"]}</div>', unsafe_allow_html=True)
                
                lbls = t['stats_labels'] # [Taille, Allonge, Frappes...]
                
                def stat_line(l, v1, v2):
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                        <span style="color:#38bdf8; font-weight:700;">{v1}</span>
                        <span style="color:#94a3b8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">{l}</span>
                        <span style="color:#f43f5e; font-weight:700;">{v2}</span>
                    </div>""", unsafe_allow_html=True)
                
                stat_line(lbls[0], s1['Taille'], s2['Taille'])
                stat_line(lbls[1], s1['Allonge'], s2['Allonge'])
                stat_line(lbls[2], s1['Coups'], s2['Coups'])
                stat_line(lbls[3], f"{s1['Preci']}%", f"{s2['Preci']}%")
                stat_line(lbls[4], s1['TD'], s2['TD'])
                stat_line(lbls[5], f"{s1['DefLutte']}%", f"{s2['DefLutte']}%")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 4. ADS / AFFILIATION (PLACEHOLDERS)
                st.markdown(f"""
                <a href="https://www.unibet.com" target="_blank" class="bet-btn">
                    {t['cta']} {winner}
                </a>
                <p style="text-align:center; color:#64748b; font-size:0.6rem; margin-top:10px;">
                    {t['ad_disclaimer']}
                </p>
                """, unsafe_allow_html=True)
            
            else:
                st.error(t['error_fetch'])
