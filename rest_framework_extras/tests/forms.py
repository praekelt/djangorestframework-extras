from django import forms

from rest_framework_extras.tests import models


class VanillaForm(forms.ModelForm):

    class Meta:
        model = models.Vanilla
        fields = (
            "editable_field",
            #"non_editable_field",
            "foreign_field",
            "many_field"
        )
