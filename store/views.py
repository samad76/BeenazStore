from django.contrib import messages
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  
from django.db.models import Q  
from category.models import Category
from orders.models import OrderProduct
from .models import Product, ProductImages,  Variation, ReviewRating
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
from cart.views import cart  
from .forms import ReviewForm


def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug is not None:
        categories = Category.objects.filter(slug=category_slug)
        products = Product.objects.filter(category__in=categories, stock__gt=0).order_by('title')
        paginator = Paginator(products, 6)  # Show 6 products per page
        page = request.GET.get('page')
        try:
            products = paginator.page(page)
            product_count = products.paginator.count
        except PageNotAnInteger:
            products = paginator.page(1)
            product_count = products.paginator.count
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
            product_count = products.paginator.count
    else:
        products = Product.objects.all().filter(stock__gt=0).order_by('title')
        paginator = Paginator(products, 6)  # Show 6 products per page
        page = request.GET.get('page')
        try:
            products = paginator.page(page)
            product_count = products.paginator.count
        except PageNotAnInteger:
            products = paginator.page(1)
            product_count = products.paginator.count
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
            product_count = products.paginator.count  
        
        categories = Category.objects.all()
    context = {
        'products': products,
        'product_count': product_count,
        'categories': categories
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(slug=product_slug, category__slug=category_slug)
        single_product_images = ProductImages.objects.filter(product=single_product)
        reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
        if single_product.is_variant:
            single_product_variations = Variation.objects.filter(product=single_product)
        if request.user.is_authenticated:
            in_cart = CartItem.objects.filter(cart__user=request.user, product=single_product).exists()
    except Product.DoesNotExist:
        product = None
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
        in_cart = None
    context = {
        'reviews': reviews,
        'single_product': single_product,
        'single_product_images': single_product_images,
        'single_product_variations': single_product_variations if single_product.is_variant else None,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        
    }
    return render(request, 'store/product-detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            
            products = Product.objects.filter(
                Q(description__icontains=keyword) | Q(title__icontains=keyword),
                stock__gt=0
            ).order_by('title')
        else:
            products = Product.objects.none()
    
    context = {
        'products': products,
        'product_count': products.count(),
    }
    return render(request, 'store/store.html', context)


@login_required(login_url='login')
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you! Your review has been updated.')
            else:
                messages.error(request, 'There was an error updating your review.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
            else:
                messages.error(request, 'There was an error submitting your review.')
            return redirect(url)
    else:
        return redirect(url)