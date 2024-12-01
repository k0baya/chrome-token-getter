import json
import time
import os
from fastapi import APIRouter, HTTPException, Request
from utils.configs import api_prefix
import base64
import hashlib
import requests
from urllib.parse import urlencode
import utils.globals as globals

router = APIRouter()

def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('=')

def generate_code_challenge(code_verifier):
    m = hashlib.sha256()
    m.update(code_verifier.encode())
    return base64.urlsafe_b64encode(m.digest()).decode().rstrip('=')

def get_preauth_cookie():
    try:
        with open(globals.PREAUTH_FILE, 'r') as f:
            data = json.load(f)
        preauth_cookie = data.get('preauth_cookie')
        expires_at = data.get('expires_at', 0)
        if preauth_cookie and time.time() < expires_at:
            return preauth_cookie
    except (IOError, json.JSONDecodeError):
        pass

    # Existing request logic
    device_token = os.getenv('DEVICE_TOKEN')
    if device_token:
        rsp = requests.post(
            'https://ios.chat.openai.com/backend-api/preauth_devicecheck',
            json={
                "bundle_id": "com.openai.chat",
                "device_id": "62345678-042E-45C7-962F-AC725D0E7770",
                "device_token": device_token,
                "request_flag": True
            }
        )
        if rsp.status_code == 200 and rsp.json().get('is_ok'):
            new_preauth = rsp.cookies.get('_preauth_devicecheck')
            if new_preauth:
                with open(preauth_path, 'w') as f:
                    json.dump({'preauth_cookie': new_preauth, 'expires_at': time.time() + 3600}, f)
                return new_preauth
    return None

def fetch_identifier_url():
    BASE_URL = os.getenv('APPLE_LOGIN_URL', 'https://auth0.openai.com')
    PREAUTH = get_preauth_cookie()
    if not PREAUTH:
        return {"u": None, "d": None, "v": None}
    
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    params = {
        "client_id": "pdlLIX2Y72MIl2rhLhTE9VV9bN905kBh",
        "audience": "https://api.openai.com/v1",
        "redirect_uri": "com.openai.chat://auth0.openai.com/ios/com.openai.chat/callback",
        "scope": "openid email profile offline_access model.request model.read organization.read offline",
        "response_type": "code",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "preauth_cookie": PREAUTH,
        "prompt": "login"
    }

    origin_url = f"{BASE_URL}/authorize?{urlencode(params)}"
    
    headers = {
        'authority': 'auth0.openai.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh,en;q=0.9,zh-CN;q=0.8',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Chromium";v="118"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    }

    try:
        response = requests.get(origin_url, headers=headers, allow_redirects=False)
        if response.status_code == 302:
            location = response.headers.get('Location')
            auth0_cookie = response.cookies.get('auth0')

            if location and auth0_cookie:
                return {"u": "https://auth0.openai.com" + location, "d": auth0_cookie, "v": code_verifier}
    except requests.RequestException:
        pass

    return {"u": None, "d": None, "v": None}

@router.get(f"/{api_prefix}/auth/url" if api_prefix else "/auth/url")
async def get_auth_url():
    return fetch_identifier_url()

@router.post(f"/{api_prefix}/auth/session" if api_prefix else "/auth/session")
async def post_auth_session(request: Request):
    data = await request.json()
    location = data.get('location')
    code_verifier = data.get('codeVerifier')
    
    if not location or not code_verifier:
        return {"error": "Invalid data"}

    # Extract 'code' from the location URL
    try:
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(location)
        code = parse_qs(parsed_url.query).get('code')
        if not code:
            return {"error": "Code not found in location"}
        code = code[0]
    except Exception:
        return {"error": "Failed to parse location URL"}

    # Request session information without using proxies
    try:
        BASE_URL = os.getenv('APPLE_LOGIN_URL', 'https://auth0.openai.com')
        token_url = f"{BASE_URL}/oauth/token"
        resp_json = requests.post(token_url, json={
            'redirect_uri': 'com.openai.chat://auth0.openai.com/ios/com.openai.chat/callback',
            'grant_type': 'authorization_code',
            'client_id': 'pdlLIX2Y72MIl2rhLhTE9VV9bN905kBh',
            'code': code,
            'code_verifier': code_verifier
        }).json()
        refresh_token = resp_json.get('refresh_token')
        if refresh_token:
            with open(globals.TOKENS_FILE, "a", encoding="utf-8") as f:
                f.write(refresh_token + "\n")
        return resp_json
    except requests.RequestException:
        return {"error": "Failed to retrieve session information"}