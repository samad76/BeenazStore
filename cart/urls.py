from django.urls import path
from . import views
urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('less/<int:product_id>/<int:cart_item_id>/', views.less_to_cart, name='less_to_cart'),
    path('checkout/', views.checkout, name='checkout'),

]