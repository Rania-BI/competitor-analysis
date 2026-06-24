import time
import pandas as pd
import streamlit as st
from google_play_scraper import search, reviews, Sort
from transformers import pipeline

@st.cache_data(show_spinner=False)
def search_apps(query,n_results=30,country="us",lang="en"):
    raw=search(query,n_hits=n_results,country=country,lang=lang)

    if not raw:
        return pd.DataFrame()

    records=[]
    for app in raw:
        records.append({
            "appId":       app.get("appId",""),
            "title":       app.get("title","N/A"),
            "developer":   app.get("developer","N/A"),
            "score":       round(app.get("score") or 0, 2),
            "ratings":     app.get("ratings") or 0,
            "installs":    app.get("installs","N/A"),
            "free":        app.get("free",True),
            "price":       app.get("price",0.0),
            "genre":       app.get("genre","N/A"),
            "description": (app.get("description") or"")[:300],
            "icon":        app.get("icon",""),
            "url":         app.get("url",""),
        })

    df=pd.DataFrame(records)
    df=df[df["appId"] != ""].reset_index(drop=True)
    return df

@st.cache_data(show_spinner=False)
def get_reviews(app_id,n_reviews=50,country="us",lang="en"):


    result, _=reviews(
        app_id,
        lang=lang,
        country=country,
        sort=Sort.MOST_RELEVANT,
        count=n_reviews,
    )

    texts=[r["content"] for r in result if r.get("content","").strip()]
    return texts

@st.cache_resource(show_spinner=False)
def load_sentiment_model():
    model_name="cardiffnlp/twitter-roberta-base-sentiment-latest"
    pipe=pipeline(
        "sentiment-analysis",
        model=model_name,
        tokenizer=model_name,
        truncation=True,
        max_length=512,
    )
    return pipe
def analyze_sentiments(texts):
    if not texts:
        return pd.DataFrame(columns=["text","label","score"])

    pipe=load_sentiment_model()
    results=[]

    for text in texts:
        try:
            pred=pipe(text[:512])[0]
            results.append({
                "text":  text[:200],
                "label": pred["label"].capitalize(),
                "score": round(pred["score"], 3),
            })
        except Exception:
            continue
        time.sleep(0.01)
    return pd.DataFrame(results)
def compute_sentiment_score(sentiment_df):
    if sentiment_df.empty:
        return {"positive":0,"neutral":0,"negative":0,"overall_score":0}

    counts=sentiment_df["label"].value_counts()
    total=len(sentiment_df)

    pos=counts.get("Positive",0)/total*100
    neu=counts.get("Neutral",0)/total*100
    neg=counts.get("Negative",0)/total*100

    return {
        "positive":round(pos,1),
        "neutral":round(neu,1),
        "negative":round(neg,1),
        "overall_score":round(pos-neg,1),
    }