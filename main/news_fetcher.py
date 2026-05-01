import feedparser
import requests
from datetime import datetime
import os


def fetch_techcrunch(news_num: int = 1):
    """TechCrunch RSS 피드에서 최신 기사 가져오기"""
    feed = feedparser.parse('https://techcrunch.com/feed/')
    articles = []

    for entry in feed.entries[:news_num]:  # 최신 5개만
        articles.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.summary
        })

    return articles


def fetch_hackernews(news_num: int = 1):
    """Hacker News API에서 top stories 가져오기"""
    top_stories_url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    top_ids = requests.get(top_stories_url).json()[:news_num]  # 상위 5개

    articles = []
    for story_id in top_ids:
        story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
        story = requests.get(story_url).json()

        if story.get('type') == 'story':
            articles.append({
                'title': story.get('title'),
                'link': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                'score': story.get('score'),
                'by': story.get('by')
            })

    return articles


if __name__ == "__main__":
    print("=== TechCrunch 최신 기사 ===")
    tc_articles = fetch_techcrunch(3)
    for article in tc_articles:
        print(f"- {article['title']}")
        print(f"  {article['link']}\n")

    print("\n=== Hacker News Top Stories ===")
    hn_articles = fetch_hackernews(3)
    for article in hn_articles:
        print(f"- {article['title']} (score: {article['score']})")
        print(f"  {article['link']}\n")