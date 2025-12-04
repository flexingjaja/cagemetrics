import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GetCageMetrics Pro", page_icon="⚡", layout="centered")

# --- 2. DATA : LE ROSTER CLASSÉ (TOP 15 + STARS) ---
ROSTER = {
    "🏆 P4P / Superstars": [
        "Islam Makhachev", "Jon Jones", "Alex Pereira", "Ilia Topuria", "Sean O'Malley", 
        "Conor McGregor", "Max Holloway", "Charles Oliveira", "Dustin Poirier", "Justin Gaethje",
        "Alexander Volkanovski", "Khamzat Chimaev", "Israel Adesanya"
    ],
    "Poids Lourds (Heavyweight)": [
        "Jon Jones", "Tom Aspinall", "Ciryl Gane", "Sergei Pavlovich", "Curtis Blaydes", 
        "Jailton Almeida", "Alexander Volkov", "Stipe Miocic", "Tai Tuivasa", "Jairzinho Rozenstruik",
        "Serghei Spivac", "Derrick Lewis", "Marcos Rogerio de Lima", "Rodrigo Nascimento", "Alexandr Romanov"
    ],
    "Poids Mi-Lourds (Light Heavyweight)": [
        "Alex Pereira", "Jiri Prochazka", "Magomed Ankalaev", "Jan Blachowicz", "Jamahal Hill",
        "Aleksandar Rakic", "Nikita Krylov", "Khalil Rountree Jr.", "Volkan Oezdemir", "Johnny Walker",
        "Anthony Smith", "Dominick Reyes", "Azamat Murzakanov", "Vitor Petrino", "Alonzo Menifield"
    ],
    "Poids Moyens (Middleweight)": [
        "Dricus Du Plessis", "Sean Strickland", "Israel Adesanya", "Robert Whittaker", "Nassourdine Imavov",
        "Jared Cannonier", "Marvin Vettori", "Brendan Allen", "Paulo Costa", "Jack Hermansson",
        "Khamzat Chimaev", "Roman Dolidze", "Caio Borralho", "Anthony Hernandez", "Michel Pereira"
    ],
    "Poids Mi-Moyens (Welterweight)": [
        "Belal Muhammad", "Leon Edwards", "Kamaru Usman", "Shavkat Rakhmonov", "Jack Della Maddalena",
        "Gilbert Burns", "Ian Machado Garry", "Sean Brady", "Stephen Thompson", "Geoff Neal",
        "Vicente Luque", "Kevin Holland", "Michael Morales", "Rinat Fakhretdinov", "Joaquin Buckley"
    ],
    "Poids Légers (Lightweight)": [
        "Islam Makhachev", "Arman Tsarukyan", "Charles Oliveira", "Justin Gaethje", "Dustin Poirier",
        "Michael Chandler", "Mateusz Gamrot", "Beneil Dariush", "Rafael Fiziev", "Benoit Saint Denis",
        "Dan Hooker", "Renato Moicano", "Jalin Turner", "Bobby Green", "Paddy Pimblett"
    ],
    "Poids Plumes (Featherweight)": [
        "Ilia Topuria", "Alexander Volkanovski", "Max Holloway", "Brian Ortega", "Yair Rodriguez",
        "Movsar Evloev", "Arnold Allen", "Josh Emmett", "Calvin Kattar", "Giga Chikadze",
        "Diego Lopes", "Bryce Mitchell", "Lerone Murphy", "Edson Barboza", "Dan Ige"
    ],
    "Poids Coqs (Bantamweight)": [
        "Sean O'Malley", "Merab Dvalishvili", "Cory Sandhagen", "Petr Yan", "Marlon Vera",
        "Henry Cejudo", "Deiveson Figueiredo", "Song Yadong", "Rob Font", "Mario Bautista",
        "Umar Nurmagomedov", "Jonathan Martinez", "Dominick Cruz", "Jose Aldo", "Kyler Phillips"
    ]
}

