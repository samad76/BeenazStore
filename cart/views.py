from itertools import product
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation, ColorVariant, SizeVariant, FlavorVariant
from .models import Cart, CartItem
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variations = []

    if request.method == "POST":
        for key in ['color', 'size', 'flavor']:
            value = request.POST.get(key)
            if value:
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_type__iexact=key,
                        id__iexact=value
                    )
                    product_variations.append(variation)
                except Variation.DoesNotExist:
                    pass
    if product.variations.exists() and not product_variations:
        messages.warning(request, "Please select a variant before adding to cart.")
        return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)

    user = request.user if request.user.is_authenticated else None

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request), user=user)

    # Check for existing cart item with same product and variations
    cart_items = CartItem.objects.filter(product=product, cart=cart)
    for item in cart_items:
        if set(item.variations.all()) == set(product_variations):
            item.quantity += 1
            item.save()
            break
    else:
        # No match found, create new item with quantity = 1
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
        if product_variations:
            cart_item.variations.set(product_variations)
        cart_item.save()

    return redirect('cart')

def cart(request, total=0, quantity=0, item_price=0, cart_item=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            item_price = 0
            if item.variations.exists():
                
                for variation in item.variations.all():
                    total += variation.price * item.quantity
                    item_price = variation.price if variation.price else 0
                
            else:
                total += item.product.discounted_price * item.quantity
                item_price = item.product.discounted_price
            quantity += item.quantity
        tax = (total * 18)/100
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass
    context = {
        'item_price': item_price,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context)


def less_to_cart(request, product_id, cart_item_id):
    # Logic to decrease the quantity of the product in the cart
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass
    return redirect('cart')

def remove_from_cart(request, product_id, cart_item_id):
    # Logic to remove the product from the cart
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
        cart_item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass
    return redirect('cart')



def checkout(request):
    # Logic for checkout
    return render(request, 'store/checkout.html')
