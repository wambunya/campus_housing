from django.urls import path
from . import views

urlpatterns = [
    path('pay/mpesa/<int:listing_id>/', views.initiate_mpesa_payment, name='mpesa_payment'),
]