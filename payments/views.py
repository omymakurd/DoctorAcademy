from django.shortcuts import render

# Create your views here.
import requests
from django.conf import settings
from django.http import JsonResponse

def create_checkout(request):
    url = "https://eu-test.oppwa.com/v1/checkouts"
    data = {
        "entityId": "8ac7a4ca8d038b3d018d13c3196c0e1c",  # هذا ممكن يختلف عندك، جبته من صفحة Iframes
        "amount": "20.00",
        "currency": "USD",
        "paymentType": "DB"
    }

    headers = {
        "Authorization": f"Bearer {settings.HYPERPAY_API_KEY}"
    }

    response = requests.post(url, data=data, headers=headers)
    return JsonResponse(response.json())
