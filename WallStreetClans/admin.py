from django.contrib import admin
from WallStreetClans.models import WallStreetUser, BlogPost, OTP, Listing, Offer, Subscription, Ad, Payment

# Register your models here.
admin.site.register(WallStreetUser)
admin.site.register(BlogPost)
admin.site.register(OTP)
admin.site.register(Listing)
admin.site.register(Offer)
admin.site.register(Subscription)
admin.site.register(Ad)
admin.site.register(Payment)

