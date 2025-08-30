from django.contrib import admin
from .models import Cart, CartItem

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'variant_name', 'quantity', 'is_active')

    def variant_name(self, obj):
        if obj.variations.exists():
            # Adjust these attribute names to match your Variation model
            return ", ".join([getattr(variation, 'name', '') for variation in obj.variations.all()])
        return '-'
    variant_name.short_description = 'Variants'

admin.site.register(Cart)
admin.site.register(CartItem, CartItemAdmin)

     


