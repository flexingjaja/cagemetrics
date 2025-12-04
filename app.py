import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Pro", page_icon="⚡", layout="centered")

# --- 2. ROSTER COMPLET (TOP 15 ACTUALISÉ) ---
ROSTER = {
    "Poids Lourds (Heavyweight)": [
        "Jon Jones", "Tom Aspinall", "Ciryl Gane", "Alexander Volkov", "Sergei Pavlovich", 
        "Curtis Blaydes", "Jailton Almeida", "Serghei Spivac", "Stipe Miocic", "Marcin Tybura", 
        "Derrick Lewis", "Jairzinho Rozenstruik", "Alexandr Romanov", "Marcos Rogerio de Lima", "Tai Tuivasa"
    ],
    "Poids Mi-Lourds (Light Heavyweight)": [
        "Alex Pereira", "Magomed Ankalaev", "Jiri Prochazka", "Jan Blachowicz", "Jamahal Hill", 
        "Aleksandar Rakic", "Khalil Rountree Jr.", "Nikita Krylov", "Volkan Oezdemir", "Johnny Walker", 
        "Azamat Murzakanov", "Anthony Smith", "Dominick Reyes", "Alonzo Menifield", "Bogdan Guskov"
    ],
    "Poids Moyens (Middleweight)": [
        "Dricus Du Plessis", "Sean Strickland", "Israel Adesanya", "Robert Whittaker", "Nassourdine Imavov", 
        "Caio Borralho", "Marvin Vettori", "Jared Cannonier", "Brendan Allen", "Roman Dolidze", 
        "Paulo Costa", "Jack Hermansson", "Anthony Hernandez", "Michel Pereira", "Chris Curtis"
    ],
    "Poids Mi-Moyens (Welterweight)": [
        "Belal Muhammad", "Leon Edwards", "Kamaru Usman", "Shavkat Rakhmonov", "Jack Della Maddalena", 
        "Ian Machado Garry", "Gilbert Burns", "Sean Brady", "Stephen Thompson", "Geoff Neal", 
        "Joaquin Buckley", "Michael Morales", "Vicente Luque", "Kevin Holland", "Neil Magny"
    ],
    "Poids Légers (Lightweight)": [
        "Islam Makhachev", "Arman Tsarukyan", "Charles Oliveira", "Justin Gaethje", "Dustin Poirier", 
        "Dan Hooker", "Michael Chandler", "Mateusz Gamrot", "Beneil Dariush", "Renato Moicano", 
        "Rafael Fiziev", "Benoit Saint Denis", "Paddy Pimblett", "Jalin Turner", "Bobby Green"
    ],
    "Poids Plumes (Featherweight)": [
        "Ilia Topuria", "Alexander Volkanovski", "Max Holloway", "Diego Lopes", "Movsar Evloev", 
        "Brian Ortega", "Yair Rodriguez", "Arnold Allen", "Josh Emmett", "Aljamain Sterling", 
        "Calvin Kattar", "Giga Chikadze", "Lerone Murphy", "Bryce Mitchell", "Dan Ige"
    ],
    "Poids Coqs (Bantamweight)": [
        "Merab Dvalishvili", "Sean O'Malley", "Petr Yan", "Umar Nurmagomedov", "Cory Sandhagen", 
        "Deiveson Figueiredo", "Marlon Vera", "Henry Cejudo", "Song Yadong", "Rob Font", 
        "Mario Bautista", "Jose Aldo", "Jonathan Martinez", "Kyler Phillips", "Dominick Cruz"
    ],
    "Poids Mouches (Flyweight)": [
        "Alexandre Pantoja", "Brandon Royval", "Brandon Moreno", "Amir Albazi", "Kai Kara-France", 
        "Tatsuro Taira", "Manel Kape", "Matheus Nicolau", "Steve Erceg", "Tim Elliott", 
        "Tagir Ulanbekov", "Bruno Silva", "Asu Almabayev"
    ],
    "Femmes - Poids Pailles (Strawweight)": [
        "Zhang Weili", "Tatiana Suarez", "Yan Xiaonan", "Virna Jandiroba", "Jessica Andrade", 
        "Amanda Lemos", "Mackenzie Dern", "Marina Rodriguez", "Loopy Godinez"
    ],
    "Femmes - Poids Mouches (Flyweight)": [
        "Valentina Shevchenko", "Alexa Grasso", "Manon Fiorot", "Erin Blanchfield", "Maycee Barber", 
        "Rose Namajunas", "Jessica Andrade", "Natalia Silva"
    ],
    "Femmes - Poids Coqs (Bantamweight)": [
        "Julianna Pena", "Raquel Pennington", "Kayla Harrison", "Ketlen Vieira", "Irene Aldana", 
        "Macy Chiasson", "Norma Dumont", "Holly Holm"
    ]
}

