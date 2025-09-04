from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('contact/', views.contact_view, name='contact'),
    path('reserve/', views.reservation_view, name='reserve'),
    path('staff/reservations/', views.staff_reservations_view, name='staff_reservations'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('register/', views.register_view, name='register'),
    path('reservation/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('reservations/', views.reservation_view, name='reservation'),
    path('reservations/available-slots/', views.available_slots, name='available_slots'),
    path("thank-you/", views.thank_you, name="thank_you"),

]
