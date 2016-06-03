import logging

from rest_framework import serializers

from mysite.models import Manufacturer, Car
from mysite.admin import ManufacturerAdminForm
from mysite import class_form_mapping


logger = logging.getLogger("django")


class CarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Car
        #fields = ('id', 'title', 'code', 'linenos', 'language', 'style')


class FormMixin(object):
    """Delegates validation to a normal Django form.
    Example:
        class MySerializer(FormMixin, ModelSerializer):
            pass
    """
    _form_class = None

    def x__init__(self, *args, **kwargs):
        super(FormMixin, self).__init__(self, *args, **kwargs)

        # Inspect registry to see if a mapping exists. Viewset takes precedence
        # over serializer because viewset is usually in scope when the mapping is made,
        # thus saving on an import.
        #klass = class_form_mapping.get(self.context["view"].__class__)
        #if klass is None:
        #    klass = class_form_mapping.get(self.__class__)
        #self._form_class = klass

    #@property
    #def fields(self):
    #    fields = super(FormMixin, self).fields
    #    print fields

    def validate(self, attrs):
        #import pdb;pdb.set_trace()
        # Inspect registry to see if a mapping exists. Viewset takes precedence
        # over serializer because viewset is usually in scope when the mapping is made,
        # thus saving on an import.
        klass = class_form_mapping.get(self.context["view"].__class__)
        if klass is None:
            klass = class_form_mapping.get(self.__class__)
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


class ManufacturerSerializer(FormMixin, serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Manufacturer

    def validate_year(self, value):
        if value < 2010:
            raise serializers.ValidationError("Serializer says year must be after 2010")
        return value
