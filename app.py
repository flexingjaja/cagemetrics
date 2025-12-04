import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
st.set_page_config(page_title="CageMetrics", page_icon="🥊")

# --- MOTEUR DE RECHERCHE OPTIMISÉ ---
def trouver_url_par_nom(nom_combattant):
    # On nettoie le nom (enlève les espaces inutiles)
    nom_clean = nom_combattant.strip()
    # On remplace les espaces par + pour l'URL
    query = nom_clean.replace(' ', '+')
    search_url = f"http://ufcstats.com/statistics/fighters/search?query={query}"
    
    # Déguisement complet pour ne pas être bloqué
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr', class_='b-statistics__table-row')
        
        # On parcourt les résultats pour trouver le bon
        for row in rows[1:]:
            link_tag = row.find('a', href=True)
            if link_tag:
                # On vérifie si le nom ressemble (pour éviter les erreurs)
                # Cette partie prend le premier résultat pertinent
                return link_tag['href']
        return None
    except:
        return None

def get_fighter_stats(fighter_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(fighter_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        stats = {}
        
        # Récupération sécurisée du nom
        title = soup.find('span', class_='b-content__title-highlight')
        stats['Nom'] = title.text.strip() if title else "Inconnu"
        
        # Valeurs par défaut
        stats['Coups/min'] = 0.0
        stats['Coups Reçus/min'] = 0.0
        stats['Takedown Avg'] = 0.0
        stats['Défense Lutte (%)'] = 0

        rows = soup.find_all('li', class_='b-list__box-list-item')
        for row in rows:
            text = row.text.replace('\n', '').strip()
            try:
                if "SLpM:" in text: stats['Coups/min'] = float(text.split(':')[1].strip())
                if "SApM:" in text: stats['Coups Reçus/min'] = float(text.split(':')[1].strip())
                if "TD Avg.:" in text: stats['Takedown Avg'] = float(text.split(':')[1].strip())
                if "TD Def.:" in text: stats['Défense Lutte (%)'] = int(text.split(':')[1].strip().replace('%', ''))
            except: continue
            
        return stats
    except: return None

# --- INTERFACE ---
st.title("🥊 CageMetrics V2")
st.write("Entrez les noms exacts (ex: Jon Jones, Ciryl Gane)")

c1, c2 = st.columns(2)
with c1:
    nom_a = st.text_input("Combattant 1")
with c2:
    nom_b = st.text_input("Combattant 2")

if st.button("Analyser"):
    if nom_a and nom_b:
        with st.spinner("Recherche en cours..."):
            url_a = trouver_url_par_nom(nom_a)
            url_b = trouver_url_par_nom(nom_b)
            
            if not url_a:
                st.error(f"❌ Impossible de trouver : {nom_a}. Vérifie l'orthographe sur Google.")
            elif not url_b:
                st.error(f"❌ Impossible de trouver : {nom_b}. Vérifie l'orthographe sur Google.")
            else:
                # Si on a les URLs, on lance les stats
                f1 = get_fighter_stats(url_a)
                f2 = get_fighter_stats(url_b)
                
                if f1 and f2:
                    st.success(f"Match trouvé : {f1['Nom']} vs {f2['Nom']}")
                    
                    # Affichage simple des metrics
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Frappes/min", f"{f1['Nom']}", f"{f1['Coups/min']}")
                    col_b.metric("Frappes/min", f"{f2['Nom']}", f"{f2['Coups/min']}")
                    
                    st.markdown("---")
                    st.subheader("💡 Analyse Rapide")
                    
                    # Logique simple
                    if f1['Takedown Avg'] > 2.0 and f2['Défense Lutte (%)'] < 50:
                        st.warning(f"⚠️ **Danger Sol :** {f1['Nom']} risque d'amener {f2['Nom']} au sol facilement.")
                    elif f1['Coups/min'] > f2['Coups/min'] + 2:
                        st.info(f"🥊 **Volume :** {f1['Nom']} est beaucoup plus actif debout.")
                    else:
                        st.write("Combat statistiquement serré.")
