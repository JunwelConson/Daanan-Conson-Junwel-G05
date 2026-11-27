
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from .models import Place


User = get_user_model()


class PlaceManagementViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='place_user',
            password='test-password-123',
        )

        UserProfile.objects.create(
            user=self.user,
            role='user',
        )

    def test_anonymous_user_cannot_open_place_list(self):
        response = self.client.get(reverse('places:list'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_anonymous_user_cannot_open_place_detail(self):
        response = self.client.get(
            reverse('places:detail', args=[1])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_authenticated_user_can_open_place_creation_page(self):
        self.client.login(
            username='place_user',
            password='test-password-123',
        )

        response = self.client.get(reverse('places:create'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'places/place_form.html')

    def test_authenticated_user_can_create_place(self):
        self.client.login(
            username='place_user',
            password='test-password-123',
        )

        data = {
            'name': 'Accessible Community Center',
            'address': 'Cebu City',
            'latitude': '10.315700',
            'longitude': '123.885400',
            'description': 'A test place.',
            'accessibility_records-TOTAL_FORMS': '0',
            'accessibility_records-INITIAL_FORMS': '0',
            'accessibility_records-MIN_NUM_FORMS': '0',
            'accessibility_records-MAX_NUM_FORMS': '1000',
        }

        response = self.client.post(
            reverse('places:create'),
            data,
        )

        self.assertEqual(response.status_code, 302)

        place = Place.objects.get(name='Accessible Community Center')

        self.assertEqual(place.created_by, self.user)
        self.assertEqual(place.address, 'Cebu City')

    def test_user_cannot_create_place_with_invalid_coordinates(self):
        self.client.login(
            username='place_user',
            password='test-password-123',
        )

        data = {
            'name': 'Invalid Place',
            'address': 'Cebu City',
            'latitude': '150',
            'longitude': '123.885400',
            'description': 'Invalid latitude test.',
            'accessibility_records-TOTAL_FORMS': '0',
            'accessibility_records-INITIAL_FORMS': '0',
            'accessibility_records-MIN_NUM_FORMS': '0',
            'accessibility_records-MAX_NUM_FORMS': '1000',
        }

        response = self.client.post(
            reverse('places:create'),
            data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Place.objects.filter(name='Invalid Place').exists()
        )