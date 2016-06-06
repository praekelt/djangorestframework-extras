import types

from django.conf import settings

from rest_framework import viewsets

from rest_framework_extras.serializers import HyperlinkedModelSerializer


def discover(router, override=None, only=None, exclude=None):
    """Generate default serializers and viewsets"""

    # Import late because apps may not be leaded yet
    from django.contrib.contenttypes.models import ContentType

    # Default
    filters = [{"app_label": app} for app in reversed(settings.INSTALLED_APPS)]

    # If only is set it trumps normal discovery
    if only is not None:
        filters = []
        for el in only:
            pattern_or_name = form = None
            if isinstance(el, (types.ListType, types.TupleType)):
                pattern_or_name, form = el
            else:
                pattern_or_name = el
            if "." in pattern_or_name:
                app_label, model = pattern_or_name.split(".")
                filters.append({"app_label": app_label, "model": model, "form": form})
            else:
                filters.append({"app_label": pattern_or_name, "form": form})

    if exclude is not None:
        raise NotImplementedError

    for filter in filters:
        form = filter.pop("form", None)
        for ct in ContentType.objects.filter(**filter):
            model = ct.model_class()
            if not hasattr(model, "objects"):
                continue
            prefix = "%s%s" % (ct.app_label.capitalize(), model.__name__)
            serializer_klass = type(
                str("%sSerializer" % prefix),
                (HyperlinkedModelSerializer,),
                {"model": model, "form": form}
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
