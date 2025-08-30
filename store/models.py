from django.db import models
from django.urls import reverse
from category.models import Category
from ckeditor.fields import RichTextField
from django.utils.html import format_html
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = RichTextField(config_name='custom', null=True, blank=True)
    short_description = RichTextField(config_name='custom', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField()
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    is_variant = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    sales_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_bestseller(self):
        return self.sales_count > 100  # tweak threshold as needed

      
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.title

class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='photos/products/', blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def image_tag(self):
        if self.image:
            return format_html('<img src="{}" style="height: 50px;"/>', self.image.url)
        return "No Image"

    def __str__(self):
        return f"Image for {self.product.title}"



# Variant Types
class ColorVariant(models.Model):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, blank=True)  # Optional for UI

    def __str__(self):
        return self.name

class SizeVariant(models.Model):
    name = models.CharField(max_length=50)
    volume_ml = models.PositiveIntegerField(null=True, blank=True)  # e.g. 100ml

    def __str__(self):
        return self.name

class FlavorVariant(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_type='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_type='size', is_active=True)

    def flavors(self):
        return super(VariationManager, self).filter(variation_type='flavor', is_active=True)

variation_type_choice = (
    ('color', 'color'),
    ('size', 'size'),
    ('flavor', 'flavor'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_type = models.CharField(max_length=10, choices=variation_type_choice)
    color = models.ForeignKey(ColorVariant, null=True, blank=True, on_delete=models.CASCADE, related_name='color_variations')
    size = models.ForeignKey(SizeVariant, null=True, blank=True, on_delete=models.CASCADE, related_name='size_variations')
    flavor = models.ForeignKey(FlavorVariant, null=True, blank=True, on_delete=models.CASCADE, related_name='flavor_variations')
    is_active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True, editable=True)
    image = models.ImageField(upload_to='photos/variations/', blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)
    def image_tag(self):
        if self.image:
            return format_html('<img src="{}" style="height: 50px;"/>', self.image.url)
        return "No Image"
    image_tag.short_description = 'Preview'
    

    objects = VariationManager()

    def __str__(self):
        if self.variation_type == 'color' and self.color:
            return self.color.name
        elif self.variation_type == 'size' and self.size:
            return self.size.name
        elif self.variation_type == 'flavor' and self.flavor:
            return self.flavor.name
        return str(self.variation_type)
    











