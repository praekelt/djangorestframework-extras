import types
import logging
from collections import OrderedDict

import six

from django.db.models.base import Model
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

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
            if not admin_site:
                # Fall back to default
                from django.contrib.admin import site as admin_site
            return  admin_klass(self.Meta.model, admin_site).get_form(
                self.context["request"], self.initial
            )
        elif form_klass:
            return form_klass
        return None

    def get_cached_form(self, data=None):
        if hasattr(self, "_form"):
            return self._form

        form_class = self.form_class
        if form_class:
            setattr(self, "_form", form_class(
                data,
                instance=self.instance if isinstance(self.instance, Model) \
                    else None)
            )
            return self._form

        return None

    def get_initial(self):
        form_class = self.form_class
        if not form_class:
            return super(FormMixin, self).get_initial()

        # We need a fresh instance to get initial values
        form = form_class(
            instance=self.instance if isinstance(self.instance, Model) else None
        )
        res = OrderedDict()
        for field_name, field in form.fields.items():
            if field.initial:
                res[field_name] = self.fields[field_name].to_representation(
                    field.initial
                )
        return res

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

        form = self.get_cached_form(attrs)

        diff = set(form.fields.keys()) - set(self.fields.keys())
        if diff:
            logger.warning("""DRFE: the field(s) "%s" are in the form %s but \
not in the serializer %s. You may encounter problems.""" % \
                (", ".join(diff), form_class.__name__, self.__class__.__name__)
            )

        if not form.is_valid():

            # Patch requests don't necessarily contain all the fields. Discard
            # validation errors on those not present.
            if self.context["request"].method.lower() == "patch":
                logger.warning("""DRFE: doing a PATCH for serializer %s with \
form %s. You may encounter problems.""" % \
                    (self.__class__.__name__, form_class.__name__)
                )

                for k, v in form.errors.items():
                    # This string matching is ugly but our only option
                    if v == [_("This field is required.")]:
                        del form.errors[k]
                        del form.fields[k]
                        exclude = list(getattr(form.Meta, "exclude", []))
                        exclude.append(k)
                        setattr(form.Meta, "exclude", exclude)

            # Map global error
            if "__all__" in form.errors:
                form.errors["non_field_errors"] = form.errors["__all__"]
                del form.errors["__all__"]
            raise serializers.ValidationError(form.errors)

        return super(FormMixin, self).validate(attrs)

    def save(self, **kwargs):
        """Delegate save to form if it is set"""

        form = self.get_cached_form()
        if not form:
            return super(FormMixin, self).save(**kwargs)

        try:
            self.instance = form.save()
        except Exception, exc:
            if self.context["request"].method.lower() == "patch":
                raise """DRFE: save failed with %s. This may be because \
 request was a PATCH.""" % exc
            raise
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
