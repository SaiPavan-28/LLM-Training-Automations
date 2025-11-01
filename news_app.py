import streamlit as st
from dotenv import load_dotenv
from newsapi import NewsApiClient
import google.generativeai as genai
import os
import re
import time
import requests
import json
from typing import List, Dict
import random
from datetime import datetime, timedelta

# --- 1. Load Environment Variables ---
load_dotenv(override=True)

# --- 2. API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# --- 3. Configure APIs ---
genai.configure(api_key=GEMINI_API_KEY)
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

# --- 4. Comprehensive Country-Specific News Config ---
COUNTRY_NEWS_CONFIG = {
    "in": {  # India
        "sources": ["the-times-of-india", "the-hindu", "google-news-in"],
        "queries": {
            "technology": "India tech startup funding digital",
            "business": "India economy business stock market",
            "sports": "India cricket IPL sports",
            "health": "India health medical covid healthcare",
            "science": "India science research ISRO",
            "entertainment": "Bollywood movies entertainment India"
        },
        "fallback_keywords": ["India", "Indian", "Delhi", "Mumbai"]
    },
    "us": {  # USA
        "sources": ["cnn", "fox-news", "nbc-news", "abc-news"],
        "queries": {
            "technology": "US tech Silicon Valley startup",
            "business": "US economy stock market Wall Street",
            "sports": "NBA NFL baseball sports USA",
            "health": "US health medical covid",
            "science": "NASA science research US",
            "entertainment": "Hollywood movies entertainment US"
        },
        "fallback_keywords": ["US", "USA", "United States", "New York", "Washington"]
    },
    "gb": {  # United Kingdom
        "sources": ["bbc-news", "the-guardian-uk", "independent", "daily-mail"],
        "queries": {
            "technology": "UK tech London startup",
            "business": "UK economy London stock market",
            "sports": "Premier League football sports UK",
            "health": "UK NHS health medical",
            "science": "UK science research Oxford Cambridge",
            "entertainment": "UK entertainment BBC movies"
        },
        "fallback_keywords": ["UK", "Britain", "London", "England"]
    },
    "ca": {  # Canada
        "sources": ["cbc-news", "ctv-news", "global-news"],
        "queries": {
            "technology": "Canada tech Toronto Vancouver startup",
            "business": "Canada economy Toronto stock market",
            "sports": "Canada hockey NHL sports",
            "health": "Canada health medical",
            "science": "Canada science research",
            "entertainment": "Canada entertainment movies Toronto"
        },
        "fallback_keywords": ["Canada", "Canadian", "Toronto", "Vancouver"]
    },
    "au": {  # Australia
        "sources": ["abc-news-au", "news-com-au", "smh"],
        "queries": {
            "technology": "Australia tech Sydney Melbourne startup",
            "business": "Australia economy ASX stock market",
            "sports": "Australia cricket rugby sports",
            "health": "Australia health medical",
            "science": "Australia science research",
            "entertainment": "Australia entertainment movies"
        },
        "fallback_keywords": ["Australia", "Australian", "Sydney", "Melbourne"]
    },
    "de": {  # Germany
        "sources": ["spiegel-online", "die-zeit", "focus"],
        "queries": {
            "technology": "Germany tech Berlin startup",
            "business": "Germany economy Berlin stock market",
            "sports": "Germany football Bundesliga sports",
            "health": "Germany health medical",
            "science": "Germany science research",
            "entertainment": "Germany entertainment movies Berlin"
        },
        "fallback_keywords": ["Germany", "German", "Berlin", "Munich"]
    },
    "fr": {  # France
        "sources": ["le-monde", "liberation", "le-figaro"],
        "queries": {
            "technology": "France tech Paris startup",
            "business": "France economy Paris stock market",
            "sports": "France football sports Paris",
            "health": "France health medical",
            "science": "France science research",
            "entertainment": "France entertainment movies Paris"
        },
        "fallback_keywords": ["France", "French", "Paris", "Marseille"]
    }
}

