import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Visualizations",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Visualizations")
st.markdown("---")

if "df_results" not in st.session_state or st.session_state["df_results"].empty:
    st.warning("⚠️ Lancez d'abord une recherche sur la page Search & Results.")
    st.stop()

df=st.session_state["df_results"].copy()
query=st.session_state.get("query","")

st.markdown(f"### Analyse de **{len(df)}** applications — *{query}*")
st.markdown("---")

with st.sidebar:
    st.header("🎛️ Filtres")

    app_options=["Toutes"]+df["appId"].tolist()
    selected_app=st.selectbox("Filtrer par Application ID",app_options)

    min_score=st.slider("Note minimale ⭐",0.0,5.0,0.0,0.5)

    price_filter=st.radio(
        "Type",
        options=["Toutes","Gratuites","Payantes"],
    )

if selected_app!="Toutes":
    df=df[df["appId"]==selected_app]
else:
    df=df[df["score"]>=min_score]
    if price_filter=="Gratuites":
        df=df[df["free"]==True]
    elif price_filter=="Payantes":
        df=df[df["free"]==False]

if df.empty:
    st.warning("Aucune application ne correspond aux filtres.")
    st.stop()

st.markdown("#### 🏆 Top Applications & Distribution des Notes")
col1,col2=st.columns(2)

with col1:
    top_rated=df.nlargest(10,"score")[["title","score"]]

    fig_top=px.bar(
        top_rated,
        x="score",
        y="title",
        orientation="h", 
        color="score",
        color_continuous_scale="Blues",
        title="🥇 Top 10 Apps par Note",
        labels={"score":"Note ⭐","title":"Application"},
    )
    fig_top.update_layout(
        yaxis={"categoryorder":"total ascending"},
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig_top,use_container_width=True)

with col2:
    fig_hist=px.histogram(
        df,
        x="score",
        nbins=10,
        color_discrete_sequence=["#636EFA"],
        title="📊 Distribution des Notes",
        labels={"score": "Note ⭐"},
    )
    fig_hist.update_layout(height=400,bargap=0.1)
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")
st.markdown("#### 📦 Installations & Modèle Économique")
col3,col4=st.columns(2)

with col3:
    df_inst=df.copy()
    df_inst["installs_num"]=(
        df_inst["installs"]
        .astype(str)
        .str.replace(r"[^0-9]","",regex=True)
        .replace("","0")
        .astype(float)
    )
    top_inst=df_inst.nlargest(10,"installs_num")[
        ["title","installs_num","installs"]
    ]
    fig_inst=px.bar(
        top_inst,
        x="installs_num",
        y="title",
        orientation="h",
        color="installs_num",
        color_continuous_scale="Greens",
        title="📥 Top 10 Apps par Installations",
        labels={"installs_num":"Installations","title":"Application"},
        hover_data={"installs":True,"installs_num":False},
    )
    fig_inst.update_layout(
        yaxis={"categoryorder":"total ascending"},
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig_inst,use_container_width=True)

with col4:
    free_counts=df["free"].value_counts().reset_index()
    free_counts.columns=["Type","Nombre"]
    free_counts["Type"]=free_counts["Type"].map(
        {True:"Gratuite ✅",False: "Payante 💰"}
    )

    fig_pie=px.pie(
        free_counts,
        names="Type",
        values="Nombre",
        title="💰 Gratuit vs Payant",
        color_discrete_sequence=["#00CC96","#EF553B"],
        hole=0.4,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.markdown("#### 🗂️ Genres & Variabilité des Notes")
col5,col6=st.columns(2)

with col5:
    genre_counts=df["genre"].value_counts().reset_index()
    genre_counts.columns=["Genre","Nombre"]

    fig_genre=px.bar(
        genre_counts,
        x="Nombre",
        y="Genre",
        orientation="h",
        color="Nombre",
        color_continuous_scale="Purples",
        title="🗂️ Distribution des Genres",
    )
    fig_genre.update_layout(
        yaxis={"categoryorder":"total ascending"},
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig_genre,use_container_width=True)

with col6:
    genre_counts_raw=df["genre"].value_counts()
    valid_genres=genre_counts_raw[genre_counts_raw>=2].index.tolist()
    df_box=df[df["genre"].isin(valid_genres)]

    if not df_box.empty:
        fig_box=px.box(
            df_box,
            x="genre",
            y="score",
            color="genre",
            title="📉 Variabilité des Notes par Genre",
            labels={"score": "Note ⭐", "genre": "Genre"},
        )
        fig_box.update_layout(
            showlegend=False,
            height=400,
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig_box,use_container_width=True)
    else:
        st.info("Pas assez de données par genre pour le Box Plot.")

st.markdown("---")

st.markdown("#### ☁️ Word Cloud des Descriptions")

all_text=" ".join(df["description"].dropna().tolist())

if all_text.strip():
    wc=WordCloud(
        width=1200,
        height=400,
        background_color="white",
        colormap="Blues",
        max_words=100,
        collocations=False,
        stopwords={
            "the", "and", "to", "of", "a", "in", "is", "for",
            "with", "your", "you", "this", "that", "are", "on",
            "it", "be", "by", "an", "or", "can", "will", "all",
            "have", "has", "from", "more", "its", "get", "use",
        },
    ).generate(all_text)
    fig_wc,ax=plt.subplots(figsize=(14,4))
    ax.imshow(wc,interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig_wc)
else:
    st.info("Pas de descriptions disponibles pour le Word Cloud.")
st.markdown("---")
with st.expander("📋 Voir le tableau des données filtrées"):
    st.dataframe(
        df[["title","developer","score","ratings","installs","free","genre"]],
        use_container_width=True,
        hide_index=True,
    )