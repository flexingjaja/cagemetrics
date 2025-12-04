import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURATION DE LA PAGE (Doit être la première ligne) ---
st.set_page_config(page_title="CageMetrics Pro", page_icon="🥊", layout="wide")

# --- 2. INJECTION CSS (Le Maquillage) ---
# C'est ici qu'on transforme le look moche en look Pro
st.markdown("""
<style>
    /* Fond général sombre */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Titre Principal */
    h1 {
        color: #FFFFFF;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Les sous-titres */
    h2, h3 {
        color: #ff4b4b; /* Rouge UFC */
    }
    
    /* Style des Metrics (Les gros chiffres) */
    div[data-testid="stMetric"] {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3d3d3d;
        text-align: center;
    }
    
    /* Bouton personnalisé */
    div.stButton > button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 20px;
        padding: 10px;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #ff0000;
        box-shadow: 0 0 10px #ff0000;
    }

    /* Carte de résultat (Custom HTML) */
    .result-card {
        background-color: #1c1c1c;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #ff4b4b;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. FONCTIONS MOTEUR (On garde la logique) ---
@st.cache_data
def chercher_combattants(nom_partiel):
    if not nom_partiel or len(nom_partiel) < 2: return []
    nom_clean = nom_partiel.strip().replace(' ', '+')
    try:
        response = requests.get(f"http://ufcstats.com/statistics/fighters/search?query={nom_clean}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        resultats = []
        for row in soup.find_all('tr', class_='b-statistics__table-row')[1:8]: # Max 7 résultats pour pas polluer
            link = row.find('a', href=True)
            if link: resultats.append({'nom': link.text.strip(), 'url': link['href']})
        return resultats
    except: return []

def get_fighter_stats(fighter_url):
    try:
        response = requests.get(fighter_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        stats = {'Coups/min': 0.0, 'Takedown Avg': 0.0, 'Défense Lutte (%)': 0, 'Précision': 0}
        
        title = soup.find('span', class_='b-content__title-highlight')
        stats['Nom'] = title.text.strip() if title else "Inconnu"
        
        for row in soup.find_all('li', class_='b-list__box-list-item'):
            text = row.text.replace('\n', '').strip()
            if "SLpM:" in text: stats['Coups/min'] = float(text.split(':')[1].strip())
            if "TD Avg.:" in text: stats['Takedown Avg'] = float(text.split(':')[1].strip())
            if "TD Def.:" in text: stats['Défense Lutte (%)'] = int(text.split(':')[1].strip().replace('%', ''))
            if "Str. Acc.:" in text: stats['Précision'] = int(text.split(':')[1].strip().replace('%', ''))
        return stats
    except: return None

# --- 4. L'INTERFACE GRAPHIQUE ---

# Header Centré
col_h1, col_h2, col_h3 = st.columns([1,2,1])
with col_h2:
    st.title("🥊 CAGEMETRICS")
    st.markdown("<p style='text-align: center; color: gray;'>L'intelligence artificielle au service de vos paris</p>", unsafe_allow_html=True)

st.divider()

# Zone de Recherche (Style Dashboard)
c1, c_mid, c2 = st.columns([1, 0.2, 1])

with c1:
    st.markdown("### 🔵 Coin Bleu")
    search_a = st.text_input("Rechercher combattant A", key="s_a", placeholder="Ex: Pereira")
    url_a = None
    if search_a:
        res_a = chercher_combattants(search_a)
        if res_a:
            opts_a = {r['nom']: r['url'] for r in res_a}
            sel_a = st.selectbox("Sélectionner A", list(opts_a.keys()), key="sel_a")
            url_a = opts_a[sel_a]

with c_mid:
    st.markdown("<h1 style='text-align: center; padding-top: 50px;'>VS</h1>", unsafe_allow_html=True)

with c2:
    st.markdown("### 🔴 Coin Rouge")
    search_b = st.text_input("Rechercher combattant B", key="s_b", placeholder="Ex: Ankalaev")
    url_b = None
    if search_b:
        res_b = chercher_combattants(search_b)
        if res_b:
            opts_b = {r['nom']: r['url'] for r in res_b}
            sel_b = st.selectbox("Sélectionner B", list(opts_b.keys()), key="sel_b")
            url_b = opts_b[sel_b]

# Bouton Action (Centré)
st.markdown("<br>", unsafe_allow_html=True)
b_col1, b_col2, b_col3 = st.columns([1, 1, 1])
with b_col2:
    bouton = st.button("ANALYSER LE COMBAT 🚀")

# --- 5. RESULTATS & VISUELS ---
if bouton and url_a and url_b:
    with st.spinner("Analyse des datas UFC..."):
        f1 = get_fighter_stats(url_a)
        f2 = get_fighter_stats(url_b)
        
        if f1 and f2:
            st.markdown("---")
            
            # TALE OF THE TAPE (Face à Face)
            t1, t2, t3, t4 = st.columns(4)
            t1.metric("Volume (Coups/min)", f1['Coups/min'], delta_color="off")
            t2.metric(f"{f1['Nom']}", "VS")
            t3.metric(f"{f2['Nom']}", "STATS")
            t4.metric("Volume (Coups/min)", f2['Coups/min'], delta_color="off")
            
            # VISUALISATION (Barres de progression)
            st.markdown("#### 📊 Comparatif Visuel")
            
            # Barre Striking
            st.caption(f"Activité Debout (Volume)")
            vol_total = f1['Coups/min'] + f2['Coups/min'] + 0.1
            st.progress(f1['Coups/min'] / vol_total)
            col_txt_a, col_txt_b = st.columns(2)
            col_txt_a.markdown(f"**{f1['Nom']}**")
            col_txt_b.markdown(f"<div style='text-align: right'>**{f2['Nom']}**</div>", unsafe_allow_html=True)

            # Barre Lutte
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption(f"Danger Sol (Takedowns/15min)")
            td_total = f1['Takedown Avg'] + f2['Takedown Avg'] + 0.1
            st.progress(f1['Takedown Avg'] / td_total)

            # L'ANALYSE (CARD DESIGN)
            st.markdown("### 🧠 L'Analyse de l'Algo")
            
            advice_html = ""
            
            # Logique
            if f1['Takedown Avg'] > 2.5 and f2['Défense Lutte (%)'] < 60:
                advice_html = f"""
                <div class="result-card">
                    <h3 style="color: #ff4b4b;">🚨 ALERTE GRAPPLING</h3>
                    <p style="font-size: 18px; color: #ddd;">
                        <strong>{f1['Nom']}</strong> possède un avantage critique au sol. La défense de {f2['Nom']} ({f2['Défense Lutte (%)']}%) 
                        est statistiquement trop faible pour résister 3 rounds.
                    </p>
                    <p>👉 <strong>Conseil :</strong> Parier sur {f1['Nom']} ou "Victoire par Soumission".</p>
                </div>
                """
            elif f1['Coups/min'] > (f2['Coups/min'] + 2.0):
                advice_html = f"""
                <div class="result-card" style="border-left: 5px solid #00cc00;">
                    <h3 style="color: #00cc00;">🥊 AVANTAGE VOLUME</h3>
                    <p style="font-size: 18px; color: #ddd;">
                        <strong>{f1['Nom']}</strong> est une mitraillette ({f1['Coups/min']} coups/min). 
                        Il va noyer {f2['Nom']} sous le volume.
                    </p>
                    <p>👉 <strong>Conseil :</strong> Victoire aux points (Décision) pour {f1['Nom']}.</p>
                </div>
                """
            else:
                 advice_html = f"""
                <div class="result-card" style="border-left: 5px solid #ffa500;">
                    <h3 style="color: #ffa500;">⚖️ COMBAT SERRÉ</h3>
                    <p style="font-size: 18px; color: #ddd;">
                        Les statistiques sont très proches. C'est un "Pile ou Face".
                    </p>
                    <p>👉 <strong>Conseil :</strong> Évitez de parier gros sur ce combat.</p>
                </div>
                """
            
            st.markdown(advice_html, unsafe_allow_html=True)