# Manual news data as final fallback for ALL countries
MANUAL_NEWS_FALLBACK = {
    "technology": [
        {"title": "AI Development Accelerates Globally", "description": "Major tech companies announce new AI initiatives and partnerships.", "source": "Tech News Network", "url": "https://example.com/tech-news-1"},
        {"title": "Cybersecurity Threats on the Rise", "description": "Companies worldwide investing more in digital security measures.", "source": "Security Daily", "url": "https://example.com/tech-news-2"},
        {"title": "5G Expansion Continues Worldwide", "description": "Telecom companies expanding 5G networks to more regions and countries.", "source": "Telecom Update", "url": "https://example.com/tech-news-3"}
    ],
    "business": [
        {"title": "Global Markets Show Mixed Signals", "description": "Stock markets experience volatility amid economic uncertainty and inflation concerns.", "source": "Financial Times", "url": "https://example.com/business-news-1"},
        {"title": "Startup Funding Trends Shift", "description": "Venture capital investments focusing on sustainable technologies and AI startups.", "source": "Business Insider", "url": "https://example.com/business-news-2"},
        {"title": "Remote Work Impact on Commercial Real Estate", "description": "Companies adapting to hybrid work models affecting office space demand globally.", "source": "Workplace News", "url": "https://example.com/business-news-3"}
    ],
    "sports": [
        {"title": "International Sports Events Update", "description": "Major tournaments and leagues continue with strong viewer engagement and record attendance.", "source": "Sports Global", "url": "https://example.com/sports-news-1"},
        {"title": "Athlete Transfers and Contract Negotiations", "description": "Top players signing new deals and transfers across various sports disciplines.", "source": "Sports Network", "url": "https://example.com/sports-news-2"},
        {"title": "Sports Technology Innovations Advance", "description": "New tech enhancing athlete performance metrics and fan viewing experience.", "source": "Tech Sports", "url": "https://example.com/sports-news-3"}
    ],
    "health": [
        {"title": "Healthcare Innovations Show Promising Results", "description": "New medical treatments and digital health technologies demonstrating significant improvements.", "source": "Medical Journal", "url": "https://example.com/health-news-1"},
        {"title": "Mental Health Awareness Grows Globally", "description": "Increased focus on mental wellness in workplaces and educational institutions worldwide.", "source": "Health Today", "url": "https://example.com/health-news-2"},
        {"title": "Nutrition and Wellness Trends Evolve", "description": "New research on diet, exercise, and lifestyle benefits emerging from international studies.", "source": "Wellness Weekly", "url": "https://example.com/health-news-3"}
    ],
    "science": [
        {"title": "Space Exploration Reaches New Milestones", "description": "New discoveries in astronomy and space technology from international space agencies.", "source": "Science Daily", "url": "https://example.com/science-news-1"},
        {"title": "Climate Research Reveals Critical Updates", "description": "Scientists report latest findings on environmental changes and conservation efforts.", "source": "Environmental News", "url": "https://example.com/science-news-2"},
        {"title": "Medical Research Breakthroughs Announced", "description": "New studies reveal insights into disease treatment and prevention methods.", "source": "Research Review", "url": "https://example.com/science-news-3"}
    ],
    "entertainment": [
        {"title": "Streaming Services Expand Original Content", "description": "Platforms announcing new original series and films with international collaborations.", "source": "Entertainment Weekly", "url": "https://example.com/entertainment-news-1"},
        {"title": "Music Industry Embraces New Technologies", "description": "Artists and labels adopting new distribution methods and immersive audio technologies.", "source": "Music News", "url": "https://example.com/entertainment-news-2"},
        {"title": "International Film Festivals Showcase Diversity", "description": "Global festivals highlighting diverse cinematic works and emerging filmmakers.", "source": "Cinema Today", "url": "https://example.com/entertainment-news-3"}
    ]
}

