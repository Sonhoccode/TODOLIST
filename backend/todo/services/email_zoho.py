import os
import requests

# Lấy env từ Railway / .env
ZOHO_CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = os.environ.get("ZOHO_REFRESH_TOKEN")
ZOHO_ACCOUNT_ID = os.environ.get("ZOHO_ACCOUNT_ID")
ZOHO_API_BASE = os.environ.get("ZOHO_API_BASE", "https://mail.zoho.com/api")
ZOHO_FROM_EMAIL = os.environ.get("ZOHO_FROM_EMAIL", "no-reply@hsonspace.id.vn")

# Region US nên dùng accounts.zoho.com
ZOHO_ACCOUNTS_BASE = os.environ.get("ZOHO_ACCOUNTS_BASE", "https://accounts.zoho.com")


def _get_access_token() -> str | None:
    """
    Dùng refresh_token để lấy access_token mỗi lần gửi mail.
    Nếu muốn tối ưu sau này có thể cache, còn giờ làm đơn giản cho dễ debug.
    """
    if not (ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET and ZOHO_REFRESH_TOKEN):
        print("[zoho_email] Thiếu CLIENT_ID / CLIENT_SECRET / REFRESH_TOKEN")
        return None

    url = f"{ZOHO_ACCOUNTS_BASE}/oauth/v2/token"
    data = {
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token",
    }

    resp = requests.post(url, data=data)
    if not resp.ok:
        print(f"[zoho_email] Lỗi lấy access_token: {resp.status_code} {resp.text}")
        return None

    js = resp.json()
    token = js.get("access_token")
    if not token:
        print("[zoho_email] Không thấy access_token trong response:", js)
    return token


def send_email(subject: str, text: str, to):
    """
    Gửi email qua Zoho Mail API.
    `to` có thể là string hoặc list email.
    """
    if isinstance(to, str):
        to = [to]

    if not ZOHO_ACCOUNT_ID:
        print("[zoho_email] Thiếu ZOHO_ACCOUNT_ID, không gửi mail được")
        return

    access_token = _get_access_token()
    if not access_token:
        return

    # Endpoint chuẩn: POST /api/accounts/{accountId}/messages
    url = f"{ZOHO_API_BASE}/accounts/{ZOHO_ACCOUNT_ID}/messages"

    payload = {
        "fromAddress": ZOHO_FROM_EMAIL,          # email gửi
        "toAddress": ",".join(to),               # list email nhận
        "subject": subject,
        "content": text,
        "mailFormat": "plaintext",               # theo docs: html | plaintext
    }

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    resp = requests.post(url, json=payload, headers=headers)
    if not resp.ok:
        print(f"[zoho_email] Lỗi gửi mail: {resp.status_code} {resp.text}")
        return False
    else:
        print("[zoho_email] Gửi mail OK:", resp.text)
        return True
