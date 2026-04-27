import os
from anthropic import Anthropic


def summarize_articles(articles, source_name):
    """여러 기사를 AI로 요약"""
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # 기사 목록을 텍스트로 정리
    articles_text = f"\n\n".join([
        f"제목: {article['title']}\n링크: {article['link']}\n요약: {article.get('summary', 'N/A')}"
        for article in articles
    ])

    prompt = f"""다음은 {source_name}의 최신 기술 뉴스입니다.

{articles_text}

위 기사들을 다음 형식으로 요약해주세요:

1. 오늘의 주요 트렌드 (2-3줄)
2. 각 기사별 핵심 요약 (기사당 1-2줄, 제목과 함께)
3. 주목할 만한 기술/회사 키워드

간결하고 읽기 쉽게 작성해주세요."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


# 기존 코드에 추가
if __name__ == "__main__":
    tc_articles = fetch_techcrunch()
    hn_articles = fetch_hackernews()

    print("=== TechCrunch AI 요약 ===")
    tc_summary = summarize_articles(tc_articles, "TechCrunch")
    print(tc_summary)

    print("\n\n=== Hacker News AI 요약 ===")
    hn_summary = summarize_articles(hn_articles, "Hacker News")
    print(hn_summary)