from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('choose/<int:order_id>/', views.choose_payment_method, name='choose_method'),
    path('pay/<int:order_id>/', views.paystack_payment, name='paystack_payment'),
    
    path('success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]
