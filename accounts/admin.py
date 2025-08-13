from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Accounts

# Register your models here.
class AccountsAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_login', 'is_active', 'is_staff')
    list_display_links = ('email', 'username')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined', 'email',)
    readonly_fields = ['date_joined', 'last_login']
admin.site.register(Accounts, AccountsAdmin)
