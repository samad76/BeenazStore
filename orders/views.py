from django.shortcuts import render, redirect
from cart.models import Cart, CartItem
from orders.models import Order
from .forms import OrderForm
from .models import Payment, Order, OrderProduct
from django.core.mail import send_mail
from django.template.loader import render_to_string
from decimal import Decimal, ROUND_HALF_UP


import datetime


def send_order_received_email(order):
    # Function to send order received email to customer
    subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': order.user,
        'order': order,
    })
    to_email = order.email
    send_mail(subject, message, 'beenazstore@gmail.com', [to_email])

# Create your views here.
def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart = Cart.objects.filter(user=current_user).first()
    cart_items = CartItem.objects.filter(cart=cart)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    quantity = 0
    total = 0
    grand_total = 0
    tax = 0 
    for item in cart_items:
        if item.variations.exists():
            for variation in item.variations.all():
                total += variation.price * item.quantity
                quantity += item.quantity
        else:
            total += item.product.discounted_price * item.quantity
            quantity += item.quantity

    tax = round((18 * total) / 100, 2)
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.payment_method = form.cleaned_data['payment_method']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.province = form.cleaned_data['province']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.status = "New"
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))  
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            request.session['order_number'] = order_number
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            
            if data.payment_method == 'Cash On Delivery':
                cart = Cart.objects.get(user=current_user)
                cart_items = CartItem.objects.filter(cart=cart)
                for item in cart_items:
                    orderproduct = OrderProduct()
                    orderproduct.order_id = order.id
                    orderproduct.payment = None  # or a Payment instance if available
                    orderproduct.user_id = order.user.id
                    orderproduct.product_id = item.product.id
                    orderproduct.quantity = item.quantity
                    orderproduct.product_price = item.product.discounted_price
                    orderproduct.ordered = True
                    orderproduct.save()
                # If the item has variations, add them to the OrderProduct
                    if item.variations.exists():
                        orderproduct.variations.set(item.variations.all())
                        orderproduct.save()
                # Reduce the quantity of the sold products
                    item.product.stock -= item.quantity
                    item.product.save() 
                # Clear the cart
                    cart_items.delete()
                # send order received email to customer
                send_order_received_email(order)
                return redirect('order_complete')
            else:
                subtotal = 0
                for item in cart_items:
                    if item.variations.exists():
                        for variation in item.variations.all():
                            subtotal += variation.price * item.quantity    
                    else:
                        subtotal += item.product.discounted_price * item.quantity
                tax = (Decimal('18') * Decimal(subtotal) / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                grand_total = subtotal + tax   
                context = {
                    'order': order,
                    'cart_items': cart_items,
                    'subtotal': subtotal,
                    'tax': tax,
                    'grand_total': grand_total,
                }
                return render(request, 'orders/payments.html', context)
        else:
            # If form is invalid, re-render the order page with errors
            context = {
                'form': form,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'store/checkout.html', context)

def payments(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        # Process payment here
        payments = Payment()
        order_number = request.session.get('order_number')  

        if order_number:
            order = Order.objects.get(order_number=order_number)
            payments.user = order.user
            payments.amount_paid = order.order_total
            payments.payment_method = payment_method
            payments.payment_id = order.order_number
            payments.status = 'Completed'
            payments.save()
            order.payment = payments
            order.is_ordered = True
            order.status = 'Ordered'
            order.save()
        # Move cart items to order products
            cart = Cart.objects.get(user=order.user)
            cart_items = CartItem.objects.filter(cart=cart)
            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payments
                orderproduct.user_id = order.user.id
                orderproduct.product_id = item.product.id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.product.discounted_price
                orderproduct.ordered = True
                orderproduct.save()
                # If the item has variations, add them to the OrderProduct
                if item.variations.exists():
                    orderproduct.variations.set(item.variations.all())
                orderproduct.save()
                # Reduce the quantity of the sold products
                item.product.stock -= item.quantity
                item.product.save() 
                # Clear the cart
                cart_items.delete()
                # send order received email to customer
                send_order_received_email(order)
            return redirect('order_complete')
    return render(request, 'orders/payments.html')



def order_complete(request):
    order_number = request.session.get('order_number')
    if order_number:
        order = Order.objects.get(order_number=order_number)
        order_products = OrderProduct.objects.filter(order=order)
        subtotal = sum(item.product_price * item.quantity for item in order_products)
        tax = round(subtotal * 0.18, 2)
        grand_total = subtotal + tax
        context = {
            'order_number': order_number,
            'order': order,
            'order_products': order_products,
            'subtotal': subtotal,
            'tax': tax,
            'grand_total': grand_total,
        }
        return render(request, 'orders/order_complete.html', context)
    return redirect('home')

def cash_on_delivery(request):
    
        # Process cash on delivery order
    return render(request, 'orders/order_complete.html')

def order_cancel(request):
    if request.method == 'POST':
        # Process order cancellation
        pass
    return render(request, 'orders/order_cancel.html')
