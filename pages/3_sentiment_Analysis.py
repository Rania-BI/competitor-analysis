import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import get_reviews, analyze_sentiments, compute_sentiment_score

# ── Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sentiment Analysis",
    page_icon="💬",
    layout="wide",
)

st.title("💬 Sentiment Analysis")
st.markdown(
    "Analyse du sentiment des avis utilisateurs via le modèle "
    "**cardiffnlp/twitter-roberta-base-sentiment-latest** de HuggingFace."
)
st.markdown("---")

# ── Vérification des données ──────────────────────────────────────────
if "df_results" not in st.session_state or st.session_state["df_results"].empty:
    st.warning("⚠️ Lancez d'abord une recherche sur la page Search & Results.")
    st.stop()

df = st.session_state["df_results"].copy()
query = st.session_state.get("query", "")

st.markdown(f"Résultats pour : *{query}* — **{len(df)} applications disponibles**")

# ── Sidebar : sélection de l'app ─────────────────────────────────────
with st.sidebar:
    st.header("🎛️ Sélection")

    # Dictionnaire title → appId pour retrouver l'id depuis le titre
    app_titles  = df["title"].tolist()
    app_ids     = df["appId"].tolist()
    title_to_id = dict(zip(app_titles, app_ids))

    selected_title = st.selectbox(
        "Application à analyser",
        options=app_titles,
    )

    n_reviews = st.slider(
        "Nombre d'avis à analyser",
        min_value=10,
        max_value=100,
        value=30,
        step=10,
    )

    run_btn = st.button("🚀 Analyser", use_container_width=True)

# ════════════════════════════════════════════════
# ANALYSE INDIVIDUELLE
# ════════════════════════════════════════════════
st.markdown("### 🔬 Analyse individuelle")

if run_btn and selected_title:
    app_id = title_to_id[selected_title]

    # Chargement du modèle (mis en cache, ne se charge qu'une fois)
    with st.spinner("⏳ Chargement du modèle HuggingFace..."):
        from utils import load_sentiment_model
        load_sentiment_model()

    # Récupération des avis
    with st.spinner(f"📥 Récupération des avis pour {selected_title}..."):
        texts = get_reviews(app_id, n_reviews=n_reviews)

    if not texts:
        st.error("Aucun avis trouvé pour cette application.")
    else:
        # Analyse des sentiments
        with st.spinner("🤖 Analyse des sentiments en cours..."):
            sentiment_df = analyze_sentiments(texts)
            scores = compute_sentiment_score(sentiment_df)

        # Sauvegarde dans session_state pour ne pas recalculer
        st.session_state[f"sentiment_{app_id}"] = {
            "df":     sentiment_df,
            "scores": scores,
            "title":  selected_title,
        }

# ── Affichage si les données sont disponibles ─────────────────────────
app_id_sel = title_to_id.get(selected_title, "")
cache_key  = f"sentiment_{app_id_sel}"

