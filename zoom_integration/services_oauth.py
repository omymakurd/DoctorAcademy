import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ZoomServiceOAuth:
    def __init__(self):
        self.base_url = "https://api.zoom.us/v2"
        self.access_token = self.get_oauth_token()
    
    def get_oauth_token(self):
        """الحصول على token باستخدام OAuth"""
        url = "https://zoom.us/oauth/token"
        
        try:
            response = requests.post(
                url,
                auth=(settings.ZOOM_CLIENT_ID, settings.ZOOM_CLIENT_SECRET),
                data={
                    'grant_type': 'account_credentials', 
                    'account_id': settings.ZOOM_ACCOUNT_ID
                },
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                logger.info("✅ تم الحصول على Zoom OAuth token بنجاح")
                return token_data['access_token']
            else:
                error_msg = f"فشل في الحصول على OAuth token: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"خطأ في الاتصال ب Zoom OAuth: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def create_meeting(self, topic, start_time, duration):
        """إنشاء اجتماع - متوافق مع JavaScript الحالي"""
        url = f"{self.base_url}/users/me/meetings"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'topic': f"دكتور أكاديمي - {topic}",
            'type': 2,  # scheduled meeting
            'start_time': start_time,  # يجب أن يكون بتنسيق "2025-10-26T10:00:00"
            'duration': int(duration),
            'timezone': 'Asia/Riyadh',
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': False,
                'mute_upon_entry': True,
                'waiting_room': True,
                'auto_recording': 'cloud',
                'private_meeting': True,
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 201:
                meeting_data = response.json()
                logger.info(f"✅ تم إنشاء اجتماع Zoom: {meeting_data['id']}")
                return meeting_data
            else:
                error_msg = f"فشل في إنشاء الاجتماع: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"خطأ في إنشاء الاجتماع: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)