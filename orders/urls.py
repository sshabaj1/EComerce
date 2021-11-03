from django.urls import path
from . import views


app_name = 'orders'

urlpatterns = [
    path('admin/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('create/', views.order_create, name='order_create'),
]
