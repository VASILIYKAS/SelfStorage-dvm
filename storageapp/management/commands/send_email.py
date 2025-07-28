from django.core.management.base import BaseCommand
from send_email import check_and_send_notifications

class Command(BaseCommand):
    help = 'Отправка уведомлений на почту'

    def handle(self, *args, **options):
        check_and_send_notifications()
        self.stdout.write(self.style.SUCCESS('Уведомление успешно отправлено'))