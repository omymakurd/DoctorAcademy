from django.shortcuts import render

def home(request):
    # لو بدك تمرر بيانات لاحقًا مثل الكورسات أو الخدمات
    context = {
        "featured_courses": [
            {
                "title": "Anatomy Basics",
                "description": "Understand the fundamentals of human anatomy.",
                "image": "https://images.unsplash.com/photo-1588776814546-6a59b2e81533?auto=format&fit=crop&w=800&q=80",
                "link": "#"
            },
            {
                "title": "Clinical Case Studies",
                "description": "Analyze real-life medical cases for better understanding.",
                "image": "https://images.unsplash.com/photo-1588776814546-6a59b2e81533?auto=format&fit=crop&w=800&q=80",
                "link": "#"
            },
            {
                "title": "Pharmacology Essentials",
                "description": "Learn about drugs, dosages, and therapeutic uses.",
                "image": "https://images.unsplash.com/photo-1588776814546-6a59b2e81533?auto=format&fit=crop&w=800&q=80",
                "link": "#"
            }
        ]
    }
    return render(request, "home.html", context)
