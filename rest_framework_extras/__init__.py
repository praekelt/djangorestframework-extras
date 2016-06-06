from django.conf import settings

from rest_framework import viewsets

from rest_framework_extras.serializers import FooSerializer


def autodiscover(router):
    """Iterate over installed apps and generate default serializer and viewset"""

    # Import late because apps may not be leaded yet
    from django.contrib.contenttypes.models import ContentType

    for app in reversed(settings.INSTALLED_APPS):
        for ct in ContentType.objects.filter(app_label=app):
            model = ct.model_class()
            if not hasattr(model, "objects"):
                continue
            prefix = "%s%s" % (ct.app_label.capitalize(), model.__name__)
            serializer_klass = type(
                str("%sSerializer" % prefix),
                (FooSerializer,),
                {"model": model}
            )
            viewset_klass = type(
                str("%sViewSet" % prefix),
                (viewsets.ModelViewSet,),
                {
                    "serializer_class": serializer_klass,
                    "queryset": model.objects.all()
                }
            )
            router.register(r"%s-%s" % (ct.app_label, ct.model), viewset_klass)


def set_form(router, prefix, form_class):
    """Add form class to serializer identified by prefix."""
    for pf, viewset, base_name in self.registry:
        if pf == prefix:
            viewset.serializer_klass.Meta.form = form_class
            break
