# zoom_utils.py
import os
import time
import base64
import hmac
import hashlib
import requests
from django.conf import settings
from datetime import datetime, timezone

# ---------- Token (Account-level OAuth) ----------
def get_zoom_token():
    token_url = "https://zoom.us/oauth/token"
    data = {
        "grant_type": "account_credentials",
        "account_id": settings.ZOOM_ACCOUNT_ID
    }
    auth = (settings.ZOOM_CLIENT_ID, settings.ZOOM_CLIENT_SECRET)
    response = requests.post(token_url, data=data, auth=auth)
    response.raise_for_status()
    return response.json()["access_token"]

# ---------- Create meeting (server creates and controls settings) ----------
def create_zoom_meeting(topic, start_time, duration=120):
    token = get_zoom_token()
    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "topic": topic,
        "type": 2,  # scheduled meeting
        "start_time": start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration": duration,
        "settings": {
            "host_video": True,
            "participant_video": True,
            "waiting_room": True,
            "join_before_host": False,
            "auto_recording": "cloud",
            "private_meeting": True,
            "allow_participants_invite": False,
            "meeting_authentication": True,
            "approval_type": 2  # enable waiting room/approval flow
        }
    }
    response = requests.post(url, json=body, headers=headers)
    response.raise_for_status()
    return response.json()

# ---------- Generate SDK Signature (server-side) ----------
# This implementation uses HMAC-SHA256 like many Zoom SDK examples:
def generate_zoom_signature(meeting_number: str, role: int = 0):
    """
    Returns signature string to be used by ZoomMtgEmbedded.join(...)
    meeting_number: string or int
    role: 0 for attendee, 1 for host
    """
    api_key = settings.ZOOM_SDK_KEY
    api_secret = settings.ZOOM_SDK_SECRET
    ts = int(round(time.time() * 1000)) - 30000
    msg = f"{api_key}{meeting_number}{ts}{role}"
    message = msg.encode('utf-8')
    secret = api_secret.encode('utf-8')
    hash = hmac.new(secret, message, hashlib.sha256).digest()
    hash_b64 = base64.b64encode(hash).decode('utf-8')
    raw_signature = f"{api_key}.{meeting_number}.{ts}.{role}.{hash_b64}"
    signature = base64.b64encode(raw_signature.encode("utf-8")).decode("utf-8")
    return signature
