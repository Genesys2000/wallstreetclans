from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Listing, Payment, WallStreetUser

class PaymentTestCase(TestCase):
    def setUp(self):
        self.user = WallStreetUser.objects.create_user(
            username='testuser', 
            email='testuser@example.com', 
            password='password',
        )
        self.property = Listing.objects.create(
            owner=self.user, 
            title='Test Property', 
            description='Description', 
            location='Location', 
            price=100000
        )
    
    def test_initiate_payment(self):
        self.client.login(email='testuser@example.com', password='password')
        response = self.client.post(reverse('initiate_payment'), {
            'email': 'testuser@example.com',
            'amount': 100000,
            'listing_id': self.property.pk
        })
        self.assertRedirects(response, 'https://checkout.paystack.com/...')
        
        payment = Payment.objects.get(property=self.property)


