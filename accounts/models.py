from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")
        if not first_name:
            raise ValueError("Users must have a first name")
    

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None):
        user = self.create_user(email, username, first_name, last_name, password)
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Accounts(AbstractUser):
    # Add any additional fields you want for your custom user model
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)    
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return super().has_module_perms(app_label)
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

ProvinceChoice=(
    ('Sindh', 'Sindh'),
    ('Punjab', 'Punjab'),
    ('Balochistan', 'Balochistan'),
    ('Khyber Pakhtunkhwa', 'Khyber Pakhtunkhwa'),
    ('Gilgit-Baltistan', 'Gilgit-Baltistan'),
    ('Azad Jammu and Kashmir', 'Azad Jammu and Kashmir'),
)
class userProfile(models.Model):
    user = models.OneToOneField(Accounts, on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile')
    city = models.CharField(blank=True, max_length=20)
    province = models.CharField(blank=True, max_length=100, choices=ProvinceChoice)
    country = models.CharField(blank=True, max_length=20)

    def __str__(self):
        return self.user.email

    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"