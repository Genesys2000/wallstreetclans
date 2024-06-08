# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import OTP, BlogPost, Listing, Offer, Ad, WallStreetUser
from .forms import *
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, viewsets
from rest_framework.filters import BaseFilterBackend
from rest_framework import filters
from django.contrib.auth import get_user_model
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.urls import reverse
# from .forms import PaymentForm
User = get_user_model()

def home(request):
    return render(request, 'index.html')

def about_us(request):
    return render(request, 'about_us.html')

def account(request):
    return render(request, 'account.html')

def blog(request):
    blog_posts = BlogPost.objects.all()
    return render(request, 'blog.html', {'blog_posts': blog_posts})

def search(request):
    query = request.GET.get('query')
    listings = Listing.objects.filter(title__icontains=query) if query else Listing.objects.all()
    return render(request, 'search.html', {'listings': listings})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Your registration is successful proceed to login")
            return redirect(reverse('login'))

    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def send_otp(user):
    otp_code = get_random_string(length=6, allowed_chars='0123456789')
    OTP.objects.create(user=user, otp=otp_code)
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp_code}',
        'from@example.com',
        [user.email],
        fail_silently=False,
    )

def otp_verification(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp']
            otp = OTP.objects.filter(otp=otp_code, user__email=request.POST.get('email')).first()
            if otp and otp.is_valid():
                otp.is_used = True
                otp.save()
                login(request, otp.user)
                return redirect('home')
    else:
        form = OTPForm()
    return render(request, 'registration/otp_verification.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            role = form.cleaned_data.get('role')
            user = WallStreetUser.objects.get(email=email)
            if user.check_password(password) and user.role == role:
                # send_otp(user)
                # return redirect('otp_verification')
                login(request,user)
                messages.info(request, "Welcome Back {{ user.username }}")
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password. Please try again.")
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

def listing_list(request):
    listings = Listing.objects.all()
    return render(request, 'listing_list.html', {'listings': listings})

def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return render(request, 'listing_detail.html', {'listing': listing})

def make_offer(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.method == 'POST':
        offer_price = request.POST.get('offer_price')
        if offer_price is None:
            # Handle the case where offer_price is missing
            messages.error(request, "Offer price is required.")
            return redirect('listing_detail', pk=pk)
        Offer.objects.create(listing=listing, buyer=request.user, offer_price=offer_price)
        return redirect('listing_detail', pk=pk)
    return render(request, 'make_offer.html', {'listing': listing})


# def cart(request):
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     return render(request, 'cart.html', {'cart': cart})

# def add_to_cart(request, pk):
#     listing = get_object_or_404(Listing, pk=pk)
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     CartItem.objects.create(cart=cart, listing=listing)
#     return redirect('cart')

# def remove_from_cart(request, pk):
#     cart_item = get_object_or_404(CartItem, pk=pk)
#     cart_item.delete()
#     return redirect('cart')

# def save_for_later(request, pk):
#     cart_item = get_object_or_404(CartItem, pk=pk)
#     cart_item.saved_for_later = True
#     cart_item.save()
#     return redirect('cart')

def subscription(request):
    return render(request, 'subscription.html')

def faq(request):
    return render(request, 'faq.html')

# Serializer for User Registration
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# View for User Registration
class UserCreate(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

# View for obtaining the JWT
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# View for Logout
@api_view(['POST'])
def logout_view(request):
    try:
        token = request.data['refresh_token']
        token_obj = RefreshToken(token)
        token_obj.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)

class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = "AdSerializer"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['price', 'address']
    search_fields = ['title', 'description', 'address', 'amenities',]
    ordering_fields = ['price', 'posted_at']

# @login_required
def initiate_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            amount = form.cleaned_data['amount']
            listing_id = form.cleaned_data['listing_id']
            listing = Listing.objects.get(id='listing _id')

            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "email": email,
                "amount": int(amount * 100),  # Paystack expects amount in kobo
                "metadata": {
                    "property_id": listing_id,
                    "user_id": request.user.id
                }
            }

            response = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=data)
            if response.status_code == 200:
                response_data = response.json()
                return redirect(response_data['data']['authorization_url'])
            else:
                form.add_error(None, "Error initializing payment. Please try again.")
    else:
        form = PaymentForm(initial={'amount': 0, 'property_id': 0})

    return render(request, 'payment/initiate_payment.html', {'form': form, 'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY})

@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        payment_reference = request.POST.get('reference')
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }
        response = requests.get(f"https://api.paystack.co/transaction/verify/{payment_reference}", headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            if response_data['data']['status'] == 'success':
                amount = response_data['data']['amount'] / 100
                listing_id = response_data['data']['metadata']['listing_id']
                user_id = response_data['data']['metadata']['user_id']

                Payment.objects.create(
                    user_id=user_id,
                    listing_id=listing_id,
                    amount=amount,
                    reference=payment_reference,
                    status='success'
                )
                return redirect('payment_success')
            else:
                Payment.objects.create(
                    user=request.user,
                    amount=amount,
                    reference=payment_reference,
                    status='failed'
                )
                return redirect('payment_failed')
    return redirect('home')

@login_required
def payment_success(request):
    return render(request, 'payment/payment_success.html')

@login_required
def payment_failed(request):
    return render(request, 'payment/payment_failed.html')