"""
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')

"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),


    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    path('employee_list', views.employee_list, name='employee_list'),
    path('employee_add', views.employee_add, name='employee_add'),
    path('remove_employee/<int:employee_id>', views.remove_employee, name='remove_employee'),

    path('register', views.register, name='register'),  # customer
    path('pet-register', views.pet, name='pet register'),
    path('customers', views.customers, name='customers'),

    path('search',views.search, name='search'),
    path('availability',views.availability, name='availability'),
    path('confirm_booking',views.confirm_booking, name='confirm_booking'),
    path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('download-receipt/<int:booking_id>/', views.download_receipt, name='download_receipt'),
    path('bookinglist', views.bookinglist, name='booking list'),
    path('services', views.services, name='services'),

    path('room', views.room_info, name='room'),
    path('add_room', views.add_room, name='add room'),
    path('remove_room', views.remove_room, name='remove room'),
    path('change_price', views.pricechange, name='price change'),

]
