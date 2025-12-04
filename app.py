import streamlit as st
import requests
from bs4 import BeautifulSoup
import random

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics", page_icon="⚡", layout="centered")

# --- 2. DATA : ROSTER ---
ROSTER = {
    "🏆 P4P / Stars": ["Jon Jones", "Islam Makhachev", "Alex Pereira", "Ilia Topuria", "Sean O'Malley", "Conor McGregor", "Max Holloway", "Charles Oliveira", "Dustin Poirier", "Justin Gaethje", "Khamzat Chimaev", "Israel Adesanya", "Benoit Saint Denis", "Ciryl Gane"],
    "Poids Lourds (HW)": ["Jon Jones", "Tom Aspinall", "Ciryl Gane", "Sergei Pavlovich", "Curtis Blaydes", "Jailton Almeida", "Alexander Volkov", "Stipe Miocic", "Derrick Lewis"],
    "Poids Mi-Lourds (LHW)": ["Alex Pereira", "Jiri Prochazka", "Magomed Ankalaev", "Jan Blachowicz", "Jamahal Hill", "Khalil Rountree Jr.", "Johnny Walker"],
    "Poids Moyens (MW)": ["Dricus Du Plessis", "Sean Strickland", "Israel Adesanya", "Robert Whittaker", "Nassourdine Imavov", "Jared Cannonier", "Marvin Vettori", "Khamzat Chimaev", "Paulo Costa"],
    "Poids Mi-Moyens (WW)": ["Belal Muhammad", "Leon Edwards", "Kamaru Usman", "Shavkat Rakhmonov", "Jack Della Maddalena", "Gilbert Burns", "Ian Machado Garry", "Colby Covington"],
    "Poids Légers (LW)": ["Islam Makhachev", "Arman Tsarukyan", "Charles Oliveira", "Justin Gaethje", "Dustin Poirier", "Michael Chandler", "Mateusz Gamrot", "Benoit Saint Denis", "Dan Hooker", "Paddy Pimblett"],
    "Poids Plumes (FW)": ["Ilia Topuria", "Alexander Volkanovski", "Max Holloway", "Brian Ortega", "Yair Rodriguez", "Movsar Evloev", "Arnold Allen", "Diego Lopes"],
    "Poids Coqs (BW)": ["Merab Dvalishvili", "Sean O'Malley", "Cory Sandhagen", "Petr Yan", "Marlon Vera", "Henry Cejudo", "Umar Nurmagomedov"]
}

# --- 3. BASE DE SECOURS (SI LE SITE PLANTE) ---
# Données réelles hardcodées pour éviter l'erreur "Impossible de récupérer" sur les stars
BACKUP_DB = {
    "Jon Jones": {"Taille": "6' 4\"", "Allonge": "84\"", "Coups": 4.30, "TD": 1.85, "DefLutte": 95, "Preci": 58},
    "Stipe Miocic": {"Taille": "6' 4\"", "Allonge": "80\"", "Coups": 4.82, "TD": 1.86, "DefLutte": 70, "Preci": 53},
    "Alex Pereira": {"Taille": "6' 4\"", "Allonge": "79\"", "Coups": 5.10, "TD": 0.20, "DefLutte": 70, "Preci": 62},
    "Ilia Topuria": {"Taille": "5' 7\"", "Allonge": "69\"", "Coups": 4.40, "TD": 1.92, "DefLutte": 92, "Preci": 46},
    "Max Holloway": {"Taille": "5' 11\"", "Allonge": "69\"", "Coups": 7.17, "TD": 0.30, "DefLutte": 84, "Preci": 48},
    "Islam Makhachev": {"Taille": "5' 10\"", "Allonge": "70\"", "Coups": 2.46, "TD": 3.17, "DefLutte": 90, "Preci": 60},
    "Benoit Saint Denis": {"Taille": "5' 11\"", "Allonge": "73\"", "Coups": 5.70, "TD": 4.55, "DefLutte": 68, "Preci": 54},
    "Dustin Poirier": {"Taille": "5' 9\"", "Allonge": "72\"", "Coups": 5.45, "TD": 1.36, "DefLutte": 63, "Preci": 51},
    "Conor McGregor": {"Taille": "5' 9\"", "Allonge": "74\"", "Coups": 5.32, "TD": 0.67, "DefLutte": 66, "Preci": 49},
    "Ciryl Gane": {"Taille": "6' 4\"", "Allonge": "81\"", "Coups": 5.11, "TD": 0.60, "DefLutte": 45, "Preci": 59},
    "Tom Aspinall": {"Taille": "6' 5\"", "Allonge": "78\"", "Coups": 7.72, "TD": 3.50, "DefLutte": 100, "Preci": 66},
    "Khamzat Chimaev": {"Taille": "6' 2\"", "Allonge": "75\"", "Coups": 5.72, "TD": 4.00, "DefLutte": 100, "Preci": 59}
}

