import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="CageMetrics Ultimate", page_icon="🥊")

# --- FONCTION 1 : CHERCHER LES NOMS ---
@st.cache_data
def chercher_combattants(nom_partiel):
    """
    Cherche sur UFCStats et renvoie une liste de choix :
    Ex: [{'nom': 'Ilia Topuria', 'url': '...'}, {'nom': 'Aleksandre Topuria', 'url': '...'}]
    """
    if not nom_partiel or len(nom_partiel) < 2:
        return []

    nom_clean = nom_partiel.strip().replace(' ', '+')
    search_url = f"http://ufcstats.com/statistics/fighters/search?query={nom_clean}"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        resultats = []
        rows = soup.find_all('tr', class_='b-statistics__table-row')
        
        # On regarde les 10 premiers résultats max
        for row in rows[1:11]: 
            link_tag = row.find('a', href=True)
            if link_tag:
                nom = link_tag.text.strip()
                # On récupère aussi le surnom s'il existe pour aider à choisir
                cols = row.find_all('td')
                if len(cols) > 2:
                    surnom = cols[2].text.strip()
                    if surnom:
                        nom = f"{nom} ({surnom})"
                
                resultats.append({'nom': nom, 'url': link_tag['href']})
                
        return resultats
    except:
        return []

# --- FONCTION 2 : RECUPERER LES STATS ---
def get_fighter_stats(fighter_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(fighter_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        stats = {}
        
        title = soup.find('span', class_='b-content__title-highlight')
        stats['Nom'] = title.text.strip() if title else "Inconnu"
        
        stats['Coups/min'] = 0.0
        stats['Takedown Avg'] = 0.0
        stats['Défense Lutte (%)'] = 0

        rows = soup.find_all('li', class_='b-list__box-list-item')
        for row in rows:
            text = row.text.replace('\n', '').strip()
            try:
                if "SLpM:" in text: stats['Coups/min'] = float(text.split(':')[1].strip())
                if "TD Avg.:" in text: stats['Takedown Avg'] = float(text.split(':')[1].strip())
                if "TD Def.:" in text: stats['Défense Lutte (%)'] = int(text.split(':')[1].strip().replace('%', ''))
            except: continue
        return stats
    except: return None

# --- INTERFACE ---
st.title("🥊 CageMetrics : Recherche Totale")
st.write("Trouvez n'importe quel combattant parmi les milliers de l'UFC.")

col1, col2 = st.columns(2)

# --- ZONE COMBATTANT A ---
with col1:
    st.subheader("Combattant 1")
    recherche_a = st.text_input("Nom (ex: Topuria)", key="search_a")
    
    # Si l'utilisateur a écrit quelque chose, on cherche
    choix_possibles_a = []
    url_a_final = None
    
    if recherche_a:
        resultats_a = chercher_combattants(recherche_a)
        if resultats_a:
            # On crée une liste de noms pour le menu déroulant
            options_a = {r['nom']: r['url'] for r in resultats_a}
            nom_choisi_a = st.selectbox("Résultats trouvés :", list(options_a.keys()), key="select_a")
            # On stocke l'URL du gagnant
            url_a_final = options_a[nom_choisi_a]
        else:
            st.warning("Aucun combattant trouvé.")

# --- ZONE COMBATTANT B ---
with col2:
    st.subheader("Combattant 2")
    recherche_b = st.text_input("Nom (ex: Holloway)", key="search_b")
    
    choix_possibles_b = []
    url_b_final = None
    
    if recherche_b:
        resultats_b = chercher_combattants(recherche_b)
        if resultats_b:
            options_b = {r['nom']: r['url'] for r in resultats_b}
            nom_choisi_b = st.selectbox("Résultats trouvés :", list(options_b.keys()), key="select_b")
            url_b_final = options_b[nom_choisi_b]
        else:
            st.warning("Aucun combattant trouvé.")

st.markdown("---")

# --- BOUTON FINAL ---
if st.button("Lancer l'Analyse 🚀", type="primary"):
    if url_a_final and url_b_final:
        with st.spinner("Analyse des données en cours..."):
            f1 = get_fighter_stats(url_a_final)
            f2 = get_fighter_stats(url_b_final)
            
            if f1 and f2:
                st.success(f"Duel : {f1['Nom']} vs {f2['Nom']}")
                
                # STATS
                c1, c2, c3 = st.columns(3)
                c1.metric("Frappes/min", f"{f1['Nom']}", f1['Coups/min'])
                c2.metric("Frappes/min", f"{f2['Nom']}", f2['Coups/min'])
                c3.metric("Différence", round(f1['Coups/min'] - f2['Coups/min'], 2))

                # ANALYSE
                st.subheader("🧠 Analyse Stratégique")
                if f1['Takedown Avg'] > 2.0 and f2['Défense Lutte (%)'] < 55:
                    st.error(f"🚨 **MENACE SOL :** {f1['Nom']} va probablement dominer en lutte.")
                elif f2['Takedown Avg'] > 2.0 and f1['Défense Lutte (%)'] < 55:
                    st.error(f"🚨 **MENACE SOL :** {f2['Nom']} a l'avantage pour amener le combat au sol.")
                elif abs(f1['Coups/min'] - f2['Coups/min']) > 2:
                    st.info("🥊 Le combat risque de se jouer debout (Striking).")
                else:
                    st.warning("⚖️ C'est un 50/50 statistique.")
    else:
        st.error("Veuillez sélectionner deux combattants valides ci-dessus.")
