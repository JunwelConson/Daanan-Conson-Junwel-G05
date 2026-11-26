from django.conf import settings
from django.db import models
from django.db.models import Q


class Place(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='places_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accessibility_features = models.ManyToManyField(
        'AccessibilityFeature',
        through='PlaceAccessibility',
        related_name='places',
    )

    class Meta:
        ordering = ('name', 'id')
        constraints = [
            models.CheckConstraint(
                condition=Q(latitude__isnull=True)
                | Q(latitude__gte=-90, latitude__lte=90),
                name='places_latitude_valid_range',
            ),
            models.CheckConstraint(
                condition=Q(longitude__isnull=True)
                | Q(longitude__gte=-180, longitude__lte=180),
                name='places_longitude_valid_range',
            ),
        ]

    def __str__(self):
        return self.name


class AccessibilityFeature(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name', 'id')

    def __str__(self):
        return self.name


class PlaceAccessibility(models.Model):
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name='accessibility_records',
    )
    feature = models.ForeignKey(
        AccessibilityFeature,
        on_delete=models.CASCADE,
        related_name='place_records',
    )
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('place__name', 'feature__name', 'id')
        constraints = [
            models.UniqueConstraint(
                fields=('place', 'feature'),
                name='places_unique_place_feature',
            ),
        ]

    def __str__(self):
        return f'{self.place.name} - {self.feature.name}'
