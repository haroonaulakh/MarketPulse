import os
import re
import json
import requests
import boto3
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

S3_BUCKET = "marketpulse-raw-haroonalk"
S3_PREFIX = "news"
NEWSAPI_URL = "https://newsapi.org/v2/everything"


TICKER_MAP = {
    "AAPL":  ["Apple"],
    "MSFT":  ["Microsoft"],
    "GOOGL": ["Google", "Alphabet"],
    "NVDA":  ["Nvidia", "NVIDIA"],
    "AMZN":  ["Amazon"],
    "META":  ["Meta", "Facebook"],
    "JPM":   ["JPMorgan", "JP Morgan"],
    "V":     ["Visa"],
    "JNJ":   ["Johnson & Johnson"],
    "UNH":   ["UnitedHealth"],
    "TSLA":  ["Tesla"],
    "WMT":   ["Walmart"],
    "KO":    ["Coca-Cola", "Coca Cola"],
    "XOM":   ["Exxon", "ExxonMobil"],
    "CVX":   ["Chevron"],
    "BA":    ["Boeing"],
}


def build_query(ticker_map):
    
    terms = []

    for ticker, names in ticker_map.items():
        terms.append(f'"{ticker}"')
        for name in names:
            terms.append(f'"{name}"')

    return " OR ".join(terms)


def compile_ticker_patterns(ticker_map):
    
    patterns = {}
    for ticker, names in ticker_map.items():

        terms = [ticker] + names
        escaped = [re.escape(t) for t in terms]
        
        patterns[ticker] = re.compile(
            r"\b(" + "|".join(escaped) + r")\b", re.IGNORECASE
        )
    return patterns


def tag_articles_with_tickers(articles, patterns):

    for art in articles:
        text = " ".join(
            filter(None, [art.get("title"), art.get("description")])
        )
        matched = [t for t, pat in patterns.items() if pat.search(text)]
        art["matched_tickers"] = matched
    return articles


def fetch_news(api_key, query):
    
    # last 3 days keeps results tight + relevant (adjustable)
    from_date = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%d")

    params = {
        "q": query,
        "from": from_date,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 100,   # max allowed 
        "apiKey": api_key,
    }
    response = requests.get(NEWSAPI_URL, params=params, timeout=30)

    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != "ok":
        raise RuntimeError(f"NewsAPI error: {payload}")
    return payload.get("articles", [])


def write_to_s3(data, bucket, prefix):

    s3 = boto3.client("s3")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

    key = f"{prefix}/news_{timestamp}.json"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2).encode("utf-8"),
        ContentType="application/json",
    )
    return key


def main():
    load_dotenv()
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise RuntimeError("NEWSAPI_KEY not found in .env")

    query = build_query(TICKER_MAP)
    print(f"Query length: {len(query)} chars")
    print(f"Fetching news (1 API request)...")

    articles = fetch_news(api_key, query)
    print(f"Fetched {len(articles)} articles.")

    patterns = compile_ticker_patterns(TICKER_MAP)
    articles = tag_articles_with_tickers(articles, patterns)

    # summary
    coverage = {t: 0 for t in TICKER_MAP}
    for art in articles:
        for t in art["matched_tickers"]:
            coverage[t] += 1

    key = write_to_s3(articles, S3_BUCKET, S3_PREFIX)
    print(f"Written: s3://{S3_BUCKET}/{key}")

    print("\nArticles matched per ticker:")
    for ticker, count in sorted(coverage.items(), key=lambda x: -x[1]):
        print(f"  {ticker}: {count}")

    unmatched = sum(1 for a in articles if not a["matched_tickers"])
    print(f"\nArticles with no ticker match (kept anyway): {unmatched}")


if __name__ == "__main__":
    main()