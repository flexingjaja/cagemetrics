import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# --- 1. CONFIGURATION DESIGN & PAGE ---
st.set_page_config(page_title="CageMetrics Elite", page_icon="🦁", layout="wide")

# CSS "TV BROADCAST STYLE" (Noir & Or)
st.markdown("""
<style>
    /* Fond noir profond */
    .stApp { background-color: #000000; }
    
    /* Titres */
    h1, h2, h3 { color: white; font-family: 'Impact', sans-serif; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Inputs */
    .stTextInput > div > div > input { color: white; background-color: #1a1a1a; border: 1px solid #333; }
    
    /* Tale of the Tape Container */
    .tale-tape {
        background: linear-gradient(180deg, #1a1a1a 0%, #000000 100%);
        border: 2px solid #D4AF37; /* OR */
        border-radius: 0px;
        padding: 20px;
        margin-bottom: 30px;
    }
    
    .row-stat {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #333;
        padding: 10px 0;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        font-size: 18px;
    }
    
    .fighter-name { font-size: 28px; font-weight: 900; color: #D4AF37; text-transform: uppercase; }
    .stat-label { color: #888; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; }
    .stat-val { color: white; width: 100px; text-align: center; }
    
    /* Prediction Box */
    .pred-box {
        background-color: #111;
        border: 1px solid #333;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
    }
    .win-prob { font-size: 40px; font-weight: bold; color: #00ff00; }
    
</style>
""", unsafe_allow_html=True)

# --- 2. MOTEUR DATA (Optimisé) ---
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
        stats = {'Coups/min': 0.0, 'Précision': 0, 'Coups Reçus': 0.0, 'Takedown Avg': 0.0, 'Défense TD': 0, 'Soumission Avg': 0.0}
        
        # Nom
        stats['Nom'] = soup.find('span', class_='b-content__title-highlight').text.strip()
        
        # Récupération physique (Taille/Allonge) - Souvent manquant ou mal formaté, on simule pour l'affichage si vide
        stats['Taille'] = "N/A"
        stats['Allonge'] = "N/A"
        
        info_box = soup.find_all('li', class_='b-list__box-list-item')
        for item in info_box:
            t = item.text.strip()
            if "Height:" in t: stats['Taille'] = t.split(':')[1].strip()
            if "Reach:" in t: stats['Allonge'] = t.split(':')[1].strip()

        # Stats techniques
        for row in info_box:
            t = row.text.replace('\n', '').strip()
            if "SLpM:" in t: stats['Coups/min'] = float(t.split(':')[1])
            if "Str. Acc.:" in t: stats['Précision'] = int(t.split(':')[1].replace('%', ''))
            if "SApM:" in t: stats['Coups Reçus'] = float(t.split(':')[1])
            if "TD Avg.:" in t: stats['Takedown Avg'] = float(t.split(':')[1])
            if "TD Def.:" in t: stats['Défense TD'] = int(t.split(':')[1].replace('%', ''))
            if "Sub. Avg.:" in t: stats['Soumission Avg'] = float(t.split(':')[1])
            
        return stats
    except: return None

# --- 3. ALGORITHME DE PREDICTION (Le Cerveau) ---
def calculer_prediction(f1, f2):
    """
    Simule une probabilité basée sur les stats.
    Ceci est une heuristique, pas une vérité absolue.
    """
    score_a = 50
    
    # 1. Facteur Striking (Volume & Précision)
    diff_strike = (f1['Coups/min'] * (f1['Précision']/100)) - (f2['Coups/min'] * (f2['Précision']/100))
    score_a += diff_strike * 4 # Poids de 4
    
    # 2. Facteur Dommages (Défense)
    diff_def = (f2['Coups Reçus'] - f1['Coups Reçus']) # Si f1 prend moins de coups, il gagne des points
    score_a += diff_def * 3
    
    # 3. Facteur Lutte (Le "Game Changer")
    if f1['Takedown Avg'] > f2['Takedown Avg']:
        # Si f1 est lutteur, est-ce que f2 défend bien ?
        if f2['Défense TD'] < 60:
            score_a += 10 # Gros bonus si la défense est nulle
        else:
            score_a += 2 # Petit bonus si la défense est bonne
    elif f2['Takedown Avg'] > f1['Takedown Avg']:
        if f1['Défense TD'] < 60:
            score_a -= 10
        else:
            score_a -= 2

    # Bornage entre 5% et 95%
    score_a = max(5, min(95, score_a))
    
    # Calcul Probabilités Finition
    method = {"KO": 20, "Sub": 10, "Dec": 70} # Base
    
    # Ajustement méthode
    power_factor = (f1['Coups/min'] + f2['Coups/min']) / 2
    grapple_factor = (f1['Takedown Avg'] + f2['Takedown Avg']) + (f1['Soumission Avg'] + f2['Soumission Avg'])
    
    if power_factor > 5: method["KO"] += 30; method["Dec"] -= 30
    if grapple_factor > 2.5: method["Sub"] += 30; method["Dec"] -= 30
    if grapple_factor > 5: method["Sub"] += 20; method["KO"] -= 20
    
    # Normalisation
    total = sum(method.values())
    method = {k: round(v/total*100) for k, v in method.items()}
    
    return round(score_a), method

# --- 4. INTERFACE ---

st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🦁 CAGEMETRICS <span style='font-size: 20px; color: white;'>LAS VEGAS EDITION</span></h1>", unsafe_allow_html=True)
st.markdown("---")

