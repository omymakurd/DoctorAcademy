# zoom_integration/services.py
import jwt
import requests
import time
from django.conf import settings

class SecureZoomManager:
    def __init__(self):
        self.api_key = settings.ZOOM_API_KEY
        self.api_secret = settings.ZOOM_API_SECRET
        self.base_url = "https://api.zoom.us/v2"
    
    def generate_zoom_jwt(self):
        """إنشاء JWT token لـ Zoom API"""
        payload = {
            "iss": self.api_key,
            "exp": int(time.time()) + 3600
        }
        return jwt.encode(payload, self.api_secret, algorithm='HS256')
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.generate_zoom_jwt()}",
            "Content-Type": "application/json"
        }
    
    def create_secure_meeting(self, lecture):
        """إنشاء اجتماع آمن"""
        url = f"{self.base_url}/users/me/meetings"
        
        meeting_data = {
            "topic": f"{lecture.title} - {settings.PLATFORM_NAME}",
            "type": 2,
            "start_time": lecture.zoom_start_time.isoformat(),
            "duration": lecture.zoom_duration or 60,
            "timezone": "Asia/Riyadh",
            "settings": {
                "host_video": True,
                "participant_video": False,
                "join_before_host": False,
                "mute_upon_entry": True,
                "waiting_room": True,
                "auto_recording": "cloud",
                "private_meeting": True,
            }
        }
        
        response = requests.post(url, headers=self.get_headers(), json=meeting_data)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Zoom API Error: {response.text}")