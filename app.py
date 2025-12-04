import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="CageMetrics - Analyse MMA",
    page_icon="🥊",
    layout="centered"
)

# --- FONCTIONS (MOTEUR) ---
def trouver_url_par_nom(nom_combattant):
    try:
        query = nom_combattant.replace(' ', '+')
        search_url = f"http://ufcstats.com/statistics/fighters/search?query={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr', class_='b-statistics__table-row')
        for row in rows[1:]:
            link = row.find('a', href=True)
            if link:
                return link['href']
        return None
    except:
        return None

def get_fighter_stats(fighter_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(fighter_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        stats = {}
        
        title_tag = soup.find('span', class_='b-content__title-highlight')
        stats['Nom'] = title_tag.text.strip() if title_tag else "Inconnu"
        
        # Valeurs par défaut
        stats['Coups/min'] = 0.0
        stats['Coups Reçus/min'] = 0.0
        stats['Takedown Avg'] = 0.0
        stats['Défense Lutte (%)'] = 0
        stats['Précision (%)'] = 0

        stat_rows = soup.find_all('li', class_='b-list__box-list-item')
        for row in stat_rows:
            text = row.text.replace('\n', '').strip()
            try:
                if "SLpM:" in text: stats['Coups/min'] = float(text.split(':')[1].strip())
                if "SApM:" in text: stats['Coups Reçus/min'] = float(text.split(':')[1].strip())
                if "TD Avg.:" in text: stats['Takedown Avg'] = float(text.split(':')[1].strip())
                if "TD Def.:" in text: stats['Défense Lutte (%)'] = int(text.split(':')[1].strip().replace('%', ''))
                if "Str. Acc.:" in text: stats['Précision (%)'] = int(text.split(':')[1].strip().replace('%', ''))
            except: continue
        return stats
    except: return None

# --- INTERFACE UTILISATEUR (FRONTEND) ---
st.title("🥊 CageMetrics")
st.markdown("### L'avantage statistique pour vos paris MMA")
st.markdown("---")

# Zone de saisie
col1, col2 = st.columns(2)
with col1:
    nom_a = st.text_input("Combattant A", placeholder="Ex: Ciryl Gane")
with col2:
    nom_b = st.text_input("Combattant B", placeholder="Ex: Jon Jones")

bouton = st.button("Lancer l'Analyse 🚀", type="primary")

if bouton and nom_a and nom_b:
    with st.spinner('Recherche des données dans l\'Octogone...'):
        url_a = trouver_url_par_nom(nom_a)
        url_b = trouver_url_par_nom(nom_b)

        if not url_a or not url_b:
            st.error("❌ Impossible de trouver l'un des combattants. Vérifie l'orthographe.")
        else:
            f1 = get_fighter_stats(url_a)
            f2 = get_fighter_stats(url_b)

            if f1 and f2:
                st.success(f"Duel trouvé : {f1['Nom']} vs {f2['Nom']}")
                
                # AFFICHAGE DES STATS (METRICS)
                st.markdown("#### 👊 Striking (Debout)")
                c1, c2, c3 = st.columns(3)
                c1.metric("Volume (Coups/min)", f"{f1['Nom']}", f"{f1['Coups/min']}")
                c2.metric("Volume (Coups/min)", f"{f2['Nom']}", f"{f2['Coups/min']}")
                delta_strike = round(f1['Coups/min'] - f2['Coups/min'], 2)
                c3.metric("Différence", f"{delta_strike}", delta_color="normal")

                st.markdown("#### 🤼 Grappling (Lutte)")
                g1, g2 = st.columns(2)
                g1.metric(f"Takedowns {f1['Nom']}", f"{f1['Takedown Avg']}/15min")
                g2.metric(f"Défense Lutte {f2['Nom']}", f"{f2['Défense Lutte (%)']}%")

                st.markdown("---")
                st.subheader("🧠 L'Analyse CageMetrics")
                
                # LOGIQUE D'ANALYSE
                analysis_made = False
                
                # Scénario Lutte
                if f1['Takedown Avg'] > 2.5 and f2['Défense Lutte (%)'] < 60:
                    st.warning(f"🚨 **ALERTE LUTTE :** {f1['Nom']} possède une lutte offensive élevée et {f2['Nom']} défend mal.")
                    st.info("💡 **Conseil :** Regarde les cotes pour une victoire de **" + f1['Nom'] + "** ou une victoire par soumission.")
                    analysis_made = True
                elif f2['Takedown Avg'] > 2.5 and f1['Défense Lutte (%)'] < 60:
                    st.warning(f"🚨 **ALERTE LUTTE :** {f2['Nom']} va probablement amener le combat au sol.")
                    st.info("💡 **Conseil :** Avantage statistique pour **" + f2['Nom'] + "**.")
                    analysis_made = True
                
                # Scénario Volume
                if f1['Coups/min'] > (f2['Coups/min'] + 2.0):
                     st.info(f"📈 **AVANTAGE VOLUME :** {f1['Nom']} est beaucoup plus actif. Si le combat va à la décision, il a l'avantage.")
                     analysis_made = True
                elif f2['Coups/min'] > (f1['Coups/min'] + 2.0):
                     st.info(f"📈 **AVANTAGE VOLUME :** {f2['Nom']} touche beaucoup plus souvent.")
                     analysis_made = True

                if not analysis_made:
                    st.write("ℹ️ Les statistiques sont très serrées. Pas d'avantage évident détecté par l'algorithme.")
