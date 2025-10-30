# zoom_integration/utils.py
import base64
import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

ZOOM_TOKEN_CACHE_KEY = "zoom_s2s_access_token"
ZOOM_BASE_URL = "https://api.zoom.us/v2"

def get_zoom_access_token():
    cached = cache.get(ZOOM_TOKEN_CACHE_KEY)
    if cached:
        return cached

    url = "https://zoom.us/oauth/token"
    params = {"grant_type": "account_credentials", "account_id": settings.ZOOM_ACCOUNT_ID}
    creds = f"{settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}"
    auth_header = base64.b64encode(creds.encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}

    response = requests.post(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()

    data = response.json()
    token = data["access_token"]
    expires_in = data.get("expires_in", 3500)
    cache.set(ZOOM_TOKEN_CACHE_KEY, token, timeout=expires_in - 60)
    return token


def create_zoom_meeting_for_lecture(lecture):
    """
    Creates a Zoom meeting for a given lecture (Basic or Clinical).
    Auto-fills zoom fields in DB.
    """
    token = get_zoom_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    start_iso = None
    if lecture.zoom_start_time:
        start_utc = lecture.zoom_start_time.astimezone(timezone.utc)
        start_iso = start_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "topic": lecture.title or "Lecture Meeting",
        "type": 2 if start_iso else 1,
        "start_time": start_iso,
        "duration": lecture.zoom_duration or 60,
        "timezone": "Africa/Cairo",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "waiting_room": True,
            "approval_type": 0,
            "join_before_host": False
        }
    }

    response = requests.post(f"{ZOOM_BASE_URL}/users/me/meetings", headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    data = response.json()

    # ✅ تخزين النتائج في المحاضرة
    lecture.zoom_meeting_id = data.get("id")
    lecture.zoom_link = data.get("join_url")
    lecture.zoom_join_url = data.get("join_url")
    lecture.zoom_start_url = data.get("start_url")
    lecture.save(update_fields=['zoom_meeting_id', 'zoom_link', 'zoom_join_url', 'zoom_start_url'])

    return data
