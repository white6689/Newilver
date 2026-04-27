if __name__ == "__main__":
    articles = fetch_all_sources()
    summary = summarize_articles(articles)
    send_email("TechDigest", summary, "your@email.com")