import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Pro", page_icon="🥊")

# --- LISTE DES STARS (Pour le menu déroulant) ---
# Tu pourras ajouter des noms ici toi-même !
STARS_UFC = [
    "Alex Pereira", "Islam Makhachev", "Jon Jones", "Ilia Topuria", "Dricus Du Plessis",
    "Sean O'Malley", "Max Holloway", "Charles Oliveira", "Justin Gaethje", "Dustin Poirier",
    "Benoit Saint Denis", "Ciryl Gane", "Manon Fiorot", "Nassourdine Imavov", "Khamzat Chimaev",
    "Conor McGregor", "Israel Adesanya", "Kamaru Usman", "Leon Edwards", "Alexander Volkanovski",
    "Tom Aspinall", "Sergei Pavlovich", "Jiri Prochazka", "Jamahal Hill", "Robert Whittaker",
    "Dricus Du Plessis", "Sean Strickland", "Colby Covington", "Shavkat Rakhmonov", "Gilbert Burns",
    "Merab Dvalishvili", "Aljamain Sterling", "Cory Sandhagen", "Petr Yan", "Marlon Vera",
    "Alexandre Pantoja", "Brandon Moreno", "Brandon Royval", "Amir Albazi", "Zhang Weili",
    "Alexa Grasso", "Valentina Shevchenko", "Erin Blanchfield", "Tatiana Suarez", "Rose Namajunas"
]
STARS_UFC.sort() # On trie par ordre alphabétique

# --- MOTEUR DE RECHERCHE ---
@st.cache_data # Garde en mémoire pour ne pas ralentir
def trouver_url_par_nom(nom_combattant):
    nom_clean = nom_combattant.strip()
    query = nom_clean.replace(' ', '+')
    search_url = f"http://ufcstats.com/statistics/fighters/search?query={query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr', class_='b-statistics__table-row')
        
        for row in rows[1:]:
            link_tag = row.find('a', href=True)
            if link_tag:
                return link_tag['href']
        return None
    except:
        return None

def get_fighter_stats(fighter_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(fighter_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        stats = {}
        
        title = soup.find('span', class_='b-content__title-highlight')
        stats['Nom'] = title.text.strip() if title else "Inconnu"
        
        # Valeurs par défaut
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
st.title("🥊 CageMetrics : Selecteur Rapide")
st.markdown("Sélectionnez les combattants dans la liste ou tapez pour chercher.")

col1, col2 = st.columns(2)

# FONCTION POUR GÉRER LE CHOIX
def selectionner_combattant(label, key):
    # On ajoute une option "Autre" pour les recherches manuelles
    choix = st.selectbox(
        label, 
        options=STARS_UFC + ["🔍 Autre (Recherche manuelle)"], 
        index=None, 
        placeholder="Tapez un nom...",
        key=key
    )
    
    nom_final = None
    if choix == "🔍 Autre (Recherche manuelle)":
        nom_final = st.text_input(f"Entrez le nom pour {label}")
    elif choix:
        nom_final = choix
        
    return nom_final

with col1:
    fighter_a = selectionner_combattant("Combattant A (Favori)", "f1")
with col2:
    fighter_b = selectionner_combattant("Combattant B (Outsider)", "f2")

# BOUTON D'ACTION
if st.button("Lancer l'Analyse 🚀", type="primary"):
    if fighter_a and fighter_b:
        with st.spinner(f"Analyse : {fighter_a} vs {fighter_b}..."):
            url_a = trouver_url_par_nom(fighter_a)
            url_b = trouver_url_par_nom(fighter_b)
            
            if url_a and url_b:
                stats_a = get_fighter_stats(url_a)
                stats_b = get_fighter_stats(url_b)
                
                if stats_a and stats_b:
                    st.success("✅ Données récupérées !")
                    
                    # AFFICHAGE DUEL
                    st.markdown(f"### {stats_a['Nom']} vs {stats_b['Nom']}")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Frappes/min", f"{stats_a['Nom']}", stats_a['Coups/min'])
                    c2.metric("Frappes/min", f"{stats_b['Nom']}", stats_b['Coups/min'])
                    diff = round(stats_a['Coups/min'] - stats_b['Coups/min'], 2)
                    c3.metric("Différence", diff)
                    
                    st.markdown("---")
                    
                    # ANALYSE INTELLIGENTE
                    if stats_a['Takedown Avg'] > 2.0 and stats_b['Défense Lutte (%)'] < 55:
                        st.error(f"🚨 **ALERTE SOL :** {stats_a['Nom']} a un gros avantage en lutte !")
                    elif stats_b['Takedown Avg'] > 2.0 and stats_a['Défense Lutte (%)'] < 55:
                        st.error(f"🚨 **ALERTE SOL :** {stats_b['Nom']} a un gros avantage en lutte !")
                    elif stats_a['Coups/min'] > stats_b['Coups/min'] + 2:
                        st.info(f"🥊 **AVANTAGE DEBOUT :** {stats_a['Nom']} envoie beaucoup plus de volume.")
                    else:
                        st.warning("⚖️ **COMBAT SERRÉ :** Pas d'avantage statistique flagrant.")
                else:
                    st.error("Erreur lors de la lecture des stats.")
            else:
                st.error("Impossible de trouver un des combattants.")
    else:
        st.warning("Veuillez sélectionner deux combattants.")
