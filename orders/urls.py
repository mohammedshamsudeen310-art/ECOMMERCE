from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('my-orders/', views.orders_list_view, name='orders_list'),
    path('cancel/<int:order_id>/', views.cancel_order_view, name='cancel_order'),
]
