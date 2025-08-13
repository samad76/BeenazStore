from django.shortcuts import render
from store.models import Product
from category.models import Category
from .models import ProductImages

def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug is not None:
        categories = Category.objects.filter(slug=category_slug)
        products = Product.objects.filter(category__in=categories, stock__gt=0).order_by('title')
        product_count = products.count()
    else:
        products = Product.objects.all().filter(stock__gt=0).order_by('title')
        product_count = products.count()
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
    except Product.DoesNotExist:
        product = None
    context = {
        'single_product': single_product,
        'single_product_images': single_product_images,
    }
    return render(request, 'store/product-detail.html', context)