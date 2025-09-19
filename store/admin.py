from django.contrib import admin
from .models import Product, Variation, ProductImages, ColorVariant, SizeVariant, FlavorVariant, ReviewRating
from django.utils.html import format_html   
from django import forms
from ckeditor.widgets import CKEditorWidget
from import_export.admin import ExportMixin
from import_export import resources


class InStockFilter(admin.SimpleListFilter):
    title = 'Stock Availability'
    parameter_name = 'in_stock'

    def lookups(self, request, model_admin):
        return [('yes', 'In Stock'), ('no', 'Out of Stock')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(stock__gt=0)
        elif self.value() == 'no':
            return queryset.filter(stock=0)

class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Price Range'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return [('low', 'Under Rs. 500'), ('mid', 'Rs. 500–1000'), ('high', 'Above Rs. 1000')]

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(price__lt=500)
        elif self.value() == 'mid':
            return queryset.filter(price__gte=500, price__lte=1000)
        elif self.value() == 'high':
            return queryset.filter(price__gt=1000)


class ProductVariantResource(resources.ModelResource):
    class Meta:
        model = Variation
        fields = ('product__title', 'variation_type', 'price', 'stock', 'color', 'size', 'flavor')

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('title', 'slug', 'description', 'price', 'discounted_price', 'stock', 'sku', 'category', 'rating', 'is_variant', 'is_active')


class ProductVariantInline(admin.TabularInline):
    model = Variation
    extra = 1
    fields = ['color', 'size', 'flavor', 'price', 'stock', 'image', 'image_tag']
    readonly_fields = ['image_tag']
    show_change_link = True
    



class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    short_description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Product
        fields = '__all__'

class ProductImageInline(admin.TabularInline):
    model = ProductImages
    extra = 1
    fields = ['image', 'alt_text', 'uploaded_at']
    readonly_fields = ('uploaded_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    resource_class = ProductResource
    list_display = ('title', 'sku', 'price', 'stock', 'category', 'is_variant', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    form = ProductAdminForm
    inlines = [ProductImageInline, ]
    search_fields = ('title', 'description', 'sku')
    list_filter = ('category',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description','short_description' ,'price', 'discounted_price', 'stock', 'sku', 'category', 'rating', 'is_variant', 'is_active')
        }),
        
    )
    readonly_fields = ('created_at', 'updated_at')
    def is_low_stock(self, obj):
        return obj.stock < 5
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock?'
    
    def is_bestseller(self, obj):
        return obj.sales_count > 100
    is_bestseller.boolean = True
    is_bestseller.short_description = '🔥 Bestseller'




@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin, ExportMixin):
    resource_class = ProductVariantResource
    list_display = ['product', 'color', 'size', 'flavor', 'price', 'stock', 'image_tag']
    list_filter = ['color', 'size', 'flavor', InStockFilter, PriceRangeFilter]
    search_fields = ['product__name']
    readonly_fields = ['image_tag']
    def is_low_stock(self, obj):
        return obj.stock < 5
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock?'


@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.image.url)
        return "No Image"
    list_display = ('product', 'image_tag', 'alt_text')
    search_fields = ('product__title', 'alt_text')
    readonly_fields = ('uploaded_at',)



class ColorVariantForm(forms.ModelForm):
    class Meta:
        model = ColorVariant
        fields = '__all__'
        widgets = {
            'hex_code': forms.TextInput(attrs={
                'type': 'color',
                'style': 'width: 80px; padding: 0; border: none;',
            }),
        }


@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    form = ColorVariantForm
    list_display = ['name', 'color_preview']

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.hex_code
        )
    color_preview.short_description = 'Preview'
    search_fields = ['name', 'hex_code']
    
   
     

@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'volume_ml')
    search_fields = ('name',)
    

@admin.register(FlavorVariant)
class FlavorVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
      


@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'subject', 'rating', 'created_at', 'updated_at')
    search_fields = ('product__title', 'user__username', 'subject', 'review')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
