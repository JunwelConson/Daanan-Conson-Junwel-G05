from django.contrib import admin

from .models import AccessibilityFeature, Place, PlaceAccessibility


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'created_by', 'created_at')
    search_fields = ('name', 'address', 'description', 'created_by__username')
    list_filter = ('created_at',)
    autocomplete_fields = ('created_by',)


@admin.register(AccessibilityFeature)
class AccessibilityFeatureAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


@admin.register(PlaceAccessibility)
class PlaceAccessibilityAdmin(admin.ModelAdmin):
    list_display = ('place', 'feature', 'notes')
    search_fields = ('place__name', 'feature__name', 'notes')
    list_filter = ('feature',)
    autocomplete_fields = ('place', 'feature')
