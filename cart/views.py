from itertools import product
from urllib import request
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from store.models import Product, Variation, ColorVariant, SizeVariant, FlavorVariant
from .models import Cart, CartItem
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart

def get_or_create_cart(request):
    user = request.user if request.user.is_authenticated else None
    cart_id = _cart_id(request)
       
    if user:
        cart, created = Cart.objects.get_or_create(
            cart_id=cart_id,
            defaults={'user': user}
        )
    else:
        cart, created = Cart.objects.get_or_create(
            cart_id=cart_id,
            defaults={'user': None}
        )
    return cart



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(product=product, cart=cart)
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

   
    # Try to find a cart item with the same variations
    for item in cart_items:
        if set(item.variations.all()) == set(product_variations):
         # Same variations found, increment quantity
          item.quantity += 1
          item.save()
          break
    else:
        # No matching item found, create a new one
        cart_item = CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=1
        )
        if product_variations:
            cart_item.variations.set(product_variations)
        cart_item.save()
    
    return redirect('cart')






def cart(request, total=0, quantity=0, item_price=0, cart_item=None):
    cart_items = []
    try:
        cart = Cart.objects.filter(user=request.user if request.user.is_authenticated else None).first()
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            if item.variations.exists():
                for variation in item.variations.all():
                    total += variation.price * item.quantity    
            else:
                total += item.product.discounted_price * item.quantity
                
            quantity += item.quantity
        tax = (total * 18)/100
        grand_total = total + tax
    except Cart.DoesNotExist:
        cart_items = []
        total = 0
        quantity = 0
        tax = 0
        grand_total = 0
    context = {
        
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context)


def less_to_cart(request, cart_item_id):
    # Logic to decrease the quantity of the product in the cart
    try:
        cart = Cart.objects.get(user=request.user if request.user.is_authenticated else None)
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
        cart = Cart.objects.get(user=request.user if request.user.is_authenticated else None)
        cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
        cart_item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass
    return redirect('cart')


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, item_price=0, cart_item=None):
    cart_items = []
    grand_total = 0
    tax = 0      
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:   
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
        cart_items = []
        total = 0
        quantity = 0
        tax = 0
        grand_total = 0
    context = {
        'item_price': item_price,
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/checkout.html', context)

def buy_now(request, product_id):
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
        messages.warning(request, "Please select a variant before buying.")
        return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)

    user = request.user if request.user.is_authenticated else None

    try:
        cart = Cart.objects.get(user=request.user if request.user.is_authenticated else None)
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

    return redirect('checkout')

def empty_cart(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        CartItem.objects.filter(cart=cart).delete()
    except Cart.DoesNotExist:
        pass
    return redirect('cart')