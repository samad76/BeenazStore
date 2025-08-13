from .models import Category

def menu_links(request):
    menu_links = Category.objects.all()
    return dict(menu_links=menu_links)