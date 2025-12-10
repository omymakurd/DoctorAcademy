from .models import Notification, AdminDevice
from users.models import User
from firebase_admin import messaging

def notify_admins(title, message):
    """
    دالة لإرسال إشعار داخلي + إشعار فوري للأدمنين
    """

    # 1️⃣ In-App Notification
    for admin in User.objects.filter(is_staff=True):
        Notification.objects.create(
            recipient=admin,
            title=title,
            message=message
        )

    # 2️⃣ FCM Notification
    for device in AdminDevice.objects.all():
        msg = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message
            ),
            token=device.fcm_token
        )
        try:
            messaging.send(msg)
        except Exception as e:
            print(f"Error sending FCM to {device.user.username}: {e}")
