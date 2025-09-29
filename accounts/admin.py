from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Accounts, userProfile
from django.utils.html import format_html

# Register your models here.
class AccountsAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name','phone_number', 'last_login', 'is_active', 'is_staff')
    list_display_links = ('email', 'username')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined', 'email',)
    readonly_fields = ['date_joined', 'last_login']


class userProfileInline(admin.StackedInline):
    def thumbnail(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%;">',
                obj.profile_picture.url
            )
        return '(No image)'
    model = userProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    list_display = ('thumbnail', 'user', 'city', 'province', 'country')
    readonly_fields = ('thumbnail',)
AccountsAdmin.inlines = (userProfileInline,)


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%;">',
                obj.profile_picture.url
            )
        return '(No image)'
    thumbnail.short_description = 'Profile Picture'
    list_display_links = ('thumbnail', 'user')
    readonly_fields = ('thumbnail',)
    list_display = ('thumbnail', 'user', 'city', 'province', 'country')
    search_fields = ('user__email', 'user__username', 'city', 'province', 'country')

admin.site.register(Accounts, AccountsAdmin)
admin.site.register(userProfile, UserProfileAdmin)
