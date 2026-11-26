from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.db.models.deletion import ProtectedError

from .models import AccessibilityFeature, Place, PlaceAccessibility


User = get_user_model()


class PlaceManagementModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='place_creator',
            password='test-password-123',
        )

    def create_place(self, **overrides):
        values = {
            'name': 'Central Library',
            'address': '10 Main Street',
            'latitude': Decimal('14.599500'),
            'longitude': Decimal('120.984200'),
            'description': 'A public library.',
            'created_by': self.user,
        }
        values.update(overrides)
        return Place.objects.create(**values)

    def test_place_can_be_created_with_valid_data(self):
        place = self.create_place()

        self.assertIsNotNone(place.pk)
        self.assertEqual(place.name, 'Central Library')
        self.assertEqual(place.address, '10 Main Street')
        self.assertEqual(place.created_by, self.user)
        self.assertIsNotNone(place.created_at)

    def test_place_can_be_created_without_coordinates(self):
        place = self.create_place(latitude=None, longitude=None)

        place.refresh_from_db()
        self.assertIsNone(place.latitude)
        self.assertIsNone(place.longitude)

    def test_latitude_database_constraint_rejects_out_of_range_values(self):
        for latitude in (Decimal('-90.000001'), Decimal('90.000001')):
            with self.subTest(latitude=latitude):
                with self.assertRaises(IntegrityError):
                    with transaction.atomic():
                        self.create_place(latitude=latitude)

    def test_longitude_database_constraint_rejects_out_of_range_values(self):
        for longitude in (Decimal('-180.000001'), Decimal('180.000001')):
            with self.subTest(longitude=longitude):
                with self.assertRaises(IntegrityError):
                    with transaction.atomic():
                        self.create_place(longitude=longitude)

    def test_duplicate_place_accessibility_pair_is_rejected(self):
        place = self.create_place()
        feature = AccessibilityFeature.objects.create(name='Step-free entrance')
        PlaceAccessibility.objects.create(place=place, feature=feature)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PlaceAccessibility.objects.create(place=place, feature=feature)

    def test_different_features_can_be_associated_with_same_place(self):
        place = self.create_place()
        ramp = AccessibilityFeature.objects.create(name='Ramp')
        accessible_toilet = AccessibilityFeature.objects.create(
            name='Accessible toilet'
        )

        PlaceAccessibility.objects.create(place=place, feature=ramp)
        PlaceAccessibility.objects.create(place=place, feature=accessible_toilet)

        self.assertEqual(place.accessibility_records.count(), 2)
        self.assertEqual(place.accessibility_features.count(), 2)

    def test_deleting_place_creator_is_protected(self):
        self.create_place()

        with self.assertRaises(ProtectedError):
            self.user.delete()

        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_deleting_place_removes_associations(self):
        place = self.create_place()
        feature = AccessibilityFeature.objects.create(name='Ramp')
        association = PlaceAccessibility.objects.create(place=place, feature=feature)

        place.delete()

        self.assertFalse(PlaceAccessibility.objects.filter(pk=association.pk).exists())

    def test_deleting_feature_removes_associations(self):
        place = self.create_place()
        feature = AccessibilityFeature.objects.create(name='Ramp')
        association = PlaceAccessibility.objects.create(place=place, feature=feature)

        feature.delete()

        self.assertFalse(PlaceAccessibility.objects.filter(pk=association.pk).exists())

    def test_model_string_representations_are_useful(self):
        place = self.create_place()
        feature = AccessibilityFeature.objects.create(name='Ramp')
        association = PlaceAccessibility.objects.create(place=place, feature=feature)

        self.assertEqual(str(place), 'Central Library')
        self.assertEqual(str(feature), 'Ramp')
        self.assertEqual(str(association), 'Central Library - Ramp')
