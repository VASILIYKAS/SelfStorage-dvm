from django.contrib.auth import get_user_model
from self_storage.models import Storage, Box, Order, UserItem
from phonenumber_field.phonenumber import PhoneNumber
from datetime import datetime, timedelta
from decimal import Decimal

# Get the custom user model
StorageUser = get_user_model()

# Create test users
users_data = [
    {
        'email': 'user1@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'phone_number': PhoneNumber.from_string('+79161234567'),
        'password': 'password123'
    },
    {
        'email': 'user2@example.com',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'phone_number': PhoneNumber.from_string('+79161234568'),
        'password': 'password123'
    },
    {
        'email': 'admin@example.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'phone_number': PhoneNumber.from_string('+79161234569'),
        'password': 'admin123',
        'is_staff': True,
        'is_superuser': True
    }
]

for user_data in users_data:
    if not StorageUser.objects.filter(email=user_data['email']).exists():
        if user_data.get('is_superuser'):
            StorageUser.objects.create_superuser(
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone_number=user_data['phone_number']
            )
        else:
            StorageUser.objects.create_user(
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone_number=user_data['phone_number']
            )
        print(f"Created user: {user_data['email']}")

# Create test storages
storages_data = [
    {
        'location': 'Одинцово',
        'adress': 'ул. Центральная, д. 10',
        'condition': 'Сухой, отапливаемый',
        'available_boxes_count': 15,
        'total_boxes_count': 20,
        'temperature': 20,
        'height': 3
    },
    {
        'location': 'Пушкино',
        'adress': 'ул. Лесная, д. 5',
        'condition': 'Сухой',
        'available_boxes_count': 10,
        'total_boxes_count': 15,
        'temperature': 18,
        'height': 2
    },
    {
        'location': 'Люберцы',
        'adress': 'ул. Солнечная, д. 3',
        'condition': 'Отапливаемый',
        'available_boxes_count': 8,
        'total_boxes_count': 10,
        'temperature': 22,
        'height': 3
    },
    {
        'location': 'Домодедово',
        'adress': 'ул. Южная, д. 7',
        'condition': 'Сухой, вентилируемый',
        'available_boxes_count': 12,
        'total_boxes_count': 18,
        'temperature': 19,
        'height': 2
    }
]

for storage_data in storages_data:
    if not Storage.objects.filter(location=storage_data['location']).exists():
        storage = Storage.objects.create(**storage_data)
        print(f"Created storage: {storage.location}")

# Create test boxes
boxes_data = [
    {'storage': 'Одинцово', 'number': 'OD1', 'area': 2, 'length': Decimal('2.0'), 'width': Decimal(
        '1.0'), 'height': Decimal('2.0'), 'floor': 1, 'price': Decimal('5000.00')},
    {'storage': 'Одинцово', 'number': '2', 'area': 5, 'length': Decimal('2.5'), 'width': Decimal(
        '2.0'), 'height': Decimal('2.5'), 'floor': 2, 'price': Decimal('1200.00')},
    {'storage': 'Одинцово', 'number': '3', 'area': 12, 'length': Decimal('4.0'), 'width': Decimal('3.0'), 'height': Decimal('3.0'), 'floor': 1', 'price': Decimal('3000.00')},
    {'storage': 'Пушкино', 'number': 'PU1', 'area': '2', 'length': Decimal('2.0'), 'width': Decimal(
        '1.0'), 'height': Decimal('2.0'), 'floor': '1', 'price': Decimal('4500.00')},
    {'storage': 'Пушкино', 'number': '2', 'area': '6', 'length': Decimal('3.0'), 'width': Decimal('2.0'), 'height': Decimal('2.0'), 'floor': '2', 'price': Decimal('7000')}, 00'),
    {'storage': 'Люберцы', 'number': 'LU1', 'area': '3', 'length': Decimal('2.0'), 'width': Decimal(
        '1.5'), 'height': Decimal('2.0'), 'floor': '1', 'price': Decimal('5500.00')},
    {'storage': 'Люберцы', 'number': '2', 'area': '8', 'length': Decimal('2.5'), 'width': Decimal(
        '2.0'), 'height': Decimal('2.5'), 'floor': '2', 'price': Decimal('9000.00')},
    {'storage': 'Домодедово', 'number': 'DO1', 'area': '4', 'length': Decimal('2.0'), 'width': Decimal(
        '2.0'), 'height': Decimal('2.0'), 'floor': '1', 'price': Decimal('6000.00')},
    {'storage': 'Домодедово', 'number': '2', 'area': '10', 'length': Decimal('3.0'), 'width': Decimal(
        '2.5'), 'height': Decimal('2.5'), 'floor': '2', 'price': Decimal('1100.00')},
]

user1= StorageUser.objects.get(email='user1@example.com')
user2= StorageUser.objects.get(email='user2@example.com')

for box_data in boxes_data:
    storage= Storage.objects.get(location=box_data['storage'])
    box_number= box_data['number']
    if not Box.objects.filter(number=box_data['number'], storage=storage).exists():
        box= Box.objects.create(
            number=box_data['number'],
            area=box_data['area'],
            length=box_data['length'],
            width=box_data['width'],
            height=box_data['height'],
            floor=box_data['floor'],
            price=box_data['price'],
            storage=storage,
            user=None  # Initially unrented
        )
        print(f"Created box: {box.number} in {storage.location}")

# Assign some boxes to users
box_od1= Box.objects.get(number='OD1', storage__location='Одинцово')
box_od1.user= user1
box_od1.save()

box_pu1= Box.objects.get(number='PU1', storage__location='Пушкино')
box_pu1.user= user2
box_pu1.save()

# Update available_boxes_count for storages
for storage in Storage.objects.all():
    storage.available_boxes_count= storage.boxes.filter(user__isnull=True).count()
    storage.save()
    print(
        f"Updated storage {storage.location}: {storage.available_boxes_count} available boxes")

# Create test orders
orders_data= [
    {
        'status': 'В процессе',
        'rental_start_date': datetime.now(),
        'end_rental_date': datetime.now().date() + timedelta(days=30),
        'self_delivery': False,
        'storage_user': user1
    },
    {
        'status': 'Доставка',
        'rental_start_date': datetime.now(),
        'end_rental_date': datetime.now().date() + timedelta(days=60),
        'self_delivery': True,
        'storage_user': user2
    }
]

for order_data in orders_data:
    if not Order.objects.filter(
        storage_user=order_data['storage_user'],
        rental_start_date__date=order_data['rental_start_date'].date()
    ).exists():
        Order.objects.create(**order_data)
        print(f"Created order for {order_data['storage_user'].email}")

# Create test user items
user_items_data= [
    {
        'area': 2,
        'length': Decimal('2.0'),
        'width': Decimal('1.0'),
        'height': Decimal('2.0'),
        'user': user1,
        'box': box_od1
    },
    {
        'area': 2,
        'length': Decimal('2.0'),
        'width': Decimal('1.0'),
        'height': Decimal('2.0'),
        'user': user2,
        'box': box_pu1
    }
]

for item_data in user_items_data:
    if not UserItem.objects.filter(box=item_data['box']).exists():
        UserItem.objects.create(
            area=item_data['area'],
            length=item_data['length'],
            width=item_data['width'],
            height=item_data['height'],
            user=item_data['user'],
            boxes=item_data['box']
        )
        print(f"Created user item for box {item_data['box'].number}")
