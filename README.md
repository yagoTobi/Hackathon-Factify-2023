# Factify - AI-Powered Balanced News Synthesizer

![Factify Home Screen](img_repo/Factify_Home_Screen.jpeg)

Factify is an AI agent application that aggregates news coverage from diverse sources and synthesizes a comprehensive, balanced, and unbiased story for the reader.

---

## 🌟 What's New in this Update

- **Relative Slant & Extremism Classification**: Evaluates retrieved articles together in a single batch prompt, using the cohort as mutual anchors to accurately detect political framing (-1.0 Far Left to +1.0 Far Right) and rhetorical extremism (0.0 to 1.0).
- **Extremism Outlier Pruning**: Automatically filters out radical, conspiratorial, or hyper-partisan fringe sources exceeding the extremism threshold (default `0.85`).
- **Proportional Viewpoint Balancing**: Enforces a proportional quota (e.g., max 40% representation from any single ideological bucket), ensuring the final synthesis draws from a healthy distribution of Left, Center, and Right sources without echo-chamber dominance.
- **Gemini 3.8 / 2.5 Flash Migration**: Replaced legacy LLM chains with Google Gemini (`gemini-2.5-flash` / `gemini-3.8-flash`), significantly reducing hallucinations, improving processing speeds, and slashing token latency.
- **75%+ AI Call Reduction**: Replaced slow individual per-article summarizer API calls (Maisa API) with local extractive NLP summaries via `newspaper3k`, dropping total pipeline roundtrips from ~25+ down to ~7 calls.
- **Local Credential Protection**: Standardized `.gitignore` and `.env.example` to prevent accidental credential leakage.

---

## 🏗️ Architecture Pipeline

```
1. Search Query ──► NewsAPI Construct & Ingestion
                          │
                          ▼
2. Extractive NLP ──► Local newspaper3k TextRank summaries (0 API calls)
                          │
                          ▼
3. Batch Classifier ──► Single Gemini Call with Mutual Anchoring
                          │   Annotates relative slant (-1 to +1) & extremism (0 to 1)
                          ▼
4. Outlier Filter ────► Prunes sources with extremism > 0.85
                          │
                          ▼
5. Proportional Cap ──► Buckets into Left / Center / Right
                          │   Caps any single category at 40% (prioritizing least extreme)
                          ▼
6. Fact Extraction ───► Parallel bullet-point extraction on balanced cohort only
                          │
                          ▼
7. Final Synthesis ───► Unified Economist-style article with attributed citations
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key ([Google AI Studio](https://aistudio.google.com/))
- A NewsAPI Key ([NewsAPI.org](https://newsapi.org/))

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/yagoTobi/Hackathon-Factify-2023.git
cd Hackathon-Factify-2023

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the sample environment file and configure your API keys:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
NEWSAPI_KEY=your_newsapi_key_here
```

---

## 🧪 Testing and Verification

### Run the Demo / Verification Script
We provide a standalone demonstration script that runs without needing live API keys:
```bash
python test_factify_demo.py
```
This tests the full cohort ingestion, outlier pruning, and proportional balancing logic on a simulated skewed dataset.

To run with live API calls:
```bash
python test_factify_demo.py --live --query "Global Semiconductor Supply Chain"
```

### Run Unit Tests
```bash
python -m unittest tests/test_bias_filter.py
```

---

## 📂 Project Structure

```
├── NewsAgent/
│   ├── article_creator.py     # Batch classifier, proportional balancer, synthesis
│   ├── news_extractor.py      # Article fetcher and local extractive NLP summarizer
│   ├── query_constructor.py   # Query planner & Gemini/OpenAI connection wrapper
│   └── streamlit/             # Web interface
├── tests/
│   └── test_bias_filter.py    # Automated test suite for slant & outlier filtering
├── test_factify_demo.py       # Standalone interactive demo script
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md
```

---

## 🤝 Contributing
Contributions are welcome! Please check out the issues or open a pull request.
