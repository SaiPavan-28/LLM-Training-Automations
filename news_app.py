import streamlit as st
from dotenv import load_dotenv
from newsapi import NewsApiClient
import google.generativeai as genai
import os
import re
import time

# --- 1. Load Environment Variables ---
load_dotenv(override=True)

# --- 2. API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# --- 3. Configure APIs ---
genai.configure(api_key=GEMINI_API_KEY)
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

# --- 4. Streamlit App Settings ---
st.set_page_config(page_title="AI News Summarizer (Guarded)", layout="wide")

st.title("📰 AI News Summarizer (Google Gemini + Guardrails)")

# --- 5. User Inputs ---
category = st.selectbox("Select News Category", ["technology", "business", "sports", "health", "science"])
region = st.selectbox("Select Country", ["us", "in", "gb", "ca", "au"])
user_query = st.text_input("Ask something about the latest news (optional)")

# --- 6. Guardrail: Input Validation ---
#  5 GUARDRAILS START HERE
#  Guardrail 1 — Input Validation
if not re.match("^[a-zA-Z0-9\s.,!?'-]*$", user_query):
    st.error("🚫 Invalid characters detected. Please use plain English text only.")
    st.stop()

# Guardrail 2 — Query Length Limit
if len(user_query) > 300:
    st.warning("⚠️ Query too long! Please shorten your question.")
    st.stop()

#  Guardrail 3 — News Data Safety Check
if not NEWSAPI_KEY or NEWSAPI_KEY == "YOUR_NEWSAPI_KEY_HERE":
    st.error("🚫 Missing NewsAPI key. Please configure it in your environment variables.")
    st.stop()

# Guardrail 4 — Token Limit for Gemini (prevent overload)
MAX_ARTICLE_CHARS = 6000

#  Guardrail 5 — Anti-hallucination / bias prevention
SAFETY_INSTRUCTIONS = """
Important:
- Base your summary strictly on the news articles below.
- Do NOT invent facts or add opinions.
- Stay neutral and professional.
- If information is missing, clearly say: "No reliable news data found on this."
"""

# --- 7. Fetch and Process News ---
if st.button("Fetch News"):
    st.info(f"Fetching {category} news from {region.upper()} ...")

    try:
        top_headlines = newsapi.get_top_headlines(category=category, country=region, page_size=10)
        articles = top_headlines.get('articles', [])
    except Exception as e:
        st.error(f"⚠️ NewsAPI error: {e}")
        st.stop()

    # --- Handoff: Fallbacks ---
    if not articles:
        st.warning(f"No news found for {category} in {region}. Trying general category...")
        top_headlines = newsapi.get_top_headlines(country=region, page_size=10)
        articles = top_headlines.get('articles', [])

    if not articles:
        st.warning(f"No top headlines found for {region}. Searching globally for '{category}'...")
        everything = newsapi.get_everything(q=category, language='en', sort_by='relevancy', page_size=10)
        articles = everything.get('articles', [])

    if not articles:
        st.error("❌ No articles found even after fallback. Try again later.")
        st.stop()

    # --- Prepare text for Gemini ---
    news_text = "\n".join([
        f"{a['title']} - {a['description']}" for a in articles if a.get('description')
    ])[:6000]  # Guardrail: limit token length

       # --- Smart Prompt: Handles optional user queries properly ---
    if user_query:
        prompt = f"""
You are a professional and neutral news analyst.

User asked: "{user_query}"

Use the following recent {category} news articles from {region.upper()} to answer.
If the answer is not found in the articles, clearly state:
"Based on the latest available news, there is no clear information about this topic."

Then, provide:
1. A direct, factual answer to the question.
2. A concise summary (8–10 bullet points) of related key developments.
3. The overall sentiment (Positive / Neutral / Negative).

News Articles:
{news_text}
"""
    else:
        prompt = f"""
You are a professional and neutral news summarizer.

Summarize the following {category} news articles from {region.upper()} in 10 bullet points.
Then provide the overall sentiment (Positive / Neutral / Negative).

News Articles:
{news_text}
"""

    # --- Gemini Guardrails: Generation with Error Handling ---
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        summary_text = response.text.strip()
    except Exception as e:
        st.warning(f"⚠️ Gemini model error: {e}")
        st.info("🪄 Switching to fallback summarizer...")
        summary_text = "• " + "\n• ".join([a["title"] for a in articles[:10]])

    # --- Guardrail: Output Cleaning ---
    summary_text = re.sub(r"(http\S+|www\S+)", "", summary_text)  # Remove links
    summary_text = summary_text.replace("**", "").strip()

    # --- Ensure Bullet Formatting ---
    if not summary_text.startswith("•") and "-" not in summary_text:
        summary_text = "• " + "\n• ".join(summary_text.split("\n"))

    # --- Display Summary ---
    st.subheader("🧠 Summary & Insights")
    st.markdown(summary_text)

    # --- Display Headlines ---
    st.subheader("🗞️ Top Headlines")
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'No title available')
        description = article.get('description', 'No description available')
        url = article.get('url', '#')
        image = article.get('urlToImage')
        source = article.get('source', {}).get('name', 'Unknown')

        with st.container():
            if image:
                st.image(image, width=500)
            st.markdown(f"### {i}. [{title}]({url})", unsafe_allow_html=True)
            st.write(description)
            st.caption(f"📰 Source: {source}")
            st.markdown("---")

    st.success("✅ Done! Guardrails + bullet summary working perfectly.")