# --- 3. CSS "RUNNATIC ULTIMATE" ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    :root {
        --bg-dark: #020617;
        --card-bg: rgba(30, 41, 59, 0.7);
        --primary: #2ecc71;
        --secondary: #38bdf8; /* Bleu Cyan */
        --accent: #f43f5e; /* Rouge Rose */
        --gold: #fbbf24;
    }

    .stApp {
        background-color: var(--bg-dark);
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(46, 204, 113, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 100% 100%, rgba(56, 189, 248, 0.15) 0%, transparent 50%);
        font-family: 'Montserrat', sans-serif;
    }

    h1, h2, h3, p, span, div { font-family: 'Montserrat', sans-serif !important; }

    /* Inputs stylisés */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        font-weight: 600;
    }

    /* Cards Glassmorphism */
    .glass-card {
        background: var(--card-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 24px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }

    /* Bouton Principal */
    div.stButton > button {
        background: linear-gradient(135deg, #2ecc71 0%, #22c55e 100%) !important;
        color: #022c22 !important;
        border: none !important;
        padding: 16px 24px !important;
        border-radius: 16px !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        width: 100%;
        box-shadow: 0 10px 20px rgba(46, 204, 113, 0.25) !important;
        transition: transform 0.2s !important;
    }
    div.stButton > button:hover { transform: scale(1.02); }

    /* Tale of the Tape */
    .fighter-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 15px; }
    .fighter-name-l { font-size: 1.2rem; font-weight: 900; color: var(--secondary); text-align: left; line-height: 1.1; }
    .fighter-name-r { font-size: 1.2rem; font-weight: 900; color: var(--accent); text-align: right; line-height: 1.1; }
    .vs-badge { background: #fff; color: #000; font-weight: 900; padding: 4px 10px; border-radius: 8px; font-size: 0.8rem; transform: rotate(-5deg); box-shadow: 0 5px 10px rgba(0,0,0,0.2); }

    /* Stats Bars */
    .stat-container { margin-bottom: 12px; }
    .stat-label { text-align: center; font-size: 0.7rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
    .bar-bg { background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; overflow: hidden; display: flex; }
    .bar-l { height: 100%; background: var(--secondary); }
    .bar-r { height: 100%; background: var(--accent); }
    .stat-nums { display: flex; justify-content: space-between; font-size: 0.9rem; font-weight: 800; color: white; padding: 0 5px; }

    /* Prediction */
    .pred-card { text-align: center; border: 2px solid var(--primary); background: radial-gradient(circle, rgba(46,204,113,0.1) 0%, rgba(30,41,59,0.8) 100%); }
    .pred-winner { font-size: 2.2rem; font-weight: 900; color: white; text-transform: uppercase; margin: 10px 0; text-shadow: 0 0 20px rgba(46,204,113,0.4); }
    .pred-pct { display: inline-block; background: var(--primary); color: #064e3b; padding: 6px 16px; border-radius: 50px; font-weight: 800; font-size: 0.9rem; }

</style>
""", unsafe_allow_html=True)

# --- 4. BACKEND (Logique) ---
@st.cache_data
def get_fighter_url(name):
    if not name: return None
    try:
        query = name.replace(' ', '+')
        url = f"http://ufcstats.com/statistics/fighters/search?query={query}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(resp.content, 'html.parser')
        for row in soup.find_all('tr', class_='b-statistics__table-row')[1:6]:
            link = row.find('a', href=True)
            if link and name.lower() in link.text.strip().lower(): return link['href']
        # Fallback
        first = soup.find('tr', class_='b-statistics__table-row')[1].find('a', href=True)
        return first['href'] if first else None
    except: return None

def get_stats(url):
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(resp.content, 'html.parser')
        s = {'Nom': '?', 'Taille': 'N/A', 'Allonge': 'N/A', 'Coups/min': 0.0, 'Takedown': 0.0, 'DefLutte': 0, 'Précision': 0}
        
        title = soup.find('span', class_='b-content__title-highlight')
        if title: s['Nom'] = title.text.strip()

        info = soup.find_all('li', class_='b-list__box-list-item')
        for i in info:
            t = i.text.strip()
            if "Height:" in t: s['Taille'] = t.split(':')[1].strip()
            if "Reach:" in t: s['Allonge'] = t.split(':')[1].strip()
            
        for row in info:
            t = row.text.replace('\n', '').strip()
            if "SLpM:" in t: s['Coups/min'] = float(t.split(':')[1])
            if "TD Avg.:" in t: s['Takedown'] = float(t.split(':')[1])
            if "TD Def.:" in t: s['DefLutte'] = int(t.split(':')[1].replace('%', ''))
            if "Str. Acc.:" in t: s['Précision'] = int(t.split(':')[1].replace('%', ''))
        return s
    except: return None

# --- 5. FRONTEND (L'App) ---

st.markdown("<h1 style='text-align:center; margin-bottom: 5px;'>GETCAGEMETRICS <span style='color:#2ecc71'>PRO</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-bottom:30px;'>L'outil d'analyse prédictive MMA ultime.</p>", unsafe_allow_html=True)

# SÉLECTEUR DE CATÉGORIE
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("<div style='color:#94a3b8; font-size:0.8rem; font-weight:700; margin-bottom:5px; text-transform:uppercase;'>ÉTAPE 1 : Division</div>", unsafe_allow_html=True)
category = st.selectbox("Choisir la catégorie", list(ROSTER.keys()), label_visibility="collapsed")
fighters_list = ROSTER[category]
st.markdown('</div>', unsafe_allow_html=True)

# SÉLECTEUR DE COMBATTANTS
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("<div style='color:#94a3b8; font-size:0.8rem; font-weight:700; margin-bottom:15px; text-transform:uppercase;'>ÉTAPE 2 : Le Matchup</div>", unsafe_allow_html=True)

c1, c_mid, c2 = st.columns([10, 2, 10])
with c1:
    st.markdown("<span style='color:#38bdf8; font-weight:700;'>🔵 COIN BLEU</span>", unsafe_allow_html=True)
    f_a = st.selectbox("Combattant A", fighters_list, index=0, label_visibility="collapsed", key="fa")
with c_mid:
    st.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:white;'>VS</div>", unsafe_allow_html=True)
with c2:
    st.markdown("<span style='color:#f43f5e; font-weight:700;'>🔴 COIN ROUGE</span>", unsafe_allow_html=True)
    f_b = st.selectbox("Combattant B", fighters_list, index=1 if len(fighters_list)>1 else 0, label_visibility="collapsed", key="fb")
st.markdown('</div>', unsafe_allow_html=True)

# BOUTON ANALYSE
if st.button("LANCER LA SIMULATION DU COMBAT", use_container_width=True):
    if f_a != f_b:
        with st.spinner("Analyse des styles en cours..."):
            url_a = get_fighter_url(f_a)
            url_b = get_fighter_url(f_b)
            
            if url_a and url_b:
                s1 = get_stats(url_a)
                s2 = get_stats(url_b)
                
                if s1 and s2:
                    # ALGO SIMPLE
                    score = 50 + (s1['Coups/min'] - s2['Coups/min']) * 6
                    if s1['Takedown'] > 2.5 and s2['DefLutte'] < 65: score += 12
                    if s2['Takedown'] > 2.5 and s1['DefLutte'] < 65: score -= 12
                    score = max(5, min(95, score))
                    
                    pct_win = int(score if score >= 50 else 100 - score)
                    winner = s1['Nom'] if score >= 50 else s2['Nom']
                    
                    # --- RESULTAT ---
                    st.markdown(f"""
                    <div class="glass-card pred-card">
                        <div style="color:#94a3b8; font-weight:700; letter-spacing:1px; font-size:0.8rem;">VAINQUEUR PRÉDIT</div>
                        <div class="pred-winner">{winner}</div>
                        <div class="pred-pct">{pct_win}% DE CONFIANCE</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- TALE OF THE TAPE VISUEL ---
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    
                    # HEADER
                    st.markdown(f"""
                    <div class="fighter-header">
                        <div class="fighter-name-l">{s1['Nom']}</div>
                        <div class="vs-badge">VS</div>
                        <div class="fighter-name-r">{s2['Nom']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # FONCTION BARRE DE STAT
                    def render_stat_bar(label, v1, v2, max_val):
                        # Normalisation pour la barre (éviter division par 0)
                        total = max(v1 + v2, 0.1)
                        p1 = (v1 / total) * 100
                        p2 = (v2 / total) * 100
                        
                        st.markdown(f"""
                        <div class="stat-container">
                            <div class="stat-nums">
                                <span style="color:#38bdf8">{v1}</span>
                                <span style="color:#f43f5e">{v2}</span>
                            </div>
                            <div class="bar-bg">
                                <div class="bar-l" style="width: {p1}%;"></div>
                                <div class="bar-r" style="width: {p2}%;"></div>
                            </div>
                            <div class="stat-label">{label}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # RENDU DES STATS
                    render_stat_bar("Volume de Frappes / min", s1['Coups/min'], s2['Coups/min'], 15)
                    render_stat_bar("Précision (%)", s1['Précision'], s2['Précision'], 100)
                    render_stat_bar("Moyenne Takedowns / 15m", s1['Takedown'], s2['Takedown'], 10)
                    render_stat_bar("Défense de Lutte (%)", s1['DefLutte'], s2['DefLutte'], 100)
                    
                    # Info Physique (Texte simple)
                    c_h1, c_h2 = st.columns(2)
                    with c_h1: st.markdown(f"<div style='text-align:center; font-size:0.8rem; color:#94a3b8;'>📏 {s1['Taille']} / {s1['Allonge']}</div>", unsafe_allow_html=True)
                    with c_h2: st.markdown(f"<div style='text-align:center; font-size:0.8rem; color:#94a3b8;'>📏 {s2['Taille']} / {s2['Allonge']}</div>", unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                    # CTA BETTING
                    st.markdown(f"""
                    <a href="https://www.unibet.fr/sport/mma" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; background:#fc4c02; color:white; border:none; padding:18px; border-radius:16px; font-weight:800; text-transform:uppercase; cursor:pointer; box-shadow: 0 5px 15px rgba(252, 76, 2, 0.4);">
                            🔥 PARIER SUR {winner}
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

                else: st.error("Erreur de récupération des données.")
    else:
        st.warning("Veuillez sélectionner deux combattants différents.")
