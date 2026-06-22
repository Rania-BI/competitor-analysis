import streamlit as st
from utils import search_apps

# ── Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Search & Results",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Search & Results")
st.markdown("Recherchez des applications sur le **Google Play Store**.")
st.markdown("---")

# ── Formulaire de recherche ───────────────────────────────────────────
# st.form() groupe les widgets ensemble.
# La recherche ne se lance QUE quand on clique sur le bouton submit.
# Sans form(), chaque interaction rechargerait toute la page.

with st.form(key="search_form"):
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        query = st.text_input(
            "🔎 Mot-clé de recherche",
            placeholder="ex : note taking ai, fitness tracker...",
        )
    with col2:
        n_results = st.slider(
            "Nombre de résultats",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
        )
    with col3:
        country = st.selectbox(
            "Pays",
            options=["us", "fr", "gb", "de", "ma"],
            index=0,
        )

    # Bouton de soumission du formulaire
    submitted = st.form_submit_button(
        "🚀 Lancer la recherche",
        use_container_width=True,
    )

# ── Logique de recherche ──────────────────────────────────────────────
# Ce bloc s'exécute uniquement quand l'utilisateur clique sur le bouton

if submitted:
    if not query.strip():
        # strip() enlève les espaces vides
        st.warning("⚠️ Veuillez saisir un mot-clé.")
    else:
        # st.spinner() affiche un message pendant le chargement
        with st.spinner(f"Recherche de '{query}' en cours..."):
            df = search_apps(
                query=query.strip(),
                n_results=n_results,
                country=country,
            )

        if df.empty:
            st.error("Aucun résultat trouvé. Essayez un autre mot-clé.")
        else:
            # ── Session State ─────────────────────────────────────────
            # On sauvegarde les résultats pour les autres pages.
            # st.session_state fonctionne comme un dictionnaire global
            # qui persiste tant que la session est ouverte.
            st.session_state["df_results"] = df
            st.session_state["query"] = query

            st.success(f"✅ {len(df)} applications trouvées pour '{query}'")

# ── Affichage des résultats ───────────────────────────────────────────
# Ce bloc s'affiche si des données existent dans le session_state

if "df_results" in st.session_state and not st.session_state["df_results"].empty:
    df = st.session_state["df_results"]

    # ── Métriques rapides ─────────────────────────────────────────────
    # 4 cartes de statistiques en haut
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Applications trouvées", len(df))
    m2.metric("Note moyenne", f"{df['score'].mean():.2f} ⭐")
    m3.metric("Apps gratuites", f"{df['free'].sum() / len(df) * 100:.0f}%")
    m4.metric("Genres distincts", df["genre"].nunique())

    st.markdown("---")

    # ── Sidebar : filtres ─────────────────────────────────────────────
    with st.sidebar:
        st.header("🎛️ Filtres")

        min_score = st.slider(
            "Note minimale ⭐",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5,
        )

        price_filter = st.radio(
            "Type d'application",
            options=["Toutes", "Gratuites", "Payantes"],
        )

        genres = ["Tous"] + sorted(df["genre"].dropna().unique().tolist())
        selected_genre = st.selectbox("Genre", genres)

    # Application des filtres sur le DataFrame
    filtered_df = df[df["score"] >= min_score].copy()

    if price_filter == "Gratuites":
        filtered_df = filtered_df[filtered_df["free"] == True]
    elif price_filter == "Payantes":
        filtered_df = filtered_df[filtered_df["free"] == False]

    if selected_genre != "Tous":
        filtered_df = filtered_df[filtered_df["genre"] == selected_genre]

    st.markdown(f"*{len(filtered_df)} application(s) affichée(s)*")

    # ── Tableau interactif ────────────────────────────────────────────
    # column_config permet de personnaliser l'affichage de chaque colonne
    st.dataframe(
        filtered_df[[
            "icon", "title", "developer", "score",
            "ratings", "installs", "free", "price", "genre", "url"
        ]],
        column_config={
            "icon":      st.column_config.ImageColumn("Icône", width="small"),
            "title":     st.column_config.TextColumn("Application"),
            "developer": st.column_config.TextColumn("Développeur"),
            "score":     st.column_config.NumberColumn("Note ⭐", format="%.2f"),
            "ratings":   st.column_config.NumberColumn("Nb avis", format="%d"),
            "installs":  st.column_config.TextColumn("Installations"),
            "free":      st.column_config.CheckboxColumn("Gratuite"),
            "price":     st.column_config.NumberColumn("Prix ($)", format="%.2f"),
            "genre":     st.column_config.TextColumn("Genre"),
            "url":       st.column_config.LinkColumn("Play Store"),
        },
        use_container_width=True,
        hide_index=True,
        height=500,
    )

    # ── Bouton d'export CSV ───────────────────────────────────────────
    csv = filtered_df.drop(columns=["icon"], errors="ignore").to_csv(index=False)
    st.download_button(
        label="⬇️ Télécharger les résultats (CSV)",
        data=csv,
        file_name=f"results_{query.replace(' ', '_')}.csv",
        mime="text/csv",
    )

else:
    # Message affiché si aucune recherche n'a encore été faite
    st.info("👆 Lancez une recherche pour afficher les résultats.")