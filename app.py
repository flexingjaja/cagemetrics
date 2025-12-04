import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="CageMetrics Pro", page_icon="⚡", layout="centered")

# --- 2. GESTION LANGUE & UNITÉS ---
if 'lang' not in st.session_state: st.session_state.lang = 'fr'

def set_fr(): st.session_state.lang = 'fr'
def set_en(): st.session_state.lang = 'en'

T = {
    "fr": { "sub": "L'outil d'analyse prédictive MMA de référence", "sel": "SÉLECTION DU MATCHUP", "btn": "LANCER L'ANALYSE", "win": "VAINQUEUR PRÉDIT", "conf": "CONFIANCE", "meth": "PROBABILITÉS DE FINISH", "tech": "COMPARATIF TECHNIQUE", "lbl": ["Taille", "Allonge", "Frappes/min", "Précision", "Takedowns/15m", "Déf. Lutte"], "cta": "PARIER SUR", "err": "Veuillez sélectionner deux combattants différents." },
    "en": { "sub": "The Ultimate MMA Predictive Analytics Tool", "sel": "MATCHUP SELECTION", "btn": "ANALYZE FIGHT", "win": "PREDICTED WINNER", "conf": "CONFIDENCE", "meth": "FINISH PROBABILITY", "tech": "TECHNICAL BREAKDOWN", "lbl": ["Height", "Reach", "Strikes/min", "Accuracy", "Takedowns/15m", "Takedown Def"], "cta": "BET ON", "err": "Please select two different fighters." }
}
txt = T[st.session_state.lang]

# --- 3. ROSTER ---
ROSTER = ["--- SELECT ---", "Alex Pereira", "Alexander Volkanovski", "Alexander Volkov", "Alexa Grasso", "Aljamain Sterling", "Amanda Nunes", "Amir Albazi", "Anderson Silva", "Anthony Smith", "Arman Tsarukyan", "Arnold Allen", "Belal Muhammad", "Beneil Dariush", "Benoit Saint Denis", "Bobby Green", "Bo Nickal", "Brandon Moreno", "Brandon Royval", "Brendan Allen", "Brian Ortega", "Brock Lesnar", "Caio Borralho", "Calvin Kattar", "Charles Oliveira", "Chris Weidman", "Ciryl Gane", "Colby Covington", "Conor McGregor", "Cory Sandhagen", "Curtis Blaydes", "Dan Hooker", "Daniel Cormier", "Deiveson Figueiredo", "Derrick Lewis", "Diego Lopes", "Dominick Cruz", "Dominick Reyes", "Dricus Du Plessis", "Dustin Poirier", "Edson Barboza", "Erin Blanchfield", "Francis Ngannou", "Georges St-Pierre", "Gilbert Burns", "Henry Cejudo", "Holly Holm", "Ian Machado Garry", "Ilia Topuria", "Islam Makhachev", "Israel Adesanya", "Jack Della Maddalena", "Jailton Almeida", "Jamahal Hill", "Jan Blachowicz", "Jared Cannonier", "Jessica Andrade", "Jiri Prochazka", "Jon Jones", "Jose Aldo", "Justin Gaethje", "Kamaru Usman", "Kayla Harrison", "Kevin Holland", "Khabib Nurmagomedov", "Khalil Rountree Jr.", "Khamzat Chimaev", "Leon Edwards", "Lerone Murphy", "Mackenzie Dern", "Magomed Ankalaev", "Manon Fiorot", "Marlon Vera", "Marvin Vettori", "Mateusz Gamrot", "Max Holloway", "Merab Dvalishvili", "Michael Chandler", "Michael Morales", "Michel Pereira", "Movsar Evloev", "Muhammad Mokaev", "Nassourdine Imavov", "Nate Diaz", "Nick Diaz", "Paddy Pimblett", "Paulo Costa", "Petr Yan", "Rafael Fiziev", "Raquel Pennington", "Renato Moicano", "Rob Font", "Robert Whittaker", "Roman Dolidze", "Rose Namajunas", "Ronda Rousey", "Sean O'Malley", "Sean Strickland", "Sergei Pavlovich", "Shavkat Rakhmonov", "Song Yadong", "Stephen Thompson", "Steve Erceg", "Stipe Miocic", "Tai Tuivasa", "Tatiana Suarez", "Tom Aspinall", "Tony Ferguson", "Umar Nurmagomedov", "Valentina Shevchenko", "Vicente Luque", "Virna Jandiroba", "Volkan Oezdemir", "Weili Zhang", "Yair Rodriguez", "Yan Xiaonan"]

# --- 4. MOTEUR DATA (ROBUSTE) ---
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
    "Conor McGregor": {"Taille": "5' 9\"", "Allonge": "74\"", "Coups": 5.32, "TD": 0.67, "DefLutte": 66, "Preci": 49},
    "Khamzat Chimaev": {"Taille": "6' 2\"", "Allonge": "75\"", "Coups": 5.72, "TD": 4.00, "DefLutte": 100, "Preci": 59}
}

