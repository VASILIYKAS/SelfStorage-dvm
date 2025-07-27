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
from io import BytesIO
import phonenumbers
import random
import string
import qrcode
import base64


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
        storage_user=request.user,
        box__in=user_boxes,
        status__in=['В процессе', 'Доставка']
    ).select_related('box')

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

        delivery = request.POST.get('delivery') == 'on'
        address = request.POST.get(
            'address', '') if not delivery else None

        Order.objects.create(
            storage_user=request.user,
            box=box,
            rental_start_date=timezone.now(),
            end_rental_date=timezone.now() + timedelta(days=30),
            delivery=delivery,
            address=address
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
        phone_number = request.POST.get("PHONE_CREATE")
        password = request.POST.get("PASSWORD_CREATE")
        password_confirm = request.POST.get("PASSWORD_CONFIRM")

        normalized_phone = phonenumbers.parse(str(phone_number), "RU")
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
                phone_number=normalized_phone
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


@login_required
def open_box(request, box_id):
    box = Box.objects.get(id=box_id, user=request.user)

    alphabet = string.ascii_letters + string.digits
    key = ''.join(random.choice(alphabet) for _ in range(16))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(key)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_image = buffer.getvalue()
    qr_base64 = base64.b64encode(qr_image).decode('utf-8')

    order = Order.objects.filter(box=box, storage_user=request.user).first()

    if request.method == 'POST':
        if 'open_box' in request.POST:
            pass

        elif 'confirm_delivery' in request.POST:
            delivery = request.POST.get('delivery') == 'on'
            address = request.POST.get('address', '') if delivery else None

            if delivery and not address:
                messages.error(request, "Пожалуйста, укажите адрес доставки")
            else:
                if not order:
                    order = Order.objects.create(
                        storage_user=request.user,
                        box=box,
                        rental_start_date=timezone.now(),
                        end_rental_date=timezone.now() + timedelta(days=30),
                        delivery=delivery,
                        address=address,
                        status='Доставка' if delivery else 'В процессе'
                    )
                    messages.success(
                        request, "Заказ на доставку успешно оформлен!")
                else:
                    order.delivery = delivery
                    order.address = address
                    if delivery:
                        order.status = 'Доставка'
                    order.save()
                    messages.success(
                        request, "Информация о доставке обновлена!")

                return redirect('my_rent')

    if order and order.end_rental_date:
        delta = order.end_rental_date - timezone.now().date()
        days_left = delta.days
        time_left = f"Осталось {days_left} дней" if days_left > 0 else "Срок аренды истёк"
    else:
        time_left = ""

    return render(request, 'open_box.html', {
        'qr_image': qr_base64,
        'box': box,
        'order': order,
        'time_left': time_left,
        'current_date': timezone.now().date()
    })


def logout_user(request):
    logout(request)
    return redirect('index')
