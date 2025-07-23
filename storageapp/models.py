from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


class StorageUser(AbstractUser):
    username = None
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        unique=True,
        verbose_name='адрес почты',
        )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    phone_number = PhoneNumberField(
        help_text='Номер телефона клиента')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Storage(models.Model):
    location = models.CharField(
        max_length=100,
        verbose_name='Локация',
    )
    available_boxes_count = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ],
        verbose_name='Боксов свободно',
    )
    total_boxes_count = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ],
        verbose_name='Всего боксов',
    )

    temperature = models.IntegerField(
        default=1,
    )
    height = models.IntegerField(
        default=1,
        verbose_name='Высота',
    )

    user = models.ManyToManyField(
        StorageUser,
        related_name='storages',
        verbose_name='Пользователи'
        )

    def __str__(self):
        return self.location
