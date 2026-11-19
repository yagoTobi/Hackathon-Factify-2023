import os
import re
from dotenv import load_dotenv
try:
    from langchain.chains import LLMChain
except ImportError:
    class LLMChain:
        def __init__(self, llm, prompt):
            self.chain = prompt | llm
        def invoke(self, input):
            res = self.chain.invoke(input)
            raw = res.content if hasattr(res, "content") else res
            if isinstance(raw, list):
                # Handle structured blocks like [{'type': 'text', 'text': '...'}]
                text = "".join([b.get("text", "") for b in raw if isinstance(b, dict)])
            elif isinstance(raw, dict):
                text = raw.get("text", str(raw))
            else:
                text = str(raw)
            return {"text": text.strip()}
from langchain_core.prompts import PromptTemplate
from datetime import date

# Import LLM providers with graceful fallbacks
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

# Load environment variables from both NewsAgent/.env and root .env
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def llm_connect(model_name="gemini-3.1-flash-lite", temperature=0.0):
    """
    Connects to the appropriate LLM provider.
    Prefers Gemini (gemini-3.1-flash-lite) if GEMINI_API_KEY or GOOGLE_API_KEY is present,
    falling back to OpenAI if OPENAI_API_KEY is present.
    """
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    # Override model if specified in environment
    target_model = os.getenv("GEMINI_MODEL") or model_name

    # If gemini key exists or model requested is gemini, use Gemini
    if (gemini_key or "gemini" in str(target_model).lower()) and ChatGoogleGenerativeAI is not None:
        return ChatGoogleGenerativeAI(
            model=target_model if "gemini" in str(target_model).lower() else "gemini-3.1-flash-lite",
            temperature=float(temperature),
            google_api_key=gemini_key
        )

    # Fallback to OpenAI if configured
    if openai_key and ChatOpenAI is not None:
        fallback_model = "gpt-3.5-turbo" if "gemini" in str(target_model).lower() else target_model
        return ChatOpenAI(
            temperature=float(temperature),
            model_name=fallback_model,
            api_key=openai_key
        )

    # Default to Gemini attempt
    if ChatGoogleGenerativeAI is not None:
        return ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite",
            temperature=float(temperature),
            google_api_key=gemini_key
        )
    elif ChatOpenAI is not None:
        return ChatOpenAI(temperature=float(temperature), model_name="gpt-3.5-turbo", api_key=openai_key)
    else:
        raise RuntimeError("No LLM provider library available. Install langchain-google-genai or langchain-openai.")


def generate_url_prompt(user_query, today_date):
    template: str = """
    Your task is to generate a URL for NewsAPI that directly corresponds to {user_query}. 
    Focus on identifying the most relevant keywords or phrases from the query "{user_query}" to ensure the URL will fetch articles closely related to the topic.

    Key considerations for constructing the URL:
    - Extract the main topic or keywords from "{user_query}" accurately.
    - If there is a date or time frame mentioned, determine the appropriate time frame for the search. If so, today's date is {today_date}. Otherwise, be sure to leave the fields empty.
    - Use the correct language setting based on the query's language.
    - For queries without a date, use general searches and format the URL as follows:
        https://newsapi.org/v2/everything?q={{main-topic-or-keyword}}&pageSize=10
    - For queries with a given date or date range, use specific searches and format the URL as follows:
        https://newsapi.org/v2/top-headlines?q={{main-topic-or-keyword}}&from={{start-date}}&to={{end-date}}&category={{category}}&pageSize=10

    This are the possible categories you can use, if you are not sure for specific queries, pick general as the default category:
    business - entertainment - general - health - science - sports - technology

    Search Example (Specific Search):
    Given the query "NVIDIA Stock Jump this week", construct a URL that fetches the most recent and relevant articles about this topic from NewsAPI. Imagine today's date is 2024-02-29.
    Query output -> https://newsapi.org/v2/top-headlines?q={{US Economy and Stock Market}}&from={{2024-02-23}}&to={{2024-02-29}}&category={{business}}&pageSize=10

    Search Example (General Search):
    Given the query "I want to learn about the climate change" construct a URL that fetches the most recent and relevant articles about this topic from NewsAPI.
    Query output -> https://newsapi.org/v2/everything?q={{Climate Change}}&pageSize=10

    Remember, focus on accuracy and relevancy in your response. Remember, only return the URL generated, don't give any further explanation.
    Also remember, the placeholders within {{}} should be replaced with information relevant to the search query. Aim for precision in keyword selection to ensure the resulting articles are on-topic.
"""
    # Correctly use the named placeholder in the format call
    prompt_template = PromptTemplate(
        template=template, input_variables=["user_query", "today_date"]
    )

    return prompt_template


def generate_search_url(user_query):
    today_date = date.today()
    # Creating an LLMChain instance
    chain = LLMChain(
        llm=llm_connect(), prompt=generate_url_prompt(user_query, today_date)
    )
    # Run the chain to get the response
    response = chain.invoke(input={"user_query": user_query, "today_date": today_date})
    raw_text = response["text"] if isinstance(response, dict) and "text" in response else str(response)

    # In case response is a list or contains markdown
    if isinstance(raw_text, list):
        raw_text = "".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in raw_text])
    else:
        raw_text = str(raw_text)

    # Extract clean http(s) URL if wrapped in extra text or quotes
    match = re.search(r'https?://[^\s\'"<>]+', raw_text)
    if match:
        return match.group(0).strip()
    return raw_text.strip()


if __name__ == "__main__":
    query = "NVIDIA Stock Market Jump this week"
    link = generate_search_url(query)
