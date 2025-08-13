from django.contrib import admin
from django.utils.html import format_html   
from . models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    
    def image_tag(self, obj):
        if obj.cat_image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.cat_image.url)
        return "No Image"

    list_display = ('name', 'slug', 'image_tag')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('name',)

# Register your models here.
admin.site.site_header = 'Beenaz Store Admin'
admin.site.site_title = 'Beenaz Store Admin Portal' 
admin.site.index_title = 'Welcome to Beenaz Store Admin Portal'

