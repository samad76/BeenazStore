from django.db import models
from store.models import Product, Variation
from accounts.models import Accounts

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE, null=True, blank=True)
    cart_id = models.CharField(max_length=255, unique=True, )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart {self.cart_id} for {self.user.username}"
        return f"Cart {self.cart_id} (anonymous)"
    

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
    
    def price(self):
        if self.variations.exists():
            return sum(variation.price for variation in self.variations.all())
        else:
            return self.product.discounted_price if self.product.discounted_price else self.product.price

    def __str__(self):
        return f"Item {self.product.title} in Cart {self.cart.cart_id}"  