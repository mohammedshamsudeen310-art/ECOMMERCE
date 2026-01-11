from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path("paystack/<int:order_id>/", views.paystack_page, name="paystack_page"),
    path("paystack/<int:order_id>/init/", views.paystack_payment, name="paystack_payment"),
    path("verify/", views.paystack_verify, name="paystack_verify"),
    
    path('success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]
