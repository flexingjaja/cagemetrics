import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GetCageMetrics", page_icon="⚡", layout="centered")

# --- 2. INJECTION CSS (STYLE RUNNATIC EXACT) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700;800;900&display=swap');

    /* --- VARIABLES RUNNATIC --- */
    :root {
        --bg: #0f172a;
        --card-glass: rgba(30, 41, 59, 0.75);
        --card-border: rgba(255, 255, 255, 0.08);
        --primary: #2ecc71;   /* Vert Néon */
        --primary-glow: rgba(46, 204, 113, 0.3);
        --accent-yellow: #facc15;
        --text-main: #f1f5f9;
        --text-muted: #94a3b8;
    }

    /* --- RESET GÉNÉRAL --- */
    .stApp {
        background-color: var(--bg);
        background-image: 
            radial-gradient(circle at 10% 10%, rgba(46, 204, 113, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 90% 90%, rgba(139, 92, 246, 0.08) 0%, transparent 40%);
        font-family: 'Montserrat', sans-serif;
    }
    
    h1, h2, h3, p, div, span { font-family: 'Montserrat', sans-serif !important; }

    /* --- INPUTS & SELECTBOX --- */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }
    .stTextInput label { color: var(--text-muted) !important; font-weight: 600; }

    /* --- BOUTON PRINCIPAL --- */
    div.stButton > button {
        background: linear-gradient(135deg, #2ecc71, #27ae60) !important;
        color: #022c22 !important;
        border: none !important;
        padding: 18px !important;
        border-radius: 14px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        box-shadow: 0 10px 25px var(--primary-glow) !important;
        width: 100%;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px var(--primary-glow) !important;
    }

    /* --- CARDS (Style Runnatic Session-Card) --- */
    .metric-card {
        background: var(--card-glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid var(--card-border);
        box-shadow: 0 15px 35px -5px rgba(0,0,0,0.4);
    }

    /* --- TALE OF THE TAPE --- */
    .vs-header {
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
    }
    .fighter-name { font-size: 24px; font-weight: 900; color: white; text-transform: uppercase; width: 40%; }
    .vs-badge { 
        background: var(--accent-yellow); color: black; font-weight: 900; 
        padding: 5px 10px; border-radius: 8px; transform: rotate(-5deg); box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    .stat-row {
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(255,255,255,0.03);
        padding: 12px; border-radius: 12px; margin-bottom: 8px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stat-val { font-weight: 700; color: var(--primary); width: 30%; text-align: center; font-size: 1.1rem; }
    .stat-label { color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; font-weight: 600; width: 40%; text-align: center; }
    
    /* --- BARRES DE PROGRESSION (Style Runnatic Steps) --- */
    .progress-container {
        height: 8px; width: 100%; background: #334155; border-radius: 4px; overflow: hidden; margin-top: 5px;
    }
    .progress-fill { height: 100%; border-radius: 4px; }
    .fill-green { background: var(--primary); }
    .fill-yellow { background: var(--accent-yellow); }

    /* --- PREDICTION BOX --- */
    .pred-box {
        background: radial-gradient(circle at top right, rgba(46, 204, 113, 0.15), var(--card-glass));
        border: 2px solid var(--primary);
        text-align: center;
    }
    .win-prob { font-size: 3rem; font-weight: 900; color: var(--primary); line-height: 1; margin-bottom: 5px; }
    .method-tag { background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; display: inline-block; margin-top: 10px; }

    /* --- BETTING BUTTON --- */
    .bet-btn {
        display: block; width: 100%; text-align: center;
        background: #fc4c02; /* Couleur Strava/Unibet */
        color: white; font-weight: 800; padding: 15px;
        border-radius: 12px; text-decoration: none;
        margin-top: 20px; text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(252, 76, 2, 0.4);
        transition: 0.3s;
    }
    .bet-btn:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(252, 76, 2, 0.6); color: white;}

</style>
""", unsafe_allow_html=True)

# --- 3. MOTEUR DATA (Keep simple and robust) ---
@st.cache_data
def chercher_combattants(nom_partiel):
    if not nom_partiel or len(nom_partiel) < 2: return []
    try:
        url = f"http://ufcstats.com/statistics/fighters/search?query={nom_partiel.replace(' ', '+')}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(resp.content, 'html.parser')
        res = []
        for row in soup.find_all('tr', class_='b-statistics__table-row')[1:6]:
            link = row.find('a', href=True)
            if link: res.append({'nom': link.text.strip(), 'url': link['href']})
        return res
    except: return []

def get_stats(url):
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(resp.content, 'html.parser')
        stats = {}
        
        # Nom
        stats['Nom'] = soup.find('span', class_='b-content__title-highlight').text.strip()
        
        # Données physiques (souvent dans la page)
        stats['Taille'] = "180 cm" # Valeur par défaut si fail
        stats['Allonge'] = "180 cm"
        info_box = soup.find_all('li', class_='b-list__box-list-item')
        for item in info_box:
            t = item.text.strip()
            if "Height:" in t: stats['Taille'] = t.split(':')[1].strip()
            if "Reach:" in t: stats['Allonge'] = t.split(':')[1].strip()

        # Stats techniques
        stats['Coups/min'] = 0.0; stats['Précision'] = 0; stats['Takedown'] = 0.0; stats['DefLutte'] = 0
        for row in info_box:
            t = row.text.replace('\n', '').strip()
            if "SLpM:" in t: stats['Coups/min'] = float(t.split(':')[1])
            if "Str. Acc.:" in t: stats['Précision'] = int(t.split(':')[1].replace('%', ''))
            if "TD Avg.:" in t: stats['Takedown'] = float(t.split(':')[1])
            if "TD Def.:" in t: stats['DefLutte'] = int(t.split(':')[1].replace('%', ''))
            
        return stats
    except: return None

# --- 4. ALGO DE PRÉDICTION ---
def prediction(f1, f2):
    # Score basique
    score = 50 
    
    # 1. Striking
    diff_strike = f1['Coups/min'] - f2['Coups/min']
    score += diff_strike * 5 
    
    # 2. Lutte
    if f1['Takedown'] > 2.0 and f2['DefLutte'] < 60: score += 10
    if f2['Takedown'] > 2.0 and f1['DefLutte'] < 60: score -= 10
    
    # Bornes
    score = max(10, min(90, score))
    
    # Méthode
    method = "DÉCISION"
    if (f1['Coups/min'] + f2['Coups/min']) > 8: method = "KO / TKO"
    if (f1['Takedown'] + f2['Takedown']) > 4: method = "SOUMISSION"
    
    return round(score), method

# --- 5. INTERFACE UTILISATEUR (UI) ---

# HEADER
c_logo, c_title = st.columns([1, 4])
with c_title:
    st.markdown("<h1 style='color:white; margin-bottom:0;'>GETCAGEMETRICS ⚡</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8;'>L'intelligence artificielle pour vos paris MMA.</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# RECHERCHE (CARD STYLE)
st.markdown('<div class="metric-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)

url_a, url_b = None, None

with c1:
    st.markdown("**🔵 COMBATTANT 1**")
    name_a = st.text_input("Nom", key="a", placeholder="Ex: Benoit Saint Denis")
    if name_a:
        res = chercher_combattants(name_a)
        if res:
            sel_a = st.selectbox("Choisir", [r['nom'] for r in res], key="sa", label_visibility="collapsed")
            url_a = next(r['url'] for r in res if r['nom'] == sel_a)

with c2:
    st.markdown("**🔴 COMBATTANT 2**")
    name_b = st.text_input("Nom", key="b", placeholder="Ex: Dustin Poirier")
    if name_b:
        res = chercher_combattants(name_b)
        if res:
            sel_b = st.selectbox("Choisir", [r['nom'] for r in res], key="sb", label_visibility="collapsed")
            url_b = next(r['url'] for r in res if r['nom'] == sel_b)

st.markdown('</div>', unsafe_allow_html=True)

# BOUTON ACTION
if st.button("ANALYSER LE COMBAT"):
    if url_a and url_b:
        with st.spinner("Analyse des données en cours..."):
            f1 = get_stats(url_a)
            f2 = get_stats(url_b)
            
            if f1 and f2:
                # Calculs
                score_a, method = prediction(f1, f2)
                score_b = 100 - score_a
                winner = f1['Nom'] if score_a >= 50 else f2['Nom']
                win_prob = score_a if score_a >= 50 else score_b
                
                # --- AFFICHAGE RESULTATS ---
                
                # 1. PRÉDICTION CARD (La plus importante)
                st.markdown(f"""
                <div class="metric-card pred-box">
                    <div style="color:#94a3b8; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;">Vainqueur Probable</div>
                    <div style="font-size:2rem; font-weight:900; color:white; text-transform:uppercase; line-height:1.1;">{winner}</div>
                    <div class="win-prob">{win_prob}%</div>
                    <div class="method-tag">FINITION PRÉVUE : {method}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 2. TALE OF THE TAPE (Style Runnatic List)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="vs-header">
                        <div class="fighter-name" style="text-align:left; color:#38bdf8;">{f1['Nom']}</div>
                        <div class="vs-badge">VS</div>
                        <div class="fighter-name" style="text-align:right; color:#f472b6;">{f2['Nom']}</div>
                    </div>
                    
                    <div class="stat-row">
                        <div class="stat-val">{f1['Taille']}</div>
                        <div class="stat-label">Taille</div>
                        <div class="stat-val">{f2['Taille']}</div>
                    </div>

                    <div class="stat-row">
                        <div class="stat-val">{f1['Allonge']}</div>
                        <div class="stat-label">Allonge</div>
                        <div class="stat-val">{f2['Allonge']}</div>
                    </div>

                    <div class="stat-row">
                        <div class="stat-val">{f1['Coups/min']}</div>
                        <div class="stat-label">Frappes / min</div>
                        <div class="stat-val">{f2['Coups/min']}</div>
                    </div>
                    
                    <div class="stat-row">
                        <div class="stat-val">{f1['Takedown']}</div>
                        <div class="stat-label">Takedown / 15m</div>
                        <div class="stat-val">{f2['Takedown']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 3. BARRES COMPARATIVES (Visuel)
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("### 📊 DOMINATION STATISTIQUE")
                
                # Barre 1: Volume
                st.caption("Volume de coups (Debout)")
                vol_tot = f1['Coups/min'] + f2['Coups/min'] + 0.1
                pct_a = (f1['Coups/min'] / vol_tot) * 100
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; color:white;">
                    <span>{f1['Nom']}</span><span>{f2['Nom']}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-fill fill-green" style="width: {pct_a}%;"></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Barre 2: Lutte
                st.markdown("<br>", unsafe_allow_html=True)
                st.caption("Menace Lutte (Takedowns)")
                td_tot = f1['Takedown'] + f2['Takedown'] + 0.1
                pct_td_a = (f1['Takedown'] / td_tot) * 100
                st.markdown(f"""
                <div class="progress-container">
                    <div class="progress-fill fill-yellow" style="width: {pct_td_a}%;"></div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # 4. CALL TO ACTION (BETTING)
                st.markdown(f"""
                <a href="https://www.unibet.fr/sport/mma" target="_blank" class="bet-btn">
                    💰 PARIER SUR {winner} (Cote boostée)
                </a>
                <p style="text-align:center; color:#94a3b8; font-size:0.7rem; margin-top:10px;">
                    Les paris sportifs comportent des risques. Jouez avec modération.
                </p>
                """, unsafe_allow_html=True)

    else:
        st.error("Veuillez sélectionner les deux combattants.")
