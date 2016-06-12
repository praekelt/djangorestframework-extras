from django import forms

from rest_framework_extras.tests import models


class WithFormForm(forms.ModelForm):

    class Meta:
        model = models.WithForm
        fields = (
            "editable_field",
            "another_editable_field",
            "foreign_field",
            "many_field"
        )


class WithFormTrickyForm(forms.ModelForm):
    an_integer = forms.IntegerField(initial=1)

    class Meta:
        model = models.WithTrickyForm
        fields = (
            "editable_field",
            "another_editable_field",
            "foreign_field",
            "many_field"
        )

    def __init__(self, *args, **kwargs):
        super(WithFormTrickyForm, self).__init__(*args, **kwargs)

        if not self.instance:
            self.fields["editable_field"].initial = "initial"

        self.fields["editable_field"].label = "An editable field"

    def clean_editable_field(self):
        value = self.cleaned_data["editable_field"]
        if value == "bar":
            raise forms.ValidationError("Editable field may not be bar.")
        return value

    def clean(self):
        cd = self.cleaned_data
        if cd["editable_field"] == cd["another_editable_field"]:
            raise forms.ValidationError(
                "Editable field and Another editable field may not be the same."
            )
        return cd

    def save(self, commit=True):
        instance = super(WithFormTrickyForm, self).save(commit=commit)
        instance.another_editable_field = "%s%s" % \
            (instance.another_editable_field + self.cleaned_data["an_integer"])
        #instance.another_editable_field = "%s%s" % \
        #    (instance.another_editable_field, self.cleaned_data["another_editable_field"])
        instance.save()
        return instance

