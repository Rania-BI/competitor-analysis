import streamlit as st

st.set_page_config(
    page_title="Competitor Analysis",
    page_icon="📊",
    layout="wide",                
    initial_sidebar_state="expanded",
)

st.title("📊 Competitor Analysis App")
st.markdown("---") 


col1,col2=st.columns(2)

with col1:
    st.header("🔍 Vue d'ensemble")
    st.markdown("""
        Cette application analyse la **concurrence sur le Google Play Store**.

        À partir d'un mot-clé, l'app :
        - Récupère les applications correspondantes
        - Affiche les résultats dans un tableau interactif
        - Génère des visualisations comparatives
        - Analyse les avis utilisateurs avec de l'IA
    """)

with col2:
    st.header("🚀 Fonctionnalités")
    st.markdown("""
        - 🔎 Recherche dynamique par mot-clé
        - 📋 Tableau filtrable et triable
        - 📈 Bar charts, pie charts, word cloud
        - 💬 Sentiment Analysis (HuggingFace)
        - 🎛️ Filtres interactifs dans la sidebar
    """)

st.markdown("---")
st.header("📖 Comment utiliser l'application")

with st.expander("1️⃣  Search & Results"):
    st.write("""
        Va sur la page Search & Results dans le menu à gauche.
        Tape un mot-clé (ex: note taking ai, fitness tracker).
        Clique sur Lancer la recherche.
    """)

with st.expander("2️⃣  Visualizations"):
    st.write("""
        Va sur la page Visualizations.
        Les graphiques se génèrent automatiquement
        à partir des résultats de ta recherche.
    """)

with st.expander("3️⃣  Sentiment Analysis"):
    st.write("""
        Va sur la page Sentiment Analysis.
        Sélectionne une application dans la sidebar.
        Clique sur Analyser pour voir le sentiment des avis.
    """)

st.markdown("---")

st.header("🛠️ Améliorations futures")

col3, col4=st.columns(2)

with col3:
    st.markdown("""
        - Ajouter des données depuis ProductHunt
        - Comparaison côte-à-côte de deux apps
        - Export des résultats en Excel
    """)

with col4:
    st.markdown("""
        - Analyse temporelle des ratings
        - Résumé automatique des avis négatifs
        - Alertes sur les nouvelles apps concurrentes
    """)

st.markdown("---")
st.caption("Data Applications Lab 2 — ENSIAS — Juin 2026")