import types
import logging

import six

from django.db.models.base import Model
from django.core.exceptions import ImproperlyConfigured

from rest_framework import serializers, relations


logger = logging.getLogger("django")


class RelaxedHyperlinkedRelatedField(relations.HyperlinkedRelatedField):
    """DRF does not provide a convenient hook to exclude fields which don't
have a target view. A custom field class at least returns a string."""

    def to_representation(self, value):
        try:
            return super(
                RelaxedHyperlinkedRelatedField, self
            ).to_representation(value)
        except ImproperlyConfigured:
            return "__not_implemented__"


class FormMixin(object):
    """Delegates validation to a normal Django form.
    Example:
        class MySerializer(FormMixin, ModelSerializer):
            pass
    """

    @property
    def form_class(self):
        form_klass = getattr(self.Meta, "form", None)
        admin_klass = getattr(self.Meta, "admin", None)
        admin_site = getattr(self.Meta, "admin_site", None)
        if admin_klass:
            return  admin_klass(self.Meta.model, admin_site).get_form(
                self.context["request"], self.initial
            )
        elif form_klass:
            return form_klass
        return None

    def validate(self, attrs):
        """Delegate validation to form if it is set"""

        form_class = self.form_class
        if not form_class:
            return super(FormMixin, self).validate(attrs)

        # Convert any objects to primary keys
        for key, value in attrs.items():
            if isinstance(value, types.ListType):
                attrs[key] = [getattr(v, "pk", v) for v in value]
            elif hasattr(value, "pk"):
                attrs[key] = value.pk

        form = form_class(attrs)

        diff = set(form.fields.keys()) - set(self.fields.keys())
        if diff:
            logger.warning("""The field(s) "%s" are in the form %s but not in the \
serializer %s. You may encounter problems.""" % \
            (", ".join(diff), klass.__name__, self.__class__.__name__)
            )
        if not form.is_valid():
            # Map global error
            if "__all__" in form.errors:
                form.errors["non_field_errors"] = form.errors["__all__"]
                del form.errors["__all__"]
            raise serializers.ValidationError(form.errors)

        return super(FormMixin, self).validate(attrs)

    def save(self, **kwargs):
        """Delegate save to form if it is set"""

        form_class = self.form_class
        if not form_class:
            return super(FormMixin, self).save(**kwargs)

        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )
        form = form_class(validated_data)
        self.instance = form.save()
        return self.instance


class SerializerMeta(serializers.SerializerMetaclass):

    def __new__(cls, name, bases, attrs):
        model = attrs.pop("model", None)
        form = attrs.pop("form", None)
        admin = attrs.pop("admin", None)
        admin_site = attrs.pop("admin_site", None)
        cls = super(SerializerMeta, cls).__new__(cls, name, bases, attrs)
        meta_klass = type(
            "Meta",
            (object,),
            {
                "model": model,
                "form": form,
                "admin": admin,
                "admin_site": admin_site
            }
        )
        setattr(cls, "Meta", meta_klass)
        return cls


@six.add_metaclass(SerializerMeta)
class HyperlinkedModelSerializer(FormMixin, serializers.HyperlinkedModelSerializer):
    serializer_related_field = RelaxedHyperlinkedRelatedField
