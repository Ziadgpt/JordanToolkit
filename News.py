
import requests

API_KEY = "331b934071f74ed3bdf150d9c2aaf2fe"  # Replace with your API key

def fetch_gold_news():
    url = (
        "https://newsapi.org/v2/everything?"
        "q=gold+OR+XAUUSD+OR+USD+OR+Fed+OR+inflation+OR+interest+rates&"
        "language=en&sortBy=publishedAt&pageSize=10&"
        f"apiKey={API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    if data["status"] == "ok":
        print("\n🟡 Relevant Macro News for Gold (Top 10):\n")
        for article in data["articles"]:
            print(f"🗞️ {article['title']}")
            print(f"🔗 {article['url']}")
            print(f"🕒 Published: {article['publishedAt']}")
            print("-" * 60)
    else:
        print("Failed to fetch news:", data)

# Run it
fetch_gold_news()