def clean_num(val):
    if isinstance(val, (int, float)): return val
    try: return float(str(val).replace('%','').replace(' cm','').strip())
    except: return 0

def to_cm(imp):
    if not imp or imp=="N/A": return "-"
    try:
        p = imp.replace('"','').split("'")
        return f"{int((int(p[0])*30.48)+(int(p[1] if len(p)>1 else 0)*2.54))} cm"
    except: return imp

@st.cache_data
def get_raw_data(name):
    # Initialisation explicite pour éviter UnboundLocalError
    d = None
    
    # 1. Backup
    if name in BACKUP:
        d = BACKUP[name].copy()
        d['Nom'] = name
        return d
    
    # 2. Scraping
    try:
        h = {'User-Agent': 'Mozilla/5.0'}
        url = f"http://ufcstats.com/statistics/fighters/search?query={name.replace(' ', '+')}"
        r = requests.get(url, headers=h, timeout=4)
        s = BeautifulSoup(r.content, 'html.parser')
        
        t = None
        rs = s.find_all('tr', class_='b-statistics__table-row')
        
        # Recherche lien
        if len(rs) > 1:
            for row in rs[1:6]:
                l = row.find('a', href=True)
                if l and name.lower() in l.text.strip().lower():
                    t = l['href']; break
            if not t: t = rs[1].find('a', href=True)['href']
            
        if t:
            r2 = requests.get(t, headers=h, timeout=4)
            s2 = BeautifulSoup(r2.content, 'html.parser')
            stats = {'Nom': name, 'Taille': 'N/A', 'Allonge': 'N/A', 'Coups': 0.0, 'TD': 0.0, 'DefLutte': 0, 'Preci': 0}
            
            for i in s2.find_all('li', class_='b-list__box-list-item'):
                tx = i.text.strip()
                if "Height:" in tx: stats['Taille'] = tx.split(':')[1].strip()
                if "Reach:" in tx: stats['Allonge'] = tx.split(':')[1].strip()
                if "SLpM:" in tx: stats['Coups'] = float(tx.split(':')[1])
                if "TD Avg.:" in tx: stats['TD'] = float(tx.split(':')[1])
                if "TD Def.:" in tx: stats['DefLutte'] = int(tx.split(':')[1].replace('%', ''))
                if "Str. Acc.:" in tx: stats['Preci'] = int(tx.split(':')[1].replace('%', ''))
            d = stats
    except:
        pass
        
    return d

def process_data_units(d, lang):
    """Gère la conversion d'unités APRES le cache"""
    if not d: return None
    new_d = d.copy()
    if lang == 'fr':
        new_d['Taille'] = to_cm(new_d['Taille'])
        try: new_d['Allonge'] = f"{int(float(new_d['Allonge'].replace('\"',''))*2.54)} cm"
        except: pass
    return new_d

def calc(f1,f2):
    s=50+(f1['Coups']-f2['Coups'])*5
    if f1['TD']>2 and f2['DefLutte']<60: s+=12
    if f2['TD']>2 and f1['DefLutte']<60: s-=12
    s=max(10,min(90,s))
    v=(f1['Coups']+f2['Coups'])+(f1['TD']+f2['TD'])*1.5
    f=min(92,25+v*4.5)
    sr=(f1['Coups']+f2['Coups'])/max(1,v)
    k=int(f*sr); sb=int(f*(1-sr)); d=100-k-sb
    return int(s),k,sb,d