if cache_key in st.session_state:
    cached       = st.session_state[cache_key]
    sentiment_df = cached["df"]
    scores       = cached["scores"]
    app_title    = cached["title"]

    st.markdown(f"#### 📱 {app_title}")
    st.markdown("---")

    # ── 4 métriques principales ───────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("😊 Positif",  f"{scores['positive']:.1f}%")
    m2.metric("😐 Neutre",   f"{scores['neutral']:.1f}%")
    m3.metric("😞 Négatif",  f"{scores['negative']:.1f}%")
    m4.metric("🎯 Score global", f"{scores['overall_score']:+.1f}")

    st.markdown("---")

    # ── Donut chart + Histogramme de confiance ────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        # Donut chart : répartition des 3 sentiments
        fig_donut = go.Figure(go.Pie(
            labels=["Positif 😊", "Neutre 😐", "Négatif 😞"],
            values=[
                scores["positive"],
                scores["neutral"],
                scores["negative"],
            ],
            hole=0.5,   # trou au centre = donut
            marker=dict(colors=["#00CC96", "#FFA15A", "#EF553B"]),
            textinfo="percent+label",
        ))
        fig_donut.update_layout(
            title="Répartition des Sentiments",
            height=350,
            showlegend=False,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        # Histogramme : distribution des scores de confiance
        # Le score de confiance = à quel point le modèle est sûr de lui
        fig_conf = px.histogram(
            sentiment_df,
            x="score",
            color="label",
            nbins=20,
            title="Distribution des Scores de Confiance",
            labels={"score": "Confiance du modèle", "count": "Nb avis"},
            color_discrete_map={
                "Positive": "#00CC96",
                "Neutral":  "#FFA15A",
                "Negative": "#EF553B",
            },
            barmode="overlay",
        )
        fig_conf.update_layout(height=350)
        st.plotly_chart(fig_conf, use_container_width=True)

    st.markdown("---")

    # ── Tableau des avis analysés ─────────────────────────────────────
    st.markdown("#### 📝 Détail des Avis")

    # Ajout d'une colonne emoji pour la lisibilité
    emoji_map = {"Positive": "😊", "Neutral": "😐", "Negative": "😞"}
    sentiment_df["Sentiment"] = (
        sentiment_df["label"].map(emoji_map) + " " + sentiment_df["label"]
    )

    # Filtre par type de sentiment
    filter_label = st.multiselect(
        "Filtrer par sentiment",
        options=["Positive", "Neutral", "Negative"],
        default=["Positive", "Neutral", "Negative"],
    )

    display_df = sentiment_df[sentiment_df["label"].isin(filter_label)][
        ["text", "Sentiment", "score"]
    ].rename(columns={
        "text":  "Extrait de l'avis",
        "score": "Confiance",
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=300,
        column_config={
            "Confiance": st.column_config.ProgressColumn(
                "Confiance",
                min_value=0,
                max_value=1,
                format="%.2f",
            )
        },
    )

else:
    st.info("👈 Sélectionnez une application dans la sidebar et cliquez sur Analyser.")

st.markdown("---")

# ════════════════════════════════════════════════
# COMPARAISON GLOBALE DE TOUTES LES APPS
# ════════════════════════════════════════════════
st.markdown("### 📊 Comparaison — Toutes les Applications")

with st.expander("🔄 Analyser toutes les applications"):
    st.info(
        "Lance l'analyse sur toutes les apps de la liste. "
        "Peut prendre quelques minutes selon le nombre d'apps."
    )

    run_all = st.button("▶️ Lancer l'analyse globale", use_container_width=True)

    if run_all:
        comparison_data = []
        # Barre de progression
        progress_bar = st.progress(0)
        status_text  = st.empty()

        for i, (title, app_id) in enumerate(title_to_id.items()):
            status_text.text(f"Analyse : {title} ({i+1}/{len(df)})")
            cache_k = f"sentiment_{app_id}"

            # Si pas encore analysée, on la traite
            if cache_k not in st.session_state:
                texts = get_reviews(app_id, n_reviews=20)
                if texts:
                    sent_df = analyze_sentiments(texts)
                    sc = compute_sentiment_score(sent_df)
                    st.session_state[cache_k] = {
                        "df": sent_df, "scores": sc, "title": title
                    }

            if cache_k in st.session_state:
                sc = st.session_state[cache_k]["scores"]
                comparison_data.append({
                    "Application":   title,
                    "Score global":  sc["overall_score"],
                    "% Positif":     sc["positive"],
                    "% Neutre":      sc["neutral"],
                    "% Négatif":     sc["negative"],
                })

            # Mise à jour de la barre de progression
            progress_bar.progress((i + 1) / len(df))

        status_text.text("✅ Analyse terminée !")
        st.session_state["comparison_data"] = comparison_data

# ── Graphique de comparaison ──────────────────────────────────────────
if "comparison_data" in st.session_state and st.session_state["comparison_data"]:
    comp_df = pd.DataFrame(st.session_state["comparison_data"])
    comp_df = comp_df.sort_values("Score global", ascending=True)

    # Bar chart horizontal : score de sentiment de chaque app
    # Rouge = négatif, Vert = positif (colorscale RdYlGn)
    fig_comp = px.bar(
        comp_df,
        x="Score global",
        y="Application",
        orientation="h",
        color="Score global",
        color_continuous_scale="RdYlGn",
        title="🎯 Score de Sentiment Global par Application",
        labels={"Score global": "Score (Positif% - Négatif%)"},
    )
    # Ligne verticale à 0 pour séparer positif et négatif
    fig_comp.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.5)
    fig_comp.update_layout(
        height=max(300, len(comp_df) * 35),
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # Tableau récapitulatif
    st.dataframe(
        comp_df.sort_values("Score global", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score global": st.column_config.NumberColumn(format="%+.1f"),
            "% Positif": st.column_config.ProgressColumn(
                min_value=0, max_value=100, format="%.1f%%"
            ),
            "% Négatif": st.column_config.ProgressColumn(
                min_value=0, max_value=100, format="%.1f%%"
            ),
        },
    )