# --- 3. BASE DE DONNÉES DE SECOURS (STARS) ---
# Permet une réponse instantanée pour les Top Fighters sans scraper
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
    "Merab Dvalishvili": {"Taille": "5' 6\"", "Allonge": "68\"", "Coups": 4.50, "TD": 6.50, "DefLutte": 80, "Preci": 45},
    "Dricus Du Plessis": {"Taille": "6' 1\"", "Allonge": "76\"", "Coups": 6.49, "TD": 2.72, "DefLutte": 55, "Preci": 50},
    "Sean Strickland": {"Taille": "6' 1\"", "Allonge": "76\"", "Coups": 5.82, "TD": 1.00, "DefLutte": 85, "Preci": 41},
    "Belal Muhammad": {"Taille": "5' 11\"", "Allonge": "72\"", "Coups": 4.50, "TD": 2.20, "DefLutte": 93, "Preci": 48},
    "Shavkat Rakhmonov": {"Taille": "6' 1\"", "Allonge": "77\"", "Coups": 4.45, "TD": 1.49, "DefLutte": 100, "Preci": 59}
}

# --- 4. STYLE CSS (DESIGN PREMIUM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');

    /* Fond Global */
    .stApp {
        background-color: #020617;
        background-image: 
            radial-gradient(at 0% 0%, rgba(46, 204, 113, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(56, 189, 248, 0.08) 0px, transparent 50%);
        font-family: 'Montserrat', sans-serif;
    }

    h1, h2, div, p { font-family: 'Montserrat', sans-serif !important; }

    /* Titre Custom sans barre */
    .main-title {
        text-align: center; font-weight: 900; font-size: 2.5rem; color: white;
        margin-top: -20px; margin-bottom: 30px; letter-spacing: -1px;
    }
    .highlight { color: #2ecc71; }

    /* Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(12px);
        border-radius: 24px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }

    /* Inputs */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        border-radius: 12px !important;
    }

    /* Bouton */
    div.stButton > button {
        background: linear-gradient(135deg, #2ecc71 0%, #10b981 100%) !important;
        color: #020617 !important;
        border: none !important;
        padding: 18px !important;
        border-radius: 16px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        box-shadow: 0 10px 25px -5px rgba(46, 204, 113, 0.3) !important;
        transition: 0.2s !important;
    }
    div.stButton > button:hover { transform: translateY(-2px); filter: brightness(1.1); }

    /* Stats Finish Bar */
    .finish-bar-container { width: 100%; height: 16px; background: #1e293b; border-radius: 8px; overflow: hidden; display: flex; margin-top: 12px; }
    .bar-seg { height: 100%; }
    .legend-row { display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.75rem; font-weight: 700; }
    
</style>
""", unsafe_allow_html=True)

# --- 5. LOGIQUE BACKEND ---
@st.cache_data
def get_data(name):
    # 1. Vérification Base de Secours (Instantané)
    if name in BACKUP:
        d = BACKUP[name]
        d['Nom'] = name
        return d
    
    # 2. Scraping si pas en base
    try:
        url = f"http://ufcstats.com/statistics/fighters/search?query={name.replace(' ', '+')}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        target = None
        rows = soup.find_all('tr', class_='b-statistics__table-row')
        
        # Recherche intelligente
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
                t = i.text.strip()
                if "Height:" in t: stats['Taille'] = t.split(':')[1].strip()
                if "Reach:" in t: stats['Allonge'] = t.split(':')[1].strip()
                if "SLpM:" in t: stats['Coups'] = float(t.split(':')[1])
                if "TD Avg.:" in t: stats['TD'] = float(t.split(':')[1])
                if "TD Def.:" in t: stats['DefLutte'] = int(t.split(':')[1].replace('%', ''))
                if "Str. Acc.:" in t: stats['Preci'] = int(t.split(':')[1].replace('%', ''))
            return stats
    except: return None
    return None

def calc_probs(f1, f2):
    # Score Vainqueur
    score = 50 + (f1['Coups'] - f2['Coups']) * 5
    if f1['TD'] > 2 and f2['DefLutte'] < 60: score += 12
    if f2['TD'] > 2 and f1['DefLutte'] < 60: score -= 12
    score = max(10, min(90, score))
    
    # Finish Logic
    violence = (f1['Coups'] + f2['Coups']) + (f1['TD'] + f2['TD'])*2
    finish_chance = min(90, 20 + violence * 4)
    
    # Répartition KO / Sub
    strike_ratio = (f1['Coups'] + f2['Coups']) / max(1, violence)
    ko = int(finish_chance * strike_ratio)
    sub = int(finish_chance * (1 - strike_ratio))
    dec = 100 - ko - sub
    
    # Correction si grapplers
    if (f1['TD'] > 2 or f2['TD'] > 2): sub += 10; ko -= 10
    
    return int(score), ko, sub, dec

# --- 6. INTERFACE ---
st.markdown("<div class='main-title'>GETCAGEMETRICS <span class='highlight'>PRO</span></div>", unsafe_allow_html=True)

# SÉLECTION
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
cat = st.selectbox("Catégorie", list(ROSTER.keys()), label_visibility="collapsed")
fighters = ROSTER[cat]

c1, c2, c3 = st.columns([1, 0.2, 1])
with c1: f_a = st.selectbox("Combattant A", fighters, index=0, label_visibility="collapsed", key="a")
with c2: st.markdown("<div style='text-align:center; padding-top:12px; font-weight:900; color:#fff;'>VS</div>", unsafe_allow_html=True)
with c3: f_b = st.selectbox("Combattant B", fighters, index=1 if len(fighters)>1 else 0, label_visibility="collapsed", key="b")
st.markdown('</div>', unsafe_allow_html=True)

if st.button("LANCER L'ANALYSE DU COMBAT", use_container_width=True):
    if f_a == f_b:
        st.warning("Veuillez sélectionner deux combattants différents.")
    else:
        with st.spinner("Analyse des statistiques..."):
            s1 = get_data(f_a)
            s2 = get_data(f_b)
            
            if s1 and s2:
                # Calculs
                score_a, ko, sub, dec = calc_probs(s1, s2)
                winner = s1['Nom'] if score_a >= 50 else s2['Nom']
                conf = score_a if score_a >= 50 else 100 - score_a
                
                # --- AFFICHAGE RÉSULTAT ---
                st.markdown(f"""
                <div class="glass-card" style="text-align:center; border:2px solid #2ecc71; background: rgba(46, 204, 113, 0.05);">
                    <div style="color:#94a3b8; font-size:0.75rem; font-weight:700; letter-spacing:1px; margin-bottom:5px;">RÉSULTAT PROBABLE</div>
                    <div style="font-size:2.5rem; font-weight:900; color:white; line-height:1;">{winner}</div>
                    <div style="background:#2ecc71; color:#020617; padding:4px 12px; border-radius:20px; font-weight:800; font-size:0.85rem; display:inline-block; margin-top:10px;">{conf}% DE CONFIANCE</div>
                </div>
                """, unsafe_allow_html=True)
                
                # --- BARRE DE FINISH ---
                st.markdown(f"""
                <div class="glass-card">
                    <div style="text-align:center; font-weight:800; color:white; margin-bottom:5px;">SCÉNARIO DU COMBAT</div>
                    <div class="finish-bar-container">
                        <div class="bar-seg" style="width:{ko}%; background:#ef4444;"></div>
                        <div class="bar-seg" style="width:{sub}%; background:#eab308;"></div>
                        <div class="bar-seg" style="width:{dec}%; background:#3b82f6;"></div>
                    </div>
                    <div class="legend-row">
                        <span style="color:#ef4444">KO/TKO {ko}%</span>
                        <span style="color:#eab308">SOUMISSION {sub}%</span>
                        <span style="color:#3b82f6">DÉCISION {dec}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # --- STATS ---
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                def stat_line(l, v1, v2):
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:4px;">
                        <span style="color:#38bdf8; font-weight:700;">{v1}</span>
                        <span style="color:#94a3b8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">{l}</span>
                        <span style="color:#f43f5e; font-weight:700;">{v2}</span>
                    </div>""", unsafe_allow_html=True)
                
                stat_line("Taille", s1['Taille'], s2['Taille'])
                stat_line("Allonge", s1['Allonge'], s2['Allonge'])
                stat_line("Frappes / min", s1['Coups'], s2['Coups'])
                stat_line("Précision", f"{s1['Preci']}%", f"{s2['Preci']}%")
                stat_line("Takedowns", s1['TD'], s2['TD'])
                stat_line("Défense Lutte", f"{s1['DefLutte']}%", f"{s2['DefLutte']}%")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # CTA
                st.markdown(f"""<a href="https://www.unibet.fr/sport/mma" target="_blank"><button>PARIER SUR {winner}</button></a>""", unsafe_allow_html=True)
            
            else:
                st.error("Données introuvables. Veuillez réessayer.")
