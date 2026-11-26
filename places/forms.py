from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Place, PlaceAccessibility


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('name', 'address', 'latitude', 'longitude', 'description')


class PlaceAccessibilityForm(forms.ModelForm):
    class Meta:
        model = PlaceAccessibility
        fields = ('feature', 'notes')
        widgets = {
            'feature': forms.Select(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class BasePlaceAccessibilityFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        selected_features = set()
        for form in self.forms:
            cleaned_data = getattr(form, 'cleaned_data', {})
            if not cleaned_data or cleaned_data.get('DELETE'):
                continue

            feature = cleaned_data.get('feature')
            if feature is None:
                continue

            if feature in selected_features:
                raise ValidationError(
                    'A feature can only be associated with a place once.'
                )

            selected_features.add(feature)


PlaceAccessibilityFormSet = inlineformset_factory(
    Place,
    PlaceAccessibility,
    form=PlaceAccessibilityForm,
    formset=BasePlaceAccessibilityFormSet,
    extra=1,
    can_delete=True,
)
