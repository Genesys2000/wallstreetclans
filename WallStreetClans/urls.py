from django.urls import path
from .views import home, about_us, account, blog, search, register, otp_verification, user_login, initiate_payment, payment_success, payment_failed, payment_callback, user_logout, listing_list, listing_detail, make_offer, subscription, faq
from django.contrib import admin
from django.urls import path, include
from .views import AdViewSet, UserCreate, MyTokenObtainPairView, logout_view
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register(r'ads', AdViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('about/', about_us, name='about_us'),
    path('account/', account, name='account'),
    path('blog/', blog, name='blog'),
    path('search/', search, name='search'),
    path('register/', register, name='register'),
    path('otp_verification/', otp_verification, name='otp_verification'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('listings/', listing_list, name='listing_list'),
    path('listing/<int:pk>/', listing_detail, name='listing_detail'),
    path('listing/<int:pk>/make_offer/', make_offer, name='make_offer'),
    path('subscription/', subscription, name='subscription'),
    path('faq/', faq, name='faq'),
    path('', include(router.urls)),
    path('register/', UserCreate.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),
    # path('initiate_payment/', initiate_payment, name='initiate_payment'),
    # path('payment_success/', payment_success, name='payment_success'),
    # path('payment_failed/', payment_failed, name='payment_failed'),
    # path('payment_callback/', payment_callback, name='payment_callback'),
]



    

