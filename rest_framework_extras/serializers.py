import logging

import six

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

    def validate(self, attrs):
        """Delegate validation to form if it is set"""
        klass = getattr(self.Meta, 'form', None)
        if klass:
            form = klass(attrs)
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
        klass = getattr(self.Meta, "form", None)
        if not klass:
            return super(FormMixin, self).save(**kwargs)

        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )
        form = klass(validated_data)
        self.instance = form.save()
        return self.instance


class SerializerMeta(serializers.SerializerMetaclass):

    def __new__(cls, name, bases, attrs):
        model = attrs.pop("model", None)
        form = attrs.pop("form", None)
        cls = super(SerializerMeta, cls).__new__(cls, name, bases, attrs)
        meta_klass = type(
            "Meta",
            (object,),
            {"model": model, "form": form}
        )
        setattr(cls, "Meta", meta_klass)
        print id(cls.Meta)
        return cls


@six.add_metaclass(SerializerMeta)
class HyperlinkedModelSerializer(FormMixin, serializers.HyperlinkedModelSerializer):
    serializer_related_field = RelaxedHyperlinkedRelatedField
