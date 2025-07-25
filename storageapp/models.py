from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Пожалуйста укажите почту')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class StorageUser(AbstractUser):
    username = None
    objects = CustomUserManager()
    photo = models.ImageField(
        upload_to='storage_images/',
        verbose_name='Фото',
        null=True,
        blank=True
    )
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
    date_joined = models.DateTimeField(
        auto_now_add=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    phone_number = PhoneNumberField(
        help_text='Номер телефона клиента',
        verbose_name='Номер телефона'
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Storage(models.Model):
    location = models.CharField(
        max_length=100,
        default='',
        verbose_name='Город',
    )
    adress = models.CharField(
        max_length=100,
        default='',
        verbose_name='Адрес'
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
        verbose_name='Температура'
    )
    image = models.ImageField(
        upload_to='storage_images/',
        verbose_name='Изображение склада',
        null=True,
        blank=True
    )
    height = models.IntegerField(
        default=1,
        verbose_name='Высота',
    )
    image = models.ImageField(
        upload_to='storage_images/',
        verbose_name='Изображение склада',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.location


class Order(models.Model):
    STATUS_CHOICES = [
        ('В процессе', 'В процессе'),
        ('Завершен', 'Завершен'),
        ('Отменен', 'Отменен'),
        ('Доставка', 'Доставка')
    ]

    status = models.CharField(
        default='В процессе',
        max_length=100,
        choices=STATUS_CHOICES,
        verbose_name='Статус'
    )

    rental_start_date = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name='Дата начала заказа'
    )
    end_rental_date = models.DateField(
        null=False,
        blank=False,
        verbose_name='Дата окончания заказа'
    )
    self_delivery = models.BooleanField(
        default=False
    )

    storage_user = models.ForeignKey(
        StorageUser,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Клиенты'
    )
    box = models.ForeignKey(
        'Box',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Арендованный бокс',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'Заказ пользователя {self.storage_user}'


class Box(models.Model):
    number = models.CharField(
        verbose_name='Номер бокса',
        unique=True
    )
    area = models.IntegerField(
        verbose_name='Площадь'
    )
    length = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='Длина'
    )
    width = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='Ширина'
    )
    height = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='Высота'
    )

    floor = models.IntegerField(
        default=0,
        verbose_name='Этаж'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    user = models.ForeignKey(
        StorageUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_boxes',
        verbose_name='Клиенты'
    )

    storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE,
        related_name='boxes',
        verbose_name='Склады'
    )

    def __str__(self):
        return f'Бокс {self.number}'


class UserItem(models.Model):
    area = models.IntegerField(
        verbose_name='Площадь'
    )
    length = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='Длина'
    )
    width = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='Ширина'
    )
    height = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='Высота'
    )
    user = models.ForeignKey(
        StorageUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='user_items',
        verbose_name='Вещи Клиента'
    )
    boxes = models.OneToOneField(
        Box,
        on_delete=models.CASCADE,
        related_name='box_items',
        verbose_name='Вещи ячейки'
    )

    def __str__(self):
        return f'Вещи клиента {self.user}'
