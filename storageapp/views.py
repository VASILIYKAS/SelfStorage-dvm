from datetime import timedelta
from django.utils import timezone
from .models import Storage, Box, Order
from .models import StorageUser
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from phonenumber_field.phonenumber import PhoneNumber
from .models import StorageUser, Storage, Box, Order


def index(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Юзать имейл юзера, если он уже в бд
            email = request.user.email
            request.session['user_email'] = email
            return HttpResponseRedirect('/boxes/#rent_boxes')
        else:
            email1 = request.POST.get('EMAIL1')
            email2 = request.POST.get('EMAIL2')
            email = email1 if email1 else email2
            if email:
                request.session['user_email'] = email
                return HttpResponseRedirect('/boxes/#rent_boxes')
            else:
                messages.error(request, "Пожалуйста, укажите ваш email")
                return redirect('index')
    return render(request, 'index.html')


def boxes(request):
    storages = Storage.objects.all()
    boxes = Box.objects.filter(user__isnull=True)
    boxes_to3 = boxes.filter(area__lte=3)
    boxes_to10 = boxes.filter(area__gt=3, area__lte=10)
    boxes_from10 = boxes.filter(area__gt=10)

    return render(request, 'boxes.html', {
        'storages': storages,
        'boxes': boxes,
        'boxes_to3': boxes_to3,
        'boxes_to10': boxes_to10,
        'boxes_from10': boxes_from10,
    })


def faq(request):
    return render(request, 'faq.html')


@login_required
def my_rent(request):
    user_boxes = Box.objects.filter(
        user=request.user).select_related('storage')
    user_orders = Order.objects.filter(
        storage_user=request.user).prefetch_related('storage_user')

    return render(request, 'my-rent.html', {
        'user_boxes': user_boxes,
        'user_orders': user_orders,
    })


def confirm_rental(request, box_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        box = Box.objects.get(id=box_id, user__isnull=True)
    except Box.DoesNotExist:
        messages.error(request, "Этот бокс уже занят или не существует")
        return redirect('boxes')

    if request.method == 'POST':
        box.user = request.user
        box.save()
        Order.objects.create(
            storage_user=request.user,
            box=box,
            rental_start_date=timezone.now(),
            end_rental_date=timezone.now() + timedelta(days=30),
            self_delivery=request.POST.get('self_delivery', False)
        )

        messages.success(request, "Бокс успешно арендован!")
        return redirect('my_rent')
    return render(request, 'confirm_rental.html', {'box': box})


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
            return redirect("register")

        if StorageUser.objects.filter(email=email).exists():
            messages.error(
                request, "Пользователь с таким email уже существует")
            return redirect("register")

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
            return redirect("register")

    return render(request, "authorization/register.html")


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
            return redirect("login")

    return render(request, "authorization/login.html")


@login_required
def update_profile(request):
    if request.method == "POST":
        first_name = request.POST.get("FIRST_NAME")
        last_name = request.POST.get("LAST_NAME")
        email = request.POST.get("EMAIL_EDIT")
        phone_number = request.POST.get("PHONE_EDIT")
        password = request.POST.get("PASSWORD_EDIT")

        user = request.user

        try:
            if email != user.email and StorageUser.objects.filter(email=email).exists():
                messages.error(
                    request, "Пользователь с таким email уже существует")
                return redirect("my_rent")

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            if phone_number:
                user.phone_number = PhoneNumber.from_string(
                    phone_number, region='RU')
            if password and password != "********":
                user.set_password(password)
            user.save()

            if email != request.user.email or (password and password != "********"):
                user = authenticate(request, email=email, password=password if password and password !=
                                    "********" else request.POST.get("PASSWORD"))
                if user is not None:
                    login(request, user)

            messages.success(request, "Профиль успешно обновлен!")
            return redirect("my_rent")
        except Exception as e:
            messages.error(request, f"Ошибка при обновлении профиля: {str(e)}")
            return redirect("my_rent")

    return redirect("my_rent")


def logout_user(request):
    logout(request)
    return redirect('index')