# SELECTION
c1, c2, c3 = st.columns([1, 0.2, 1])
with c1:
    s_a = st.text_input("COMBATTANT 1 (Rouge)", placeholder="Ex: Jon Jones")
    u_a = None
    if s_a:
        r = chercher_combattants(s_a)
        if r:
            x = st.selectbox("", [i['nom'] for i in r], key="1")
            u_a = next(item['url'] for item in r if item["nom"] == x)

with c3:
    s_b = st.text_input("COMBATTANT 2 (Bleu)", placeholder="Ex: Aspinall")
    u_b = None
    if s_b:
        r = chercher_combattants(s_b)
        if r:
            x = st.selectbox("", [i['nom'] for i in r], key="2")
            u_b = next(item['url'] for item in r if item["nom"] == x)

if st.button("LANCER LA SIMULATION DU COMBAT", type="primary", use_container_width=True):
    if u_a and u_b:
        with st.spinner("Analyse des styles... Calcul des probabilités..."):
            f1 = get_stats(u_a)
            f2 = get_stats(u_b)
            
            if f1 and f2:
                # Calculs
                prob_a, methods = calculer_prediction(f1, f2)
                prob_b = 100 - prob_a
                
                # --- AFFICHAGE TALE OF THE TAPE (HTML PUR) ---
                st.markdown(f"""
                <div class="tale-tape">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <span style="color: #888; letter-spacing: 3px;">TALE OF THE TAPE</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <div class="fighter-name" style="color: #ff4b4b;">{f1['Nom']}</div>
                        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/UFC_logo.svg/2560px-UFC_logo.svg.png" width="50" style="opacity: 0.5;">
                        <div class="fighter-name" style="color: #4b88ff;">{f2['Nom']}</div>
                    </div>

                    <div class="row-stat"><div class="stat-val">{f1['Taille']}</div><div class="stat-label">TAILLE</div><div class="stat-val">{f2['Taille']}</div></div>
                    <div class="row-stat"><div class="stat-val">{f1['Allonge']}</div><div class="stat-label">ALLONGE</div><div class="stat-val">{f2['Allonge']}</div></div>
                    <div class="row-stat"><div class="stat-val">{f1['Coups/min']}</div><div class="stat-label">FRAPPES / MIN</div><div class="stat-val">{f2['Coups/min']}</div></div>
                    <div class="row-stat"><div class="stat-val">{f1['Précision']}%</div><div class="stat-label">PRÉCISION</div><div class="stat-val">{f2['Précision']}%</div></div>
                    <div class="row-stat"><div class="stat-val">{f1['Takedown Avg']}</div><div class="stat-label">TAKEDOWNS / 15M</div><div class="stat-val">{f2['Takedown Avg']}</div></div>
                    <div class="row-stat"><div class="stat-val">{f1['Défense TD']}%</div><div class="stat-label">DÉFENSE LUTTE</div><div class="stat-val">{f2['Défense TD']}%</div></div>
                </div>
                """, unsafe_allow_html=True)

                # --- ZONE DE PREDICTION ---
                st.markdown("### 🔮 PRÉDICTION I.A.")
                
                col_pred1, col_pred2 = st.columns(2)
                
                # Jauge de victoire
                with col_pred1:
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = prob_a,
                        title = {'text': f"Chances de victoire<br>{f1['Nom']}"},
                        number = {'suffix': "%", 'font': {'color': "white"}},
                        gauge = {
                            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "#ff4b4b"},
                            'bgcolor': "black",
                            'borderwidth': 2,
                            'bordercolor': "gray",
                            'steps': [
                                {'range': [0, 50], 'color': '#333'},
                                {'range': [50, 100], 'color': '#111'}],
                        }))
                    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white", 'family': "Arial"})
                    st.plotly_chart(fig, use_container_width=True)

                # Graphique Méthode
                with col_pred2:
                    labels = ['KO/TKO', 'SOUMISSION', 'DÉCISION']
                    values = [methods['KO'], methods['Sub'], methods['Dec']]
                    colors = ['#FF4136', '#FFDC00', '#0074D9'] # Rouge, Jaune, Bleu

                    fig2 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, marker=dict(colors=colors))])
                    fig2.update_layout(
                        title_text="Scénario le plus probable", 
                        paper_bgcolor = "rgba(0,0,0,0)", 
                        font = {'color': "white"},
                        showlegend=True
                    )
                    st.plotly_chart(fig2, use_container_width=True)

                # --- VERDICT FINAL & BETTING ---
                winner = f1['Nom'] if prob_a >= 50 else f2['Nom']
                confidence = prob_a if prob_a >= 50 else prob_b
                
                bet_color = "#00ff00" if confidence > 65 else "#ffa500"
                
                st.markdown(f"""
                <div class="pred-box" style="border-color: {bet_color};">
                    <h2 style="color: white; margin-bottom: 0;">LE PARI INTELLIGENT</h2>
                    <div style="font-size: 50px; color: {bet_color}; font-weight: bold;">{winner}</div>
                    <div style="font-size: 20px; color: #ccc;">Indice de confiance : {confidence}%</div>
                    <br>
                    <a href="https://www.unibet.fr/sport/mma" target="_blank">
                        <button style="background-color: {bet_color}; color: black; font-weight: bold; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 18px;">
                            PARIER SUR {winner} ➔
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
