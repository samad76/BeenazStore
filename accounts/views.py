from urllib import request
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib import messages, auth
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Accounts
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from cart.views import _cart_id
from cart.models import Cart, CartItem
import requests

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            phone_number = form.cleaned_data.get("phone_number")
            password = form.cleaned_data.get("password")
            username = first_name + last_name
            user = Accounts.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username
            )
            user.phone_number = phone_number
            user.set_password(password)
            user.save()

            # USER ACTIVATION EMAIL
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email

            # Send the email
            send_mail(
                mail_subject,
                message,
                'beenazstore@gmail.com',
                [to_email],
                fail_silently=False,
            )
            

            # You can add a success message or redirect to another page
            # messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address. Please verify to activate your account.')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:   
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
              try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                     cart_item = CartItem.objects.filter(cart=cart)
    
                     # Get the product variations by cart id
                     product_variation = []
                     for item in cart_item:
                          variation = item.variations.all()
                          product_variation.append(list(variation))
    
                     # Get the cart items from the user to access his product variations
                     cart_item = CartItem.objects.filter(user=user)
                     ex_var_list = []
                     id = []
                     for item in cart_item:
                          existing_variation = item.variations.all()
                          ex_var_list.append(list(existing_variation))
                          id.append(item.id)
    
                     for pr in product_variation:
                          if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                          else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                 item.user = user
                                 item.save()
              except:
                pass
                auth_login(request, user)
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    # next=/cart/checkout/
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
    else:
       return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
   auth_logout(request)
   return redirect('login') 

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. You can now log in to your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('register') 

def forgot_password(request):
    # Your forgot password logic here
    return render(request, 'accounts/forgot_password.html')

@login_required(login_url='login')
def dashboard(request):

    return render(request, 'accounts/dashboard.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Accounts.objects.filter(email=email).exists():
            user = Accounts.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email

            # Send the email
            send_mail(
                mail_subject,
                message,
                'beenazstore@gmail.com',
                [to_email],
                fail_silently=False,
            )
            messages.success(request, 'We have sent you an email to reset your password.')
            return redirect('login')
        else:
            messages.error(request, 'This email is not registered.')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')
    
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Accounts.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful. You can now log in with your new password.')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')