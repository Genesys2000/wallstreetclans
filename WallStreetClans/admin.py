from django.contrib import admin
from .models import WallStreetUser, BlogPost, OTP, Listing, Offer, Subscription, Ad, Payment

class WallStreetUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email')

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('title', 'content')

# Define similar ModelAdmin classes for other models if needed

admin.site.register(WallStreetUser, WallStreetUserAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(OTP)
admin.site.register(Listing)
admin.site.register(Offer)
admin.site.register(Subscription)
admin.site.register(Ad)
admin.site.register(Payment)
