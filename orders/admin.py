from django.contrib import admin
from .models import Payment, Order, OrderProduct

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    can_delete = False
    extra = 0   

# Register your models here.
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'amount_paid', 'status', 'created_at')
    search_fields = ('payment_id', 'user__email')
    list_filter = ('status', 'created_at')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'first_name', 'last_name', 'email', 'order_total', 'status', 'created_at')
    search_fields = ('order_number', 'user__email', 'first_name', 'last_name')
    list_filter = ('status', 'created_at')
    inlines = [OrderProductInline]

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'product_price', 'ordered', 'created_at')
    search_fields = ('order__order_number', 'product__title')
    list_filter = ('ordered', 'created_at')
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)