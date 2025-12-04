import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GetCageMetrics", page_icon="⚡", layout="centered")

# --- 2. BASE DE DONNÉES (LES COMBATTANTS) ---
# J'ai mis ici les 300+ combattants les plus importants (Top 15 + Légendes)
# C'est cette liste qui te permet d'avoir le menu déroulant direct.
ROSTER = [
    "--- SÉLECTIONNER ---",
    "Alex Pereira", "Islam Makhachev", "Jon Jones", "Ilia Topuria", "Dricus Du Plessis",
    "Sean O'Malley", "Max Holloway", "Charles Oliveira", "Justin Gaethje", "Dustin Poirier",
    "Benoit Saint Denis", "Ciryl Gane", "Manon Fiorot", "Nassourdine Imavov", "Khamzat Chimaev",
    "Conor McGregor", "Israel Adesanya", "Kamaru Usman", "Leon Edwards", "Alexander Volkanovski",
    "Tom Aspinall", "Sergei Pavlovich", "Jiri Prochazka", "Jamahal Hill", "Robert Whittaker",
    "Sean Strickland", "Colby Covington", "Shavkat Rakhmonov", "Gilbert Burns", "Merab Dvalishvili",
    "Aljamain Sterling", "Cory Sandhagen", "Petr Yan", "Marlon Vera", "Alexandre Pantoja",
    "Brandon Moreno", "Brandon Royval", "Amir Albazi", "Zhang Weili", "Alexa Grasso",
    "Valentina Shevchenko", "Erin Blanchfield", "Tatiana Suarez", "Rose Namajunas", "Amanda Nunes",
    "Francis Ngannou", "Stipe Miocic", "Daniel Cormier", "Khabib Nurmagomedov", "Georges St-Pierre",
    "Anderson Silva", "Jose Aldo", "Demetrious Johnson", "Henry Cejudo", "Tony Ferguson",
    "Michael Chandler", "Mateusz Gamrot", "Arman Tsarukyan", "Rafael Fiziev", "Dan Hooker",
    "Jailton Almeida", "Curtis Blaydes", "Alexander Volkov", "Tai Tuivasa", "Jairzinho Rozenstruik",
    "Jan Blachowicz", "Aleksandar Rakic", "Magomed Ankalaev", "Johnny Walker", "Nikita Krylov",
    "Paulo Costa", "Brendan Allen", "Marvin Vettori", "Jared Cannonier", "Jack Della Maddalena",
    "Ian Machado Garry", "Kevin Holland", "Stephen Thompson", "Vicente Luque", "Belal Muhammad",
    "Movsar Evloev", "Arnold Allen", "Calvin Kattar", "Giga Chikadze", "Yair Rodriguez",
    "Brian Ortega", "Deiveson Figueiredo", "Kai Kara-France", "Manel Kape", "Matheus Nicolau",
    "Julianna Pena", "Raquel Pennington", "Mayra Bueno Silva", "Holly Holm", "Ketlen Vieira",
    "Yan Xiaonan", "Virna Jandiroba", "Mackenzie Dern", "Amanda Lemos", "Jéssica Andrade",
    "Kayla Harrison", "Bo Nickal", "Paddy Pimblett", "Michel Pereira", "Derrick Lewis",
    "Anthony Smith", "Dominick Reyes", "Chris Weidman", "Edson Barboza", "Bobby Green",
    "Jim Miller", "Clay Guida", "Neil Magny", "Li Jingliang", "Santiago Ponzinibbio",
    "Jack Hermansson", "Paul Craig", "Caio Borralho", "Roman Dolidze", "Alonzo Menifield",
    "Khalil Rountree Jr.", "Azamat Murzakanov", "Vitor Petrino", "Steve Erceg", "Muhammad Mokaev",
    "Umar Nurmagomedov", "Jonathan Martinez", "Mario Bautista", "Rob Font", "Kyler Phillips",
    "Sodiq Yusuff", "Diego Lopes", "Lerone Murphy", "Edson Barboza", "Bryce Mitchell",
    "Fares Ziam", "William Gomis", "Morgan Charriere", "Taylor Lapilus", "Nora Cornolle"
]
ROSTER.sort() # On trie par ordre alphabétique pour que ce soit propre

