from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgot-password/', views.forgot_password, name='forgotPassword'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('forgot-password/', views.forgot_password, name='forgotPassword'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_validate, name='resetPasswordValidate'),
    path('reset-password/', views.reset_password, name='resetPassword'),
    path('my-orders/', views.my_orders, name='myOrders'),
    path('edit-profile/', views.edit_profile, name='editProfile'),
    path('order-detail/<int:order_id>/', views.order_detail, name='orderDetail'),
    path('change-password/', views.change_password, name='change_password'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),  # --- IGNORE ---
]