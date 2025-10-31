# LLM-Training-Automations
AI News Summarizer (Google Gemini + Streamlit + Guardrails)

An intelligent AI-powered news summarization system that fetches real-time headlines, applies safety guardrails, and uses Google Gemini to generate structured summaries and sentiment analysis.

This project is built using Streamlit, NewsAPI, and Google Gemini 2.5 Flash, and was developed and debugged using Cursor AI code editor for efficient coding, automation, and LLM integration.

🌟 Features

Fetches latest news by category and region.

Allows custom user queries for specific insights.

Summarizes with Gemini 2.5 Flash, ensuring factual, neutral results.

Produces 10+ key bullet points per summary.

Uses 5+ AI safety guardrails for reliability and trustworthiness.

Automatic fallbacks and handoffs if APIs fail.

Clean, dark-mode Streamlit interface with contrasting text and visuals.

[User Input]
   │
   ├── Input Guardrails (Validation + Token Limit)
   │
   ▼
[News Fetching]
   ├── Regional Headlines
   ├── Fallback → General
   └── Fallback → Global
   │
   ▼
[Gemini Summarizer]
   ├── Multi-point Summary (≥ 10)
   ├── Sentiment Analysis
   └── User Query Handling
   │
   ▼
[Streamlit UI]
   ├── Clean Display
   ├── Output Sanitization
   └── Download Summary Option


🛡️ Guardrails Implemented
#	Guardrail	Description
1️⃣	Input Validation	Blocks special characters & unsafe inputs

2️⃣	Query Length Control	Prevents long/spammy prompts

3️⃣	Token Limit	Restricts text size to model-safe range

4️⃣	Fallback Handling	Switches to general/global news or extractive summary

5️⃣	Output Cleaning	Removes URLs, markup, and unsafe text

6️⃣	Neutrality Enforcement	Gemini instructed to avoid political bias or speculation

🔄 Handoffs Implemented

Handoffs ensure graceful degradation when certain steps fail.

| Stage                    | Handoff Type                      | Purpose                                  |
| :----------------------- | :-------------------------------- | :--------------------------------------- |
| 📰 **NewsAPI**           | Regional → General → Global       | Ensures some results always appear.      |
| 🧠 **Gemini Summarizer** | Summarizer → Extractive Headlines | Prevents blank output if LLM fails.      |
| 🧩 **Input**             | Invalid → Controlled Stop         | Protects the system from unsafe queries. |
| 💬 **Output**            | Raw → Sanitized                   | Keeps responses safe and readable.       |

| Tool                     | Purpose                                                          |
| :----------------------- | :--------------------------------------------------------------- |
| **Cursor**               | Main AI-assisted IDE for coding, debugging, and LLM integration. |
| **Streamlit**            | Frontend framework for interactive web UI.                       |
| **Google Gemini API**    | Performs text summarization and analysis.                        |
| **NewsAPI**              | Fetches real-time categorized news data.                         |
| **Python-dotenv**        | Manages API keys securely.                                       |
| **Regex + Custom Logic** | Used for guardrails, input validation, and text cleaning.        |

🎨 User Interface

Modern dark theme background (#0f172a)

Contrasting text and buttons for readability

Streamlit widgets for category, region, and user queries

Displays both summarized insights and raw headlines

⚙️ Setup
1️⃣ Prerequisites

Python ≥ 3.9

Valid API keys for NewsAPI and Gemini

2️⃣ Installation
git clone https://github.com/SaiPavan-28/LLM-Training-Automations.git
cd ai-news-summarizer
pip install -r requirements.txt

3️⃣ Environment Variables

Create a .env file in the project root:

NEWSAPI_KEY=your_newsapi_key
GEMINI_API_KEY=your_gemini_api_key

4️⃣ Run the App
streamlit run ai_news_summarizer_guarded.py

📊 Example Output

Category: Technology
Region: IN
Sentiment: Neutral

1. AI startups in India raised over $100M in funding.
2. Government introduced AI governance framework.
3. Indian universities launch AI-focused programs.
4. Major tech firms open new AI research hubs.
5. AI usage in healthcare continues to rise.
...

![alt text](<WhatsApp Image 2025-10-31 at 01.08.30_0b30abec.jpg>)

![alt text](<WhatsApp Image 2025-10-31 at 01.08.47_2f197877.jpg>)

![alt text](<WhatsApp Image 2025-10-31 at 01.09.13_6f2e2476.jpg>)

🧩 Tech Stack
| Component | Technology |

| Frontend/UI |	Streamlit |

| Backend Logic | Python |

| News Fetching | NewsAPI|

| LLM Summarizer | Google Gemini 2.5 Flash |

| IDE & Development | Cursor |

| Security/Env Mgmt | dotenv |

🚀 Future Enhancements

Add multi-language summarization using Gemini’s translation.

Include voice-based query input for accessibility.

Enable email summaries for subscribed users.

Integrate Gemini Pro for deeper reasoning and insight generation.
