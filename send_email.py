import os
import django
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib
from datetime import timedelta
from django.utils import timezone

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'self_storage.settings')
django.setup()

from storageapp.models import Order, SentNotification

def get_notification_type(days_left):
    if days_left == 30:
        return '1_month'
    elif days_left == 14:
        return '2_weeks'
    elif days_left == 7:
        return '1_week'
    elif days_left == 3:
        return '3_days'
    elif days_left < 0:
        return 'expired'
    return None

def was_notification_sent(order, notification_type):
    return SentNotification.objects.filter(
        order=order,
        notification_type=notification_type
    ).exists()

def create_and_save_notification(order, notification_type):
    SentNotification.objects.create(
        order=order,
        notification_type=notification_type
    )

def send_email_notification(order, days_left):
    user_name = order.storage_user.first_name
    end_date = order.end_rental_date.strftime('%d.%m.%Y')
    box_number = order.box.number
    user_email = order.storage_user.email
    final_date = (order.end_rental_date + timedelta(days=180)).strftime('%d.%m.%Y')
    site_url = 'http://storage.azamat21x.space/'

    templates = {
        30: f"""Уважаемый {user_name},
Ваша аренда бокса №{box_number} истекает через 1 месяц ({end_date}).
Пожалуйста, зайдите в личный кабинет "{site_url}" или свяжитесь с нами.""",
        
        14: f"""Уважаемый {user_name},
Ваша аренда бокса №{box_number} истекает через 2 недели ({end_date}).
Пожалуйста, зайдите в личный кабинет "{site_url}" или свяжитесь с нами.""",
        
        7: f"""Уважаемый {user_name},
Ваша аренда бокса №{box_number} истекает через 1 неделю ({end_date}).
Пожалуйста, зайдите в личный кабинет "{site_url}" или свяжитесь с нами.""",
        
        3: f"""Уважаемый {user_name},
Ваша аренда бокса №{box_number} истекает через 3 дня ({end_date}).
Пожалуйста, зайдите в личный кабинет "{site_url}" или свяжитесь с нами.""",
        
        0: f"""\n
            Уважаемый {user_name},\n
            Ваша аренда бокса №{box_number} истекла {end_date}.\n
            Ваши вещи будут автоматически переведены на хранение по повышенному тарифу на 6 месяцев.\n
            Крайняя дата для вывоза вещей: {final_date}.\n
            Чтобы избежать дополнительных расходов и потери вещей:\n
            Продлите аренду в личном кабинете {site_url}.\n
            Заберите вещи до {final_date}.\n
            Свяжитесь с нами по телефону 8 (800) 000-00-00 для уточнения деталей.\n
            После {final_date} ваши вещи будут утилизированы без возможности восстановления."""
    }

    msg = EmailMessage()
    msg['From'] = os.getenv('YANDEX_MAIL')
    msg['To'] = user_email
    
    if days_left in templates:
        msg['Subject'] = 'Напоминание об окончании аренды'
        msg.set_content(templates[days_left])
    elif days_left < 0:
        msg['Subject'] = 'Ваша аренда просрочена!'
        msg.set_content(templates[0])

    with smtplib.SMTP_SSL('smtp.yandex.ru', 465) as server:
        server.login(os.getenv('YANDEX_MAIL'), os.getenv('YANDEX_PASSWORD'))
        server.send_message(msg)

def check_and_send_notifications():
    today = timezone.now().date()
    active_orders = Order.objects.filter(
        status__in=['В процессе', 'Доставка']
    ).select_related('storage_user', 'box')

    for order in active_orders:
        days_left = (order.end_rental_date - today).days
        notification_type = get_notification_type(days_left)
        
        if notification_type and not was_notification_sent(order, notification_type):
            send_email_notification(order, days_left)
            create_and_save_notification(order, notification_type)

if __name__ == "__main__":
    check_and_send_notifications()
