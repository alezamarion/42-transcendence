from django.test import TestCase, Client
from django.urls import reverse
from .models import User
from unittest.mock import patch
import json

class AuthenticationTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.auth_url = reverse('app_auth:intra_login')
        self.callback_url = reverse('app_auth:intra_login_redirect')

    @patch('app_auth.services.exchange_code')
    @patch('app_auth.services.get_access_token')
    @patch('app_auth.services.get_user_info')
    def test_user_creation_after_authentication(self, mock_get_user_info, mock_get_access_token, mock_exchange_code):
        # Mock the response from exchange_code
        mock_exchange_code.return_value = {
            'id': 12345,
            'login': 'testuser',
            'email': 'testuser@example.com'
        }
        # Mock the response from get_access_token
        mock_get_access_token.return_value = 'fake_access_token'
        # Mock the response from get_user_info
        mock_get_user_info.return_value = {
            'id': 12345,
            'login': 'testuser',
            'email': 'testuser@example.com'
        }

        # Simulate the login process
        response = self.client.get(self.callback_url, {'code': 'fake_code'})
        
        # Check if the user was created
        user = User.objects.get(username='testuser')
        
        # Print user details
        print("User Created:", user)
        
        # Verify the user details
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.username, 'testuser')
        
        # Check if the response is a redirect to success
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('app_auth:success'))



"""

python manage.py shell

from app_auth.models import User
users = User.objects.all()
for user in users:
    print(user.username, user.email)

"""