# --- 4. CSS RUNNATIC ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800;900&display=swap');
    .stApp { background-color: #020617; font-family: 'Montserrat', sans-serif; }
    h1, h2, h3, div, p { font-family: 'Montserrat', sans-serif !important; }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); border-radius: 20px;
        padding: 20px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 15px;
    }
    div.stButton > button {
        background: #2ecc71 !important; color: #022c22 !important; border-radius: 12px !important;
        font-weight: 900 !important; padding: 16px !important; width: 100%; border: none !important;
    }
    .winner { font-size: 2.5rem; font-weight: 900; color: white; text-transform: uppercase; margin: 5px 0; }
    .pct { background: #2ecc71; color: #020617; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.85rem; }
    
    /* Barres de stats finish */
    .finish-bar { display: flex; height: 20px; border-radius: 10px; overflow: hidden; margin-top: 10px; }
    .seg-ko { background: #ef4444; }
    .seg-sub { background: #eab308; }
    .seg-dec { background: #3b82f6; }
    .legend { display: flex; justify-content: space-between; font-size: 0.7rem; color: #cbd5e1; font-weight: 700; margin-top: 5px; }

</style>
""", unsafe_allow_html=True)

# --- 5. MOTEUR HYBRIDE (SCRAPING + BACKUP) ---
@st.cache_data
def get_fighter_data(name):
    # 1. Vérifier la base de secours d'abord (Zéro chargement)
    if name in BACKUP_DB:
        data = BACKUP_DB[name]
        data['Nom'] = name
        return data

    # 2. Sinon, on tente le scraping
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        url = f"http://ufcstats.com/statistics/fighters/search?query={name.replace(' ', '+')}"
        resp = requests.get(url, headers=headers, timeout=4)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Trouver le lien
        target_url = None
        rows = soup.find_all('tr', class_='b-statistics__table-row')
        if len(rows) > 1:
            target_url = rows[1].find('a', href=True)['href'] # Prend le 1er résultat

        if target_url:
            r2 = requests.get(target_url, headers=headers, timeout=4)
            s2 = BeautifulSoup(r2.content, 'html.parser')
            stats = {'Nom': name, 'Taille': '-', 'Allonge': '-', 'Coups': 0.0, 'TD': 0.0, 'DefLutte': 0, 'Preci': 0}
            
            # Parsing
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
    except:
        return None
    return None

# --- 6. LOGIQUE DE FINISH ---
def calculate_finish_probs(f1, f2):
    """Calcule les probabilités de KO, SUB, DECISION"""
    
    # Facteur de violence (Volume + Précision)
    violence_score = (f1['Coups'] + f2['Coups']) * 0.8
    # Facteur de grappling (Takedowns)
    grapple_score = (f1['TD'] + f2['TD']) * 1.5
    
    # Base de probabilité de finish (plus les stats sont hautes, moins ça va à la décision)
    finish_chance = 30 + (violence_score * 3) + (grapple_score * 4)
    finish_chance = min(90, max(20, finish_chance)) # Borné entre 20% et 90%
    
    dec_prob = 100 - finish_chance
    
    # Répartition KO vs SUB dans le finish chance
    # Si beaucoup de grappling -> Sub augmente
    total_factor = violence_score + grapple_score
    ko_ratio = violence_score / total_factor if total_factor > 0 else 0.7
    
    ko_prob = finish_chance * ko_ratio
    sub_prob = finish_chance * (1 - ko_ratio)
    
    # Ajustement si l'un est un pur striker (Pereira)
    if f1['TD'] < 0.5 and f2['TD'] < 0.5:
        ko_prob += 15
        sub_prob -= 15
        if sub_prob < 0: sub_prob = 5

    return int(ko_prob), int(sub_prob), int(dec_prob)

# --- 7. INTERFACE ---
st.markdown("<h1 style='text-align:center; color:white;'>CAGEMETRICS <span style='color:#2ecc71'>V10</span></h1>", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
cat = st.selectbox("Catégorie", list(ROSTER.keys()), label_visibility="collapsed")
fighters = ROSTER[cat]
c1, c2, c3 = st.columns([1, 0.2, 1])
with c1: f_a = st.selectbox("A", fighters, index=0, label_visibility="collapsed", key="a")
with c2: st.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:#fff;'>VS</div>", unsafe_allow_html=True)
with c3: f_b = st.selectbox("B", fighters, index=1 if len(fighters)>1 else 0, label_visibility="collapsed", key="b")
st.markdown('</div>', unsafe_allow_html=True)

if st.button("SIMULER LE COMBAT"):
    if f_a == f_b:
        st.warning("Même combattant sélectionné.")
    else:
        s1 = get_fighter_data(f_a)
        s2 = get_fighter_data(f_b)
        
        if s1 and s2:
            # Score Vainqueur
            score = 50 + (s1['Coups'] - s2['Coups']) * 5
            if s1['TD'] > 2.5 and s2['DefLutte'] < 65: score += 15
            if s2['TD'] > 2.5 and s1['DefLutte'] < 65: score -= 15
            score = max(10, min(90, score))
            winner = s1['Nom'] if score >= 50 else s2['Nom']
            pct = int(score if score >= 50 else 100 - score)

            # Proba Finish
            p_ko, p_sub, p_dec = calculate_finish_probs(s1, s2)

            # --- AFFICHAGE ---
            
            # 1. CARTE VAINQUEUR
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; border: 2px solid #2ecc71; background: rgba(46, 204, 113, 0.05);">
                <div style="color:#94a3b8; font-size:0.7rem; font-weight:700;">VAINQUEUR PRÉDIT</div>
                <div class="winner">{winner}</div>
                <span class="pct">{pct}% DE CONFIANCE</span>
            </div>
            """, unsafe_allow_html=True)

            # 2. BARRE DE PROBABILITÉ DE FINISH (NOUVEAU !)
            st.markdown(f"""
            <div class="glass-card">
                <div style="text-align:center; margin-bottom:10px; font-weight:800; color:white;">MÉTHODE DE VICTOIRE</div>
                <div class="finish-bar">
                    <div class="seg-ko" style="width: {p_ko}%;"></div>
                    <div class="seg-sub" style="width: {p_sub}%;"></div>
                    <div class="seg-dec" style="width: {p_dec}%;"></div>
                </div>
                <div class="legend">
                    <span style="color:#ef4444;">KO/TKO {p_ko}%</span>
                    <span style="color:#eab308;">SOUMISSION {p_sub}%</span>
                    <span style="color:#3b82f6;">DÉCISION {p_dec}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 3. STATS
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            def row(lbl, v1, v2):
                st.markdown(f"""<div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                    <div style="color:#38bdf8; font-weight:700;">{v1}</div>
                    <div style="color:#94a3b8; font-size:0.7rem; font-weight:700;">{lbl}</div>
                    <div style="color:#f43f5e; font-weight:700;">{v2}</div></div>""", unsafe_allow_html=True)
            
            row("Taille", s1['Taille'], s2['Taille'])
            row("Coups / min", s1['Coups'], s2['Coups'])
            row("Takedowns", s1['TD'], s2['TD'])
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f"""<a href="https://www.unibet.fr/sport/mma" target="_blank"><button style="margin-top:10px;">PARIER SUR {winner}</button></a>""", unsafe_allow_html=True)

        else:
            st.error("Données indisponibles. Réessayez plus tard.")
