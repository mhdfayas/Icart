from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('products/', views.product_list, name='admin_product_list'),
    path('products/add/', views.add_product, name='admin_add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='admin_edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='admin_delete_product'),
    path('categories/', views.category_list, name='admin_category_list'),
    path('categories/add/', views.add_category, name='admin_add_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='admin_delete_category'),
    path('orders/', views.order_list, name='admin_order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='admin_order_detail'),
    path('orders/delete/<int:order_id>/', views.delete_order, name='admin_delete_order'),
    path('users/', views.user_list, name='admin_user_list'),
    path('users/delete/<int:user_id>/', views.delete_user, name='admin_delete_user'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='admin_edit_category'),
]