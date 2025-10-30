# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User, StudentProfile, InstructorProfile, CourseProviderProfile

def auth_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # =========================
        # تسجيل دخول
        # =========================
        if action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")

            # السماح بتسجيل الدخول بالـ username أو الـ email
            user = authenticate(request, username=username, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user:
                login(request, user)
                messages.success(request, "Welcome back!")

                # تحويل حسب الدور
                if user.role == "instructor":
                    return redirect("instructor_dashboard")
                elif user.role == "student":
                    return redirect("student_dashboard")
                elif user.role == "course_provider":
                    return redirect("courses:course_provider_dashboard")
                else:
                    return redirect("home")
            else:
                messages.error(request, "Invalid credentials. Please try again.")

        # =========================
        # إنشاء حساب
        # =========================
        elif action == "signup":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            role = request.POST.get("role")

            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                return redirect("auth")

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect("auth")

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect("auth")

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                role=role,
            )

            # إنشاء البروفايل حسب الدور
            if role == "student":
                StudentProfile.objects.create(user=user)
            elif role == "instructor":
                InstructorProfile.objects.create(user=user)
            elif role == "course_provider":
                CourseProviderProfile.objects.create(user=user)

            messages.success(request, "Account created successfully.")

            # تحويل المستخدم حسب الدور
            login(request, user)
            if role == "instructor":
                return redirect("instructor_dashboard")
            elif role == "student":
                return redirect("student_dashboard")
            elif role == "course_provider":
                return redirect("courses:course_provider_dashboard")

            else:
                return redirect("home")

    return render(request, "auth.html",{})


def logout_view(request):
    """
    تسجيل خروج المستخدم
    """
    logout(request)
    messages.info(request, "👋 You have been logged out.")
    return redirect('auth')
