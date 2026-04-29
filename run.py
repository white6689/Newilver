# run.py
from dotenv import load_dotenv
import os
from main.news_fetcher import fetch_techcrunch, fetch_hackernews
from main.summarizer import summarize_articles
from main.email_sender import send_email


def main():
    load_dotenv()
    recipient = os.environ.get("GMAIL_ADDRESS")

    print("📰 뉴스 수집 시작...")

    # 1. 뉴스 수집
    tc_articles = fetch_techcrunch()
    hn_articles = fetch_hackernews()

    print(f"✅ TechCrunch: {len(tc_articles)}건")
    print(f"✅ Hacker News: {len(hn_articles)}건")

    # 2. AI 요약 (각 소스별 1번씩 = 총 2번 API 호출)
    print("\n🤖 AI 요약 중...")

    tc_summary_text = summarize_articles(tc_articles, "TechCrunch")
    hn_summary_text = summarize_articles(hn_articles, "Hacker News")

    # 3. 이메일용 데이터 구조로 변환
    email_articles = []

    # TechCrunch 기사들 추가
    for article in tc_articles:
        email_articles.append({
            'source': 'TechCrunch',
            'title': article['title'],
            'url': article['link'],
            'summary': article.get('summary', '')[:200] + '...'  # 원문 요약 일부만
        })

    # Hacker News 기사들 추가
    for article in hn_articles:
        email_articles.append({
            'source': 'Hacker News',
            'title': article['title'],
            'url': article['link'],
            'summary': f"Score: {article.get('score', 'N/A')}"  # HN은 점수만
        })

    # 맨 앞에 AI 종합 요약 추가 (선택사항)
    email_articles.insert(0, {
        'source': '📊 오늘의 트렌드',
        'title': 'AI가 분석한 주요 트렌드',
        'url': '#',
        'summary': f"{tc_summary_text}\n\n{hn_summary_text}"
    })

    print(f"✅ 총 {len(email_articles)}건 준비 완료")

    # 4. 이메일 발송
    print("\n📧 이메일 발송 중...")
    send_email(email_articles, recipient)

    print("\n🎉 모든 작업 완료!")


if __name__ == "__main__":
    main()