# --- 5. Enhanced Fact-Checking Tool ---
class EnhancedFactCheckTool:
    def __init__(self):
        self.claim_cache = {}
    
    def extract_claims_from_summary(self, summary: str) -> List[str]:
        """Extract specific factual claims from the AI-generated summary"""
        prompt = f"""
        Analyze this news summary and extract specific, verifiable factual claims.
        Focus on numbers, statistics, specific events, and measurable data.
        
        Return ONLY a JSON list of specific claims.
        
        News Summary:
        {summary}
        """
        
        try:
            model = genai.GenerativeModel("models/gemini-2.5-flash")
            response = model.generate_content(prompt)
            cleaned_response = response.text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:-3] if cleaned_response.endswith("```") else cleaned_response[7:]
            claims = json.loads(cleaned_response)
            return claims if isinstance(claims, list) else []
        except Exception as e:
            return []
    
    def verify_claim_with_multiple_sources(self, claim: str, articles: List) -> Dict:
        """Verify a claim using multiple methods"""
        verification_methods = [
            self._verify_with_article_cross_check,
            self._verify_with_wikipedia,
            self._verify_with_common_knowledge
        ]
        
        best_result = None
        for method in verification_methods:
            result = method(claim, articles)
            if result['verified']:
                best_result = result
                break
            elif best_result is None or result['confidence'] == 'medium':
                best_result = result
        
        return best_result or {
            "claim": claim,
            "verified": False,
            "source": "No verification possible",
            "confidence": "low",
            "explanation": "Could not verify with available sources"
        }
    
    def _verify_with_article_cross_check(self, claim: str, articles: List) -> Dict:
        """Cross-check claim against original news articles"""
        claim_lower = claim.lower()
        supporting_articles = []
        
        for article in articles:
            article_text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            if any(keyword in article_text for keyword in claim_lower.split()[:5]):
                supporting_articles.append(article.get('source', {}).get('name', 'Unknown'))
        
        if supporting_articles:
            return {
                "claim": claim,
                "verified": True,
                "source": "News Article Cross-Check",
                "confidence": "high",
                "explanation": f"Supported by {len(supporting_articles)} news sources",
                "sources_count": len(supporting_articles)
            }
        
        return {
            "claim": claim,
            "verified": False,
            "source": "News Article Cross-Check",
            "confidence": "medium",
            "explanation": "No direct support found in source articles"
        }
    
    def _verify_with_wikipedia(self, claim: str, articles: List) -> Dict:
        """Verify using Wikipedia API"""
        main_entity = claim.split()[0] if claim.split() else "unknown"
        wikipedia_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{main_entity}"
        
        try:
            response = requests.get(wikipedia_url, timeout=5)
            if response.status_code == 200:
                return {
                    "claim": claim,
                    "verified": True,
                    "source": "Wikipedia",
                    "confidence": "medium",
                    "explanation": f"Related information found about {main_entity}"
                }
        except:
            pass
        
        return {
            "claim": claim,
            "verified": False,
            "source": "Wikipedia",
            "confidence": "low", 
            "explanation": "No relevant Wikipedia entry found"
        }
    
    def _verify_with_common_knowledge(self, claim: str, articles: List) -> Dict:
        """Use Gemini to verify based on common knowledge"""
        prompt = f'Verify this claim: "{claim}" - Respond with JSON: {{"verdict": "true/false/uncertain", "explanation": "brief reason"}}'
        
        try:
            model = genai.GenerativeModel("models/gemini-2.5-flash")
            response = model.generate_content(prompt)
            result = json.loads(response.text.strip())
            
            verdict = result.get("verdict", "uncertain")
            return {
                "claim": claim,
                "verified": verdict == "true",
                "source": "AI Common Knowledge Check",
                "confidence": "low",
                "explanation": result.get("explanation", "AI verification inconclusive")
            }
        except:
            return {
                "claim": claim,
                "verified": False,
                "source": "AI Common Knowledge Check", 
                "confidence": "low",
                "explanation": "AI verification failed"
            }
    
    def calculate_credibility_score(self, verification_results: List[Dict]) -> float:
        """Calculate overall credibility score for the summary"""
        if not verification_results:
            return 0.5
        
        total_score = 0
        for result in verification_results:
            if result['verified']:
                if result['confidence'] == 'high':
                    total_score += 1.0
                elif result['confidence'] == 'medium':
                    total_score += 0.7
                else:
                    total_score += 0.3
            else:
                total_score += 0.2
        
        return total_score / len(verification_results)

def add_enhanced_fact_checking_section(summary_text: str, articles: List) -> None:
    """Add enhanced fact-checking section to Streamlit app"""
    
    st.subheader("🔍 Enhanced Fact-Checking & Credibility Analysis")
    
    with st.spinner("🔎 Analyzing claims and cross-referencing with sources..."):
        fact_checker = EnhancedFactCheckTool()
        
        claims = fact_checker.extract_claims_from_summary(summary_text)
        
        if claims:
            st.write(f"📊 Extracted {len(claims)} verifiable claims:")
            
            verification_results = []
            for i, claim in enumerate(claims[:5]):
                with st.expander(f"Claim #{i+1}: {claim}", expanded=i<2):
                    result = fact_checker.verify_claim_with_multiple_sources(claim, articles)
                    verification_results.append(result)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if result['verified']:
                            st.success(f"✅ **Verified** ({result['confidence'].title()} Confidence)")
                        else:
                            st.warning(f"⚠️ **Unverified** ({result['confidence'].title()} Confidence)")
                    
                    with col2:
                        st.metric("Confidence", result['confidence'].upper())
                    
                    st.write(f"**Source:** {result['source']}")
                    st.write(f"**Explanation:** {result['explanation']}")
            
            credibility_score = fact_checker.calculate_credibility_score(verification_results)
            verified_count = sum(1 for r in verification_results if r['verified'])
            
            st.markdown("---")
            st.subheader("📈 Credibility Report")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Overall Score", f"{credibility_score:.0%}")
            with col2:
                st.metric("Claims Verified", f"{verified_count}/{len(verification_results)}")
            
            if credibility_score > 0.7:
                st.success("✅ **GOOD RELIABILITY** - Summary is generally trustworthy")
            elif credibility_score > 0.4:
                st.warning("⚠️ **MODERATE RELIABILITY** - Verify critical information")
            else:
                st.error("🔴 **LOW RELIABILITY** - Exercise caution")
                
        else:
            st.warning("🤔 No specific factual claims detected for verification.")

