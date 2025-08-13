from django.contrib import admin
from .models import Product, ProductVariation, ProductImages
from django.utils.html import format_html   
from django import forms
from ckeditor.widgets import CKEditorWidget

class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Product
        fields = '__all__'

class ProductImageInline(admin.TabularInline):
    model = ProductImages
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariation
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'sku', 'price', 'stock', 'category', 'is_variant')
    prepopulated_fields = {'slug': ('title',)}
    form = ProductAdminForm
    inlines = [ProductImageInline, ProductVariantInline]
    search_fields = ('title', 'description')
    list_filter = ('category',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'price', 'discounted_price', 'stock', 'sku', 'category', 'is_variant')
        }),
        
    )


@admin.register(ProductVariation)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'flavor', 'price', 'stock', 'sku')

@admin.register(ProductImages)
class ProductImageAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return "No Image"
    
    list_display = ('product', 'image_tag', 'alt_text')
    search_fields = ('product__title', 'alt_text')
