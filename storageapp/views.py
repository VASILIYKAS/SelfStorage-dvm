from .models import StorageUser
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test



def index(request):
    return render(request, 'index.html')


def boxes(request):
    return render(request, 'boxes.html')


def faq(request):
    return render(request, 'faq.html')


@login_required
def my_rent(request):
    return render(request, 'my-rent.html')


@login_required
def my_rent_empty(request):
    return render(request, 'my-rent-empty.html')


def register_user(request):
    if request.method == "POST":
        email = request.POST.get("EMAIL_CREATE")
        password = request.POST.get("PASSWORD_CREATE")
        password_confirm = request.POST.get("PASSWORD_CONFIRM")

        if password != password_confirm:
            messages.error(request, "Пароли не совпадают")
            return redirect("index")

        if StorageUser.objects.filter(email=email).exists():
            messages.error(
                request, "Пользователь с таким email уже существует")
            return redirect("index")

        try:
            user = StorageUser.objects.create_user(
                email=email,
                password=password,
                first_name="",
                last_name="",
                phone_number=""
            )
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("my_rent")
        except Exception as e:
            messages.error(request, f"Ошибка регистрации: {str(e)}")
            return redirect("index")

    return render(request, "index.html")


def login_user(request):
    if request.method == "POST":
        email = request.POST.get("EMAIL")
        password = request.POST.get("PASSWORD")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("my_rent")
        else:
            messages.error(request, "Неверный email или пароль")
            return redirect("index")

    return render(request, "index.html")
