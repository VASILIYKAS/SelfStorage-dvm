from django.contrib import admin
from django.urls import path
from storageapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('boxes/', views.boxes, name='boxes'),
    path('faq/', views.faq, name='faq'),
    path('my-rent/', views.my_rent, name='my_rent'),
    path('my-rent-empty/', views.my_rent, name='my_rent_empty'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('logout/', views.logout_user, name='logout'),
    path('rent-box/<int:box_id>/', views.confirm_rental, name='rent_box'),
    path('open-box/<int:box_id>/', views.open_box, name='open_box'),
    path('my-items/', views.my_items, name='my_items'),
    path('my-items/<int:box_id>/', views.my_items, name='my_items_box'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
