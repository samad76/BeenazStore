from cart.views import _cart_id
from .models import Cart, CartItem

def counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = CartItem.objects.filter(cart=cart).count()
    else:
        cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        if cart:
            cart_count = CartItem.objects.filter(cart=cart).count()        
    return dict(cart_count=cart_count)