import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

from scraper_appartements import scraper_appartements, clean_data
from scraper_terrains import scraper_terrains, clean_data
from scraper_villas import scraper_villas, clean_data

# Configuration
st.set_page_config(page_title="Scraper Immobilier", layout="wide")
st.title("🏡 Application de Web Scraping Immobilier")
st.markdown("""
Cette application vous permet d’accéder facilement aux données immobilières issues de CoinAfrique.

### Fonctions principales :
* 🏗️ **Scraping en direct** : récupérez en temps réel les annonces d’appartements, villas ou terrains.
* 💾 **Téléchargement de données** : consultez et téléchargez des jeux de données préenregistrés.
* 📝 **Évaluation de l'application** : donnez votre avis et contribuez à l'amélioration de l’outil.

* **Technologies utilisées :** Python, pandas, streamlit, BeautifulSoup
* **Source des données :** [CoinAfrique Sénégal](https://sn.coinafrique.com/)
""")


# Créer les trois onglets
onglet1, onglet2, onglet3 = st.tabs([
    "🔍 Scraper des données",
    "📂 Jeux de données existants",
    "📝 Évaluation de l'application"
])

# === ONGLET 1 : Scraping ===
with onglet1:
    choix = st.selectbox("Quel type de bien veux-tu scraper ?", ["Appartements", "Terrains", "Villas"])
    nb_pages = st.number_input("Nombre de pages à scraper", min_value=1, max_value=50, step=1, value=1)

    if st.button("🚀 Lancer le scraping"):
        st.info(f"Lancement du scraping pour {choix.lower()} sur {nb_pages} page(s)...")
        try:
            if choix == "Appartements":
                df = scraper_appartements(nb_pages)
            elif choix == "Terrains":
                df = scraper_terrains(nb_pages)
            elif choix == "Villas":
                df = scraper_villas(nb_pages)

            st.success("✅ Scraping terminé")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger en CSV", data=csv, file_name=f"{choix.lower()}_data.csv", mime="text/csv")
        except Exception as e:
            st.error(f"❌ Une erreur est survenue : {e}")

# === ONGLET 2 : Données existantes ===
with onglet2:
    st.subheader("📊 Visualiser et télécharger les jeux de données existants")

    st.markdown("""
        <style>
        div.stButton {text-align:center}
        .stButton>button {
            font-size: 14px;
            height: 3em;
            width: 25em;
            background-color: #f0f2f6;
            color: #333;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    def load_(dataframe, title, key, filename):
        if st.button(title, key=key):
            st.subheader(f'📂 {title}')
            st.write(f'Dimensions : {dataframe.shape[0]} lignes × {dataframe.shape[1]} colonnes')
            st.dataframe(dataframe)

            csv = dataframe.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger ce fichier CSV", data=csv, file_name=filename, mime="text/csv")

    try:
        df_appart = pd.read_csv("data/appartements_coinafrique_WSc.csv")
        df_terrains = pd.read_csv("data/terrains_coinafrique_WSc.csv")
        df_villas = pd.read_csv("data/Villas_coinafrique_WSc.csv")

        load_(df_appart, "Voir les données Appartements", "btn_app", "appartements.csv")
        load_(df_terrains, "Voir les données Terrains", "btn_terr", "terrains.csv")
        load_(df_villas, "Voir les données Villas", "btn_vill", "villas.csv")

    except FileNotFoundError as e:
        st.error(f"❌ Fichier manquant : {e.filename}")
    except Exception as e:
        st.error(f"❌ Erreur inattendue : {e}")

# === ONGLET 3 : Évaluation via Kobotoolbox ===
with onglet3:
    st.subheader("📝 Merci de remplir ce formulaire pour évaluer l'application")

    # Utilisation du lien KoboToolbox extrait de l'iframe
    formulaire_url = "https://ee.kobotoolbox.org/x/VmBcI71C"

    # Intégration du formulaire avec une iframe Streamlit
    components.iframe(formulaire_url, height=700, scrolling=True)
    
# === Fin de l'application Streamlit ===
