# main/email_sender.py
import os
import base64
import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    load_dotenv()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
    TOKEN_PATH = os.path.join(BASE_DIR, "token.json")  # 로컬 저장용

    creds = None

    # 1. 로컬 token.json 파일이 있으면 로드
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    # 2. 환경변수에서 토큰 로드 (GitHub Actions용)
    elif os.environ.get("GMAIL_TOKEN_JSON"):
        token_json = os.environ.get("GMAIL_TOKEN_JSON")
        creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)

    # 토큰 만료 시 자동 갱신
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # 갱신된 토큰 저장
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    # 토큰이 없으면 최초 인증
    elif not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(
                f"credentials.json 파일이 없습니다!\n"
                f"경로: {CREDENTIALS_PATH}\n"
                f"Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고\n"
                f"credentials.json 파일을 다운로드해서 main/ 폴더에 넣어주세요."
            )

        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=8080)

        # 토큰 저장
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

        print("\n✅ 인증 완료!")
        print("=== GitHub Secret용 토큰 (복사해서 GMAIL_TOKEN_JSON에 저장) ===")
        print(creds.to_json())
        print("=" * 60)

    return build("gmail", "v1", credentials=creds)


def build_html(articles: list[dict]) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    count = len(articles)

    article_blocks = ""
    for i, a in enumerate(articles, 1):
        article_blocks += f"""
        <div style="margin-bottom:32px; padding-bottom:24px; border-bottom:1px solid #eee;">
            <p style="color:#888; font-size:12px; margin:0 0 4px;">
                {i}. {a.get('source', '')} &nbsp;·&nbsp;
                <a href="{a['url']}">원문 링크</a>
            </p>
            <h2 style="margin:0 0 8px; font-size:18px;">{a['title']}</h2>
            <p style="margin:0; line-height:1.7; color:#333;">{a['summary']}</p>
        </div>
        """

    return f"""
    <html><body style="font-family:sans-serif; max-width:680px; margin:auto; padding:24px; color:#222;">
        <div style="background:#0f172a; color:white; padding:20px 24px; border-radius:8px; margin-bottom:28px;">
            <h1 style="margin:0; font-size:22px;">📰 Newilver Daily</h1>
            <p style="margin:6px 0 0; color:#94a3b8;">{date_str} &nbsp;·&nbsp; 기사 {count}건</p>
        </div>
        {article_blocks}
        <p style="color:#aaa; font-size:12px; text-align:center; margin-top:32px;">
            Newilver · 자동 발송 · 매일 08:00 KST
        </p>
    </body></html>
    """


def send_email(articles: list[dict], recipient: str):
    service = get_gmail_service()
    date_str = datetime.now().strftime("%Y-%m-%d")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Newilver] {date_str} 기술 뉴스"
    msg["From"] = recipient
    msg["To"] = recipient
    msg.attach(MIMEText(build_html(articles), "html"))

    encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(
        userId="me", body={"raw": encoded}
    ).execute()

    print(f"✅ 이메일 발송 완료: {date_str}")

if __name__ == "__main__":
    get_gmail_service()