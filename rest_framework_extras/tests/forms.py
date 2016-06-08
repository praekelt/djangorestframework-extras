from django import forms

from rest_framework_extras.tests import models


class WithFormForm(forms.ModelForm):

    class Meta:
        model = models.WithForm
        fields = (
            "editable_field",
            #"non_editable_field",
            "foreign_field",
            "many_field"
        )