# --- 5. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    .stApp { background-color: #0f172a; background-image: radial-gradient(at 50% 0%, rgba(46, 204, 113, 0.1) 0px, transparent 60%); font-family: 'Montserrat', sans-serif; }
    h1,h2,div,p{font-family:'Montserrat',sans-serif!important;}
    .main-title { font-weight: 900; font-size: 2rem; color: white; letter-spacing: -1px; margin:0; }
    .glass-card { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); border-radius: 20px; padding: 24px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 10px 30px -5px rgba(0,0,0,0.4); margin-bottom: 20px; }
    div.stButton>button { background: #2ecc71!important; color: #020617!important; border-radius: 12px; padding: 18px; font-weight: 900; text-transform: uppercase; border: none; width: 100%; }
    .bar-bg { width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; display: flex; margin-top: 5px; }
    .bar-l { height: 100%; background: #38bdf8; } .bar-r { height: 100%; background: #f43f5e; }
    .finish-cont { width: 100%; height: 14px; background: #1e293b; border-radius: 7px; overflow: hidden; display: flex; margin-top: 10px; }
    .flag-btn { background: transparent; border: 1px solid rgba(255,255,255,0.2); color:white; border-radius: 8px; padding: 5px 10px; cursor: pointer; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# --- 6. UI ---
c_t, c_l = st.columns([5,1])
with c_t: 
    st.markdown(f"<div class='main-title'>CAGEMETRICS <span style='color:#2ecc71'>PRO</span></div>", unsafe_allow_html=True)
    st.caption(txt['sub'])
with c_l: 
    # Drapeaux Emojis
    if st.button("🇫🇷" if st.session_state.lang == 'en' else "🇺🇸"): 
        toggle()
        st.rerun()

st.markdown(f'<div class="glass-card"><div style="font-size:0.75rem; color:#94a3b8; font-weight:700; margin-bottom:15px; letter-spacing:1px;">{txt["sel"]}</div>', unsafe_allow_html=True)
c1,c2,c3=st.columns([1,0.1,1])
ia=ROSTER.index("Jon Jones") if "Jon Jones" in ROSTER else 0
ib=ROSTER.index("Tom Aspinall") if "Tom Aspinall" in ROSTER else 0
f_a=c1.selectbox("A",ROSTER,index=ia,label_visibility="collapsed")
c2.markdown("<div style='text-align:center; padding-top:10px; font-weight:900; color:white;'>VS</div>",unsafe_allow_html=True)
f_b=c3.selectbox("B",ROSTER,index=ib,label_visibility="collapsed")
st.markdown('</div>',unsafe_allow_html=True)

if st.button(txt['btn']):
    if f_a=="--- SELECT ---" or f_a==f_b: st.warning(txt['err'])
    else:
        with st.spinner("..."):
            # 1. Récupération brute (Cache)
            raw_s1 = get_raw_data(f_a)
            raw_s2 = get_raw_data(f_b)
            
            # 2. Conversion Unités (Live)
            s1 = process_data_units(raw_s1, st.session_state.lang)
            s2 = process_data_units(raw_s2, st.session_state.lang)
            
            if s1 and s2:
                sc,k,sb,d=calc(s1,s2); w=s1['Nom'] if sc>=50 else s2['Nom']; cf=sc if sc>=50 else 100-sc
                st.markdown(f"""<div class="glass-card" style="text-align:center; border:2px solid #2ecc71; background:rgba(46, 204, 113, 0.05);"><div style="color:#94a3b8; font-size:0.7rem; font-weight:700; letter-spacing:1px; margin-bottom:5px;">{txt['win']}</div><div style="font-size:2.2rem; font-weight:900; color:white; line-height:1; margin-bottom:10px;">{w}</div><span style="background:#2ecc71; color:#020617; padding:4px 12px; border-radius:20px; font-weight:800; font-size:0.8rem;">{cf}% {txt['conf']}</span></div>""",unsafe_allow_html=True)
                st.markdown(f"""<div class="glass-card"><div style="text-align:center; font-weight:800; color:white;">{txt['meth']}</div><div class="finish-cont"><div style="width:{k}%; background:#ef4444;"></div><div style="width:{sb}%; background:#eab308;"></div><div style="width:{d}%; background:#3b82f6;"></div></div><div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.7rem; font-weight:700;"><span style="color:#ef4444">KO/TKO {k}%</span><span style="color:#eab308">SUB {sb}%</span><span style="color:#3b82f6">DEC {d}%</span></div></div>""",unsafe_allow_html=True)
                
                st.markdown(f'<div class="glass-card"><div style="text-align:center; color:#94a3b8; font-weight:700; margin-bottom:15px;">{txt["tech"]}</div>',unsafe_allow_html=True)
                def stat_vis(l,v1,v2):
                    n1=clean_num(v1); n2=clean_num(v2); tot=max(n1+n2,0.1); p1=(n1/tot)*100; p2=(n2/tot)*100
                    st.markdown(f"""<div style="margin-bottom:12px;"><div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.9rem;"><span style="color:#38bdf8">{v1}</span><span style="color:#f43f5e">{v2}</span></div><div class="bar-bg"><div class="bar-l" style="width:{p1}%"></div><div class="bar-r" style="width:{p2}%"></div></div><div style="text-align:center; font-size:0.7rem; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-top:2px;">{l}</div></div>""",unsafe_allow_html=True)
                l=txt['lbl']
                stat_vis(l[0],s1['Taille'],s2['Taille']); stat_vis(l[1],s1['Allonge'],s2['Allonge']); stat_vis(l[2],s1['Coups'],s2['Coups'])
                stat_vis(l[3],f"{s1['Preci']}%",f"{s2['Preci']}%"); stat_vis(l[4],s1['TD'],s2['TD']); stat_vis(l[5],f"{s1['DefLutte']}%",f"{s2['DefLutte']}%")
                st.markdown('</div>',unsafe_allow_html=True)
                st.markdown(f"""<a href="https://www.unibet.fr/sport/mma" target="_blank" style="text-decoration:none;"><button style="width:100%; background:#fc4c02; color:white; border:none; padding:16px; border-radius:12px; font-weight:800; cursor:pointer;">{txt['cta']} {w}</button></a>""",unsafe_allow_html=True)
            else: st.error("Data error.")
