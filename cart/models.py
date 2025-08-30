from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from store.models import Product, Variation

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart_id = models.CharField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.cart_id} for {self.user.username}"
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        if self.variations.exists():
            return sum(variation.price * self.quantity for variation in self.variations.all())
        return self.product.discounted_price * self.quantity
    
    def __str__(self):
        return f"Item {self.product.title} in Cart {self.cart.cart_id}"  