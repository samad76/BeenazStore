from django.shortcuts import render

from store.models import Product

def index(request):
    products = Product.objects.all().filter(stock__gt=0).order_by('title')
    context = {
        'products': products
    }
    return render(request, 'index.html', context)