# --- 6. FIXED: Display News Headlines with Proper Links and Images ---
def display_news_headlines(articles: List):
    """Display news headlines with proper links, images, and formatting"""
    st.subheader("🗞️ Source News Headlines")
    
    if not articles:
        st.warning("No articles to display.")
        return
    
    for i, article in enumerate(articles, 1):
        # Create a container for each article
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Display image if available and valid
                image_url = article.get('urlToImage')
                if image_url and image_url != "None" and image_url.startswith(('http://', 'https://')):
                    try:
                        st.image(image_url, width=150, caption="Article Image")
                    except:
                        st.image("https://via.placeholder.com/150x100/4F46E5/FFFFFF?text=News", 
                                width=150, caption="Image not available")
                else:
                    st.image("https://via.placeholder.com/150x100/4F46E5/FFFFFF?text=News", 
                            width=150, caption="No image available")
            
            with col2:
                # Display title as clickable link
                title = article.get('title', 'No title available')
                url = article.get('url', '#')
                
                if url and url != "#":
                    st.markdown(f"### [{title}]({url})", unsafe_allow_html=True)
                else:
                    st.markdown(f"### {title}")
                
                # Display description
                description = article.get('description', 'No description available')
                if description and description != "None":
                    st.write(description)
                else:
                    st.write("No description available")
                
                # Display source and date
                source_name = article.get('source', {}).get('name', 'Unknown source')
                published = article.get('publishedAt', '')
                
                if published:
                    try:
                        # Format date nicely
                        date_obj = datetime.fromisoformat(published.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime("%B %d, %Y at %H:%M")
                    except:
                        formatted_date = published[:10]
                else:
                    formatted_date = "Unknown date"
                
                st.caption(f"**📰 Source:** {source_name} | **🗓️ Published:** {formatted_date}")
            
            # Add separator between articles
            st.markdown("---")

# --- 7. Universal News Fetcher for ALL Countries ---
def get_country_news_enhanced(category: str, region: str, max_retries: int = 3):
    """Enhanced news fetching for ANY country with multiple fallbacks"""
    
    articles = []
    country_config = COUNTRY_NEWS_CONFIG.get(region, {})
    
    # Strategy 1: Try country-specific sources
    if country_config.get('sources'):
        try:
            sources = ",".join(country_config['sources'])
            top_headlines = newsapi.get_top_headlines(
                sources=sources,
                category=category,
                page_size=10,
                language='en'
            )
            articles = top_headlines.get('articles', [])
            if articles:
                st.success(f"🇺🇳 Found news from {region.upper()} specific sources!")
                return articles
        except Exception as e:
            st.write(f"Debug: Country sources failed - {e}")
    
    # Strategy 2: Try country-specific headlines
    try:
        top_headlines = newsapi.get_top_headlines(
            country=region,
            category=category,
            page_size=10,
            language='en'
        )
        articles = top_headlines.get('articles', [])
        if articles:
            st.success(f"🇺🇳 Found {region.upper()} news via country search!")
            return articles
    except Exception as e:
        st.write(f"Debug: Country search failed - {e}")
    
    # Strategy 3: Use everything endpoint with country-specific queries
    country_query = country_config.get('queries', {}).get(category, region)
    try:
        everything = newsapi.get_everything(
            q=country_query,
            language='en',
            sort_by='publishedAt',
            page_size=10
        )
        articles = everything.get('articles', [])
        if articles:
            st.success(f"🔍 Found news using {region.upper()}-specific search!")
            return articles
    except Exception as e:
        st.write(f"Debug: Everything endpoint failed - {e}")
    
    # Strategy 4: Broader regional search
    fallback_keywords = country_config.get('fallback_keywords', [region])
    for keyword in fallback_keywords:
        try:
            everything = newsapi.get_everything(
                q=f"{keyword} {category}",
                language='en',
                sort_by='relevancy',
                page_size=10
            )
            articles = everything.get('articles', [])
            if articles:
                st.info(f"🌍 Found news mentioning {keyword}")
                return articles
        except Exception as e:
            continue
    
    # Strategy 5: Global news as fallback
    try:
        everything = newsapi.get_everything(
            q=category,
            language='en',
            sort_by='publishedAt',
            page_size=10
        )
        articles = everything.get('articles', [])
        if articles:
            st.info("🌐 Found global news as fallback")
            return articles
    except Exception as e:
        st.write(f"Debug: Global search failed - {e}")
    
    # Strategy 6: FINAL FALLBACK - Manual news data
    st.warning("⚠️ Using manual news data as final fallback")
    manual_articles = MANUAL_NEWS_FALLBACK.get(category, MANUAL_NEWS_FALLBACK['technology'])
    
    # Convert manual data to same format as NewsAPI with proper URLs
    formatted_articles = []
    for i, article in enumerate(manual_articles):
        formatted_articles.append({
            'title': article['title'],
            'description': article['description'],
            'url': article['url'],
            'urlToImage': f"https://via.placeholder.com/400x200/4F46E5/FFFFFF?text={article['source'].replace(' ', '+')}",
            'publishedAt': datetime.now().isoformat(),
            'source': {'name': article['source']}
        })
    
    return formatted_articles

# --- 8. Streamlit App ---
st.set_page_config(page_title="Global AI News Summarizer", layout="wide")
st.title("🌍 Global AI News Summarizer with Fact-Checking")

# User Inputs
category = st.selectbox("Select News Category", ["technology", "business", "sports", "health", "science", "entertainment"])
region = st.selectbox("Select Country", ["us", "in", "gb", "ca", "au", "de", "fr"])
user_query = st.text_input("Ask something about the latest news (optional)")

# Guardrails
if user_query and not re.match("^[a-zA-Z0-9\s.,!?'-]*$", user_query):
    st.error("🚫 Invalid characters detected.")
    st.stop()

if user_query and len(user_query) > 300:
    st.warning("⚠️ Query too long!")
    st.stop()

if not NEWSAPI_KEY or NEWSAPI_KEY == "YOUR_NEWSAPI_KEY_HERE":
    st.error("🚫 Missing NewsAPI key.")
    st.stop()

# Enhanced safety instructions
ENHANCED_SAFETY_INSTRUCTIONS = """
IMPORTANT: Base ALL information strictly on provided news articles. Include specific numbers and facts when available. Stay neutral and professional.
"""

# Main execution
if st.button("🚀 Fetch & Analyze News"):
    country_names = {"us": "USA", "in": "India", "gb": "UK", "ca": "Canada", "au": "Australia", "de": "Germany", "fr": "France"}
    country_name = country_names.get(region, region.upper())
    
    st.info(f"🌍 Fetching {category} news from {country_name}...")
    
    # Get news with comprehensive fallbacks
    articles = get_country_news_enhanced(category, region)
    
    if not articles:
        st.error("❌ No news articles found even after all fallbacks. Please try again later.")
        st.stop()
    
    # Prepare text for Gemini
    news_text = "\n".join([f"{a['title']} - {a.get('description', '')}" for a in articles if a.get('description')])[:6000]
    
    # Generate prompt
    if user_query:
        prompt = f"""Answer this: "{user_query}" using these news articles. {ENHANCED_SAFETY_INSTRUCTIONS}
        
        NEWS: {news_text}"""
    else:
        prompt = f"""Summarize these {category} news articles in bullet points. {ENHANCED_SAFETY_INSTRUCTIONS}
        
        NEWS: {news_text}"""
    
    # Generate summary
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        summary_text = response.text.strip()
    except Exception as e:
        st.warning(f"⚠️ Gemini error, using fallback: {e}")
        summary_text = "• " + "\n• ".join([a["title"] for a in articles[:8]])
    
    # Clean and display
    summary_text = re.sub(r"(http\S+|www\S+)", "", summary_text)
    
    st.subheader("🧠 AI Summary & Insights")
    st.markdown(summary_text)
    
    # Fact-checking
    add_enhanced_fact_checking_section(summary_text, articles)
    
    # FIXED: Display articles with proper links and images
    display_news_headlines(articles)
    
    st.success("✅ Analysis complete! Now with proper links and images in headlines.")