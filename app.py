import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics", page_icon="⚡", layout="centered")

# --- 2. DATA : ROSTER COMPLET ---
ROSTER = {
    "🏆 P4P / Stars": [
        "Jon Jones", "Islam Makhachev", "Alex Pereira", "Ilia Topuria", "Sean O'Malley", 
        "Conor McGregor", "Max Holloway", "Charles Oliveira", "Dustin Poirier", "Justin Gaethje",
        "Khamzat Chimaev", "Israel Adesanya", "Benoit Saint Denis", "Ciryl Gane"
    ],
    "Poids Lourds (HW)": ["Jon Jones", "Tom Aspinall", "Ciryl Gane", "Sergei Pavlovich", "Curtis Blaydes", "Jailton Almeida", "Alexander Volkov", "Stipe Miocic", "Derrick Lewis"],
    "Poids Mi-Lourds (LHW)": ["Alex Pereira", "Jiri Prochazka", "Magomed Ankalaev", "Jan Blachowicz", "Jamahal Hill", "Khalil Rountree Jr.", "Johnny Walker"],
    "Poids Moyens (MW)": ["Dricus Du Plessis", "Sean Strickland", "Israel Adesanya", "Robert Whittaker", "Nassourdine Imavov", "Jared Cannonier", "Marvin Vettori", "Khamzat Chimaev", "Paulo Costa"],
    "Poids Mi-Moyens (WW)": ["Belal Muhammad", "Leon Edwards", "Kamaru Usman", "Shavkat Rakhmonov", "Jack Della Maddalena", "Gilbert Burns", "Ian Machado Garry", "Colby Covington"],
    "Poids Légers (LW)": ["Islam Makhachev", "Arman Tsarukyan", "Charles Oliveira", "Justin Gaethje", "Dustin Poirier", "Michael Chandler", "Mateusz Gamrot", "Benoit Saint Denis", "Dan Hooker", "Paddy Pimblett"],
    "Poids Plumes (FW)": ["Ilia Topuria", "Alexander Volkanovski", "Max Holloway", "Brian Ortega", "Yair Rodriguez", "Movsar Evloev", "Arnold Allen", "Diego Lopes"],
    "Poids Coqs (BW)": ["Merab Dvalishvili", "Sean O'Malley", "Cory Sandhagen", "Petr Yan", "Marlon Vera", "Henry Cejudo", "Umar Nurmagomedov"]
}

# --- 3. CSS "PURE STYLE" ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800;900&display=swap');

    .stApp {
        background-color: #020617; /* Noir Profond */
        background-image: radial-gradient(circle at 50% 0%, rgba(46, 204, 113, 0.1) 0%, transparent 60%);
        font-family: 'Montserrat', sans-serif;
    }
    
    h1, h2, h3, div, p { font-family: 'Montserrat', sans-serif !important; }

    /* Inputs plus discrets */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
    }

    /* Cards Ultra Clean */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 15px;
    }

    /* Bouton Action */
    div.stButton > button {
        background: #2ecc71 !important;
        color: #022c22 !important;
        border: none !important;
        padding: 16px !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        width: 100%;
        transition: 0.2s;
    }
    div.stButton > button:hover { opacity: 0.9; transform: scale(1.01); }

    /* Tale of the Tape Styles */
    .fighter-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .name-l { color: #38bdf8; font-weight: 900; font-size: 1.1rem; text-align: left; width: 45%; }
    .name-r { color: #f43f5e; font-weight: 900; font-size: 1.1rem; text-align: right; width: 45%; }
    .vs-tag { background: #fff; color: #000; font-weight: 900; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; }
    
    .stat-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .s-val { color: white; font-weight: 700; width: 20%; text-align: center; }
    .s-lbl { color: #94a3b8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; width: 60%; text-align: center; }

    /* Prediction Card */
    .pred-card { text-align: center; border: 2px solid #2ecc71; background: rgba(46, 204, 113, 0.05); }
    .winner { font-size: 2rem; font-weight: 900; color: white; text-transform: uppercase; margin: 5px 0; }
    .pct { background: #2ecc71; color: #020617; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.85rem; }

</style>
""", unsafe_allow_html=True)

# --- 4. MOTEUR ROBUSTE (CORRECTION BUGS) ---
@st.cache_data
def get_fighter_data_robust(name):
    """Cherche l'URL et scrape les données en une fois."""
    if not name: return None
    
    # 1. Recherche URL (Mode permissif)
    search_url = f"http://ufcstats.com/statistics/fighters/search?query={name.replace(' ', '+')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        resp = requests.get(search_url, headers=headers, timeout=6)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        target_url = None
        rows = soup.find_all('tr', class_='b-statistics__table-row')
        
        # Essai 1 : Match exact ou partiel
        for row in rows[1:6]:
            link = row.find('a', href=True)
            if link and name.lower() in link.text.strip().lower():
                target_url = link['href']
                break
        
        # Essai 2 : Si pas trouvé, on prend le tout premier résultat (Force brute)
        if not target_url and len(rows) > 1:
            first_link = rows[1].find('a', href=True)
            if first_link: target_url = first_link['href']

        if not target_url: return None

        # 2. Scraping Stats
        resp_stats = requests.get(target_url, headers=headers, timeout=6)
        soup_s = BeautifulSoup(resp_stats.content, 'html.parser')
        
        s = {'Nom': name, 'Taille': '-', 'Allonge': '-', 'Coups': 0.0, 'TD': 0.0, 'DefLutte': 0, 'Preci': 0}
        
        # Nom officiel
        title = soup_s.find('span', class_='b-content__title-highlight')
        if title: s['Nom'] = title.text.strip()
        
        # Parsing
        info = soup_s.find_all('li', class_='b-list__box-list-item')
        for i in info:
            t = i.text.strip()
            if "Height:" in t: s['Taille'] = t.split(':')[1].strip()
            if "Reach:" in t: s['Allonge'] = t.split(':')[1].strip()
            if "SLpM:" in t: s['Coups'] = float(t.split(':')[1])
            if "TD Avg.:" in t: s['TD'] = float(t.split(':')[1])
            if "TD Def.:" in t: s['DefLutte'] = int(t.split(':')[1].replace('%', ''))
            if "Str. Acc.:" in t: s['Preci'] = int(t.split(':')[1].replace('%', ''))
            
        return s

    except Exception as e:
        return None

# --- 5. INTERFACE ---

st.markdown("<h1 style='text-align:center; margin-bottom: 20px; color:white;'>GETCAGEMETRICS ⚡</h1>", unsafe_allow_html=True)

# SÉLECTION (Design Compact)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
cat = st.selectbox("Catégorie", list(ROSTER.keys()), label_visibility="collapsed")
fighters = ROSTER[cat]

c1, c2, c3 = st.columns([1, 0.2, 1])
with c1: f_a = st.selectbox("A", fighters, index=0, label_visibility="collapsed", key="a")
with c2: st.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:#444;'>VS</div>", unsafe_allow_html=True)
with c3: f_b = st.selectbox("B", fighters, index=1 if len(fighters)>1 else 0, label_visibility="collapsed", key="b")
st.markdown('</div>', unsafe_allow_html=True)

# BOUTON
if st.button("LANCER L'ANALYSE", use_container_width=True):
    if f_a == f_b:
        st.warning("Choisissez deux combattants différents.")
    else:
        with st.spinner("Analyse des données en cours..."):
            s1 = get_fighter_data_robust(f_a)
            s2 = get_fighter_data_robust(f_b)
            
            if s1 and s2:
                # --- CALCUL SCORE ---
                score = 50 + (s1['Coups'] - s2['Coups']) * 5
                # Bonus Lutte vs Passoire
                if s1['TD'] > 2.5 and s2['DefLutte'] < 60: score += 15
                if s2['TD'] > 2.5 and s1['DefLutte'] < 60: score -= 15
                
                score = max(5, min(95, score))
                winner = s1['Nom'] if score >= 50 else s2['Nom']
                pct = int(score if score >= 50 else 100 - score)

                # --- RÉSULTATS ---
                
                # 1. Carte de Prédiction
                st.markdown(f"""
                <div class="glass-card pred-card">
                    <div style="color:#94a3b8; font-size:0.75rem; font-weight:700; letter-spacing:1px;">VAINQUEUR PRÉDIT</div>
                    <div class="winner">{winner}</div>
                    <span class="pct">{pct}% DE CONFIANCE</span>
                </div>
                """, unsafe_allow_html=True)

                # 2. Tale of the Tape (Stats Visuelles)
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                
                # Header Noms
                st.markdown(f"""
                <div class="fighter-header">
                    <div class="name-l">{s1['Nom']}</div>
                    <div class="vs-tag">VS</div>
                    <div class="name-r">{s2['Nom']}</div>
                </div>
                """, unsafe_allow_html=True)

                # Lignes Stats
                def row(lbl, v1, v2):
                    st.markdown(f"""
                    <div class="stat-row">
                        <div class="s-val" style="color:#38bdf8;">{v1}</div>
                        <div class="s-lbl">{lbl}</div>
                        <div class="s-val" style="color:#f43f5e;">{v2}</div>
                    </div>
                    """, unsafe_allow_html=True)

                row("Taille", s1['Taille'], s2['Taille'])
                row("Allonge", s1['Allonge'], s2['Allonge'])
                row("Frappes / min", s1['Coups'], s2['Coups'])
                row("Précision", f"{s1['Preci']}%", f"{s2['Preci']}%")
                row("Takedowns / 15m", s1['TD'], s2['TD'])
                row("Défense Lutte", f"{s1['DefLutte']}%", f"{s2['DefLutte']}%")

                st.markdown('</div>', unsafe_allow_html=True)
                
                # 3. Lien Pari
                st.markdown(f"""
                <a href="https://www.unibet.fr/sport/mma" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background:#fc4c02; color:white; border:none; padding:15px; border-radius:12px; font-weight:800; cursor:pointer;">
                        PARIER SUR {winner}
                    </button>
                </a>
                """, unsafe_allow_html=True)

            else:
                st.error("Impossible de récupérer les données pour ces combattants (Site UFC lent ou inaccessible). Réessayez.")