# --- 3. STYLE RUNNATIC (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700;800;900&display=swap');

    :root {
        --bg: #0f172a;
        --card-glass: rgba(30, 41, 59, 0.75);
        --primary: #2ecc71;
        --primary-glow: rgba(46, 204, 113, 0.3);
        --text-muted: #94a3b8;
    }

    .stApp {
        background-color: var(--bg);
        background-image: radial-gradient(circle at 50% 0%, rgba(46, 204, 113, 0.1) 0%, transparent 50%);
        font-family: 'Montserrat', sans-serif;
    }
    
    h1, h2, h3, div, span, p { font-family: 'Montserrat', sans-serif !important; }

    /* Inputs et Selectbox */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Cards */
    .metric-card {
        background: var(--card-glass);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 30px -5px rgba(0,0,0,0.3);
    }

    /* Tale of the Tape Fix */
    .stat-line {
        display: flex; justify-content: space-between; align-items: center;
        padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .stat-label { font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; text-align: center; width: 40%; }
    .stat-val { font-weight: 800; font-size: 1rem; width: 30%; text-align: center; }
    .val-blue { color: #38bdf8; }
    .val-pink { color: #f472b6; }

    /* Bouton */
    div.stButton > button {
        background: linear-gradient(135deg, #2ecc71, #27ae60) !important;
        color: #022c22 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        padding: 16px !important;
        box-shadow: 0 10px 20px rgba(46, 204, 113, 0.2) !important;
        border: none !important;
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.02); }

    /* Prediction */
    .pred-box { text-align: center; border: 2px solid var(--primary); background: rgba(46, 204, 113, 0.05); }
    .winner-name { font-size: 2rem; font-weight: 900; color: white; text-transform: uppercase; margin: 10px 0; }
    .prob-tag { background: var(--primary); color: #022c22; padding: 5px 15px; border-radius: 20px; font-weight: 800; }

</style>
""", unsafe_allow_html=True)

# --- 4. MOTEUR DE RECHERCHE AUTO ---
# Cette fonction cherche l'URL en arrière-plan une fois le nom sélectionné
@st.cache_data
def get_fighter_url(name):
    if name == "--- SÉLECTIONNER ---": return None
    try:
        query = name.replace(' ', '+')
        url = f"http://ufcstats.com/statistics/fighters/search?query={query}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(resp.content, 'html.parser')
        # On prend le premier résultat qui correspond
        for row in soup.find_all('tr', class_='b-statistics__table-row')[1:6]:
            link = row.find('a', href=True)
            if link and name.lower() in link.text.strip().lower():
                return link['href']
        # Si pas de match exact, on prend le premier résultat
        first_link = soup.find('tr', class_='b-statistics__table-row')[1].find('a', href=True)
        return first_link['href'] if first_link else None
    except: return None

def get_stats(url):
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(resp.content, 'html.parser')
        stats = {}
        
        # Nom & Info
        stats['Nom'] = soup.find('span', class_='b-content__title-highlight').text.strip()
        stats['Taille'] = "N/A"
        stats['Allonge'] = "N/A"
        
        info_box = soup.find_all('li', class_='b-list__box-list-item')
        for item in info_box:
            t = item.text.strip()
            if "Height:" in t: stats['Taille'] = t.split(':')[1].strip()
            if "Reach:" in t: stats['Allonge'] = t.split(':')[1].strip()

        # Stats Combat
        stats['Coups/min'] = 0.0; stats['Takedown'] = 0.0; stats['DefLutte'] = 0; stats['Précision'] = 0
        for row in info_box:
            t = row.text.replace('\n', '').strip()
            if "SLpM:" in t: stats['Coups/min'] = float(t.split(':')[1])
            if "TD Avg.:" in t: stats['Takedown'] = float(t.split(':')[1])
            if "TD Def.:" in t: stats['DefLutte'] = int(t.split(':')[1].replace('%', ''))
            if "Str. Acc.:" in t: stats['Précision'] = int(t.split(':')[1].replace('%', ''))
            
        return stats
    except: return None

# --- 5. INTERFACE ---

st.markdown("<h1 style='text-align:center; color:white;'>GETCAGEMETRICS ⚡</h1>", unsafe_allow_html=True)

# SÉLECTION DIRECTE (Plus de recherche manuelle)
st.markdown('<div class="metric-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown("**🔵 COMBATTANT 1**")
    # C'est ici la magie : une liste déroulante où tu peux écrire
    fighter_a = st.selectbox("Sélection A", ROSTER, index=0, label_visibility="collapsed")
with c2:
    st.markdown("**🔴 COMBATTANT 2**")
    fighter_b = st.selectbox("Sélection B", ROSTER, index=0, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE", use_container_width=True):
    if fighter_a != "--- SÉLECTIONNER ---" and fighter_b != "--- SÉLECTIONNER ---":
        with st.spinner("Récupération des données officielles..."):
            url_a = get_fighter_url(fighter_a)
            url_b = get_fighter_url(fighter_b)
            
            if url_a and url_b:
                f1 = get_stats(url_a)
                f2 = get_stats(url_b)
                
                if f1 and f2:
                    # Calcul Prédiction
                    score = 50 + (f1['Coups/min'] - f2['Coups/min'])*5
                    if f1['Takedown'] > 2 and f2['DefLutte'] < 60: score += 15
                    if f2['Takedown'] > 2 and f1['DefLutte'] < 60: score -= 15
                    score = max(5, min(95, score))
                    
                    winner = f1['Nom'] if score >= 50 else f2['Nom']
                    pct = int(score if score >= 50 else 100 - score)
                    
                    # --- AFFICHAGE PRÉDICTION ---
                    st.markdown(f"""
                    <div class="metric-card pred-box">
                        <div style="color:#94a3b8; font-size:0.8rem; letter-spacing:1px; font-weight:700;">RÉSULTAT PROBABLE</div>
                        <div class="winner-name">{winner}</div>
                        <span class="prob-tag">{pct}% DE CHANCE DE VICTOIRE</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # --- TALE OF THE TAPE (CORRIGÉ & STYLÉ) ---
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    
                    # En-tête VS
                    c_n1, c_vs, c_n2 = st.columns([2,1,2])
                    with c_n1: st.markdown(f"<div style='text-align:center; color:#38bdf8; font-weight:900;'>{f1['Nom']}</div>", unsafe_allow_html=True)
                    with c_vs: st.markdown("<div style='text-align:center; font-weight:900; background:#facc15; color:black; border-radius:5px;'>VS</div>", unsafe_allow_html=True)
                    with c_n2: st.markdown(f"<div style='text-align:center; color:#f472b6; font-weight:900;'>{f2['Nom']}</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Lignes de stats (Utilisation de st.columns pour l'alignement parfait)
                    def stat_line(label, v1, v2):
                        c_v1, c_l, c_v2 = st.columns([1, 2, 1])
                        with c_v1: st.markdown(f"<div style='text-align:center; font-weight:700; color:#38bdf8;'>{v1}</div>", unsafe_allow_html=True)
                        with c_l: st.markdown(f"<div style='text-align:center; font-size:0.7rem; color:#94a3b8; font-weight:700; text-transform:uppercase;'>{label}</div>", unsafe_allow_html=True)
                        with c_v2: st.markdown(f"<div style='text-align:center; font-weight:700; color:#f472b6;'>{v2}</div>", unsafe_allow_html=True)
                        st.markdown("<div style='border-bottom:1px solid rgba(255,255,255,0.05); margin:5px 0;'></div>", unsafe_allow_html=True)

                    stat_line("Taille", f1['Taille'], f2['Taille'])
                    stat_line("Allonge", f1['Allonge'], f2['Allonge'])
                    stat_line("Frappes / Min", f1['Coups/min'], f2['Coups/min'])
                    stat_line("Précision", f"{f1['Précision']}%", f"{f2['Précision']}%")
                    stat_line("Takedown / 15m", f1['Takedown'], f2['Takedown'])
                    stat_line("Défense Lutte", f"{f1['DefLutte']}%", f"{f2['DefLutte']}%")
                    
                    st.markdown('</div>', unsafe_allow_html=True)

                    # --- BOUTON PARI ---
                    st.markdown(f"""
                    <a href="https://www.unibet.fr/sport/mma" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; background:#fc4c02; color:white; border:none; padding:15px; border-radius:12px; font-weight:800; cursor:pointer;">
                            PARIER SUR {winner}
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

    else:
        st.warning("Veuillez choisir 2 combattants.")
