import requests
import feedparser
import os
from datetime import datetime
from openai import OpenAI

# Configuration
RSS_FEEDS = [
    'https://hnrss.org/newest?q=AI',
    'https://www.reddit.com/r/artificial/.rss',
    'https://www.jiqizhixin.com/rss'
]

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def fetch_articles(limit=10):
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', '')
                })
        except Exception as e:
            print(f'Error fetching {feed_url}: {e}')
    return articles

def summarize_with_llm(articles):
    if not articles:
        return 'No articles found.'
    text = '\n'.join([f"- {a['title']} ({a['link']})" for a in articles])
    prompt = f"Summarize these AI news items into a daily digest, highlighting key trends and insights:\n{text}"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f'LLM error: {e}'

def generate_daily_digest():
    articles = fetch_articles()
    digest = summarize_with_llm(articles)
    date_str = datetime.now().strftime('%Y-%m-%d')
    with open(f'digest_{date_str}.md', 'w') as f:
        f.write(f'# AI Daily Digest - {date_str}\n\n{digest}\n\n## Sources\n')
        for a in articles:
            f.write(f'- [{a['title']}]({a['link']})\n')
    print(f'Saved digest_{date_str}.md')

if __name__ == '__main__':
    generate_daily_digest()
