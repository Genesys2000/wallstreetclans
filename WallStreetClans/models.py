# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from PIL import Image

ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('realtor', 'Realtor'),
        ('listing_owner', 'Listing Owner'),
        ('group_manager', 'Group Manager'),
    ]

class WallStreetUserManger(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        if not username:
            raise ValueError('Username fied must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self,username,email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('terms_accepted',True)
        extra_fields.setdefault('role','group_manager')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('terms_accepted') is not True:
            raise ValueError('terms_accepted must have terms_accepted=True.')
        if extra_fields.get('role','group_manager') is not True:
            raise ValueError('role', 'group_manager must have=True.')
        
        user = self.create_user(username, email, password, **extra_fields)
        return user
    

class WallStreetUser(AbstractBaseUser):
    email = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=30, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    terms_accepted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = WallStreetUserManger()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email

class OTP(models.Model):
    user = models.ForeignKey(WallStreetUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 600 and not self.is_used


class BlogPost(models.Model):
    author = models.ForeignKey(WallStreetUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Listing(models.Model):
    owner = models.ForeignKey(WallStreetUser, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    listed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Subscription(models.Model):
    user = models.ForeignKey(WallStreetUser, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.plan}"
    

class Ad(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=300)
    image = models.ImageField(upload_to='ad_images/', blank=True, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(WallStreetUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.image.path)

    def __str__(self):
        return self.title
    
 
class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    owner = models.ForeignKey(WallStreetUser, on_delete=models.CASCADE, related_name='listings')

    def __str__(self):
        return self.title


class Offer(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='offers', default=models.SET_NULL)
    buyer = models.ForeignKey(WallStreetUser, on_delete=models.CASCADE, related_name='offers')
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')

    def __str__(self):
        return f"{self.listing.title} - {self.offer_price}"

class Payment(models.Model):
    user = models.ForeignKey(WallStreetUser, on_delete=models.CASCADE)
    Listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)