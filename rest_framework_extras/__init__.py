import logging
import re
from collections import OrderedDict

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

from rest_framework.permissions import DjangoModelPermissions

from rest_framework_extras.serializers import HyperlinkedModelSerializer


logger = logging.getLogger("django")


def get_settings():
    """Due to app loading issues during startup provide a function to return
    settings only when needed."""

    # Import late because apps may not be loaded yet
    from rest_framework.authentication import SessionAuthentication, BasicAuthentication

    return getattr(settings, "REST_FRAMEWORK_EXTRAS", {
        "blacklist": {
            "sessions-session": {},
            "admin-logentry": {},
        },
        "authentication-classes": (SessionAuthentication, BasicAuthentication),
        "permission-classes": (DjangoModelPermissions,)
    })


def discover(router, override=None, only=None, exclude=None):
    """Generate default serializers and viewsets. This function should be run
    before doing normal registration through the router."""

    # Import late because apps may not be loaded yet
    from django.contrib.contenttypes.models import ContentType
    from rest_framework import viewsets

    # Upon first migrate the contenttypes have not been loaded yet
    try:
        list(ContentType.objects.all())
    except (OperationalError, ProgrammingError):
        return False

    filters = OrderedDict()

    # If only is set it trumps normal discovery
    if only is None:
        for app in reversed(settings.INSTALLED_APPS):
            for ct in ContentType.objects.filter(app_label=app.split(".")[-1]):
                filters["%s.%s" % (ct.app_label, ct.model)] = {"content_type": ct}

    # Parse the setting
    for el in ((only or []) or (override or [])):
        pattern_or_name = form = admin = admin_site = None
        if isinstance(el, (list, tuple)):
            pattern_or_name, di = el
            form = di.get("form", None)
            admin = di.get("admin", None)
            admin_site = di.get("admin_site", None)
            if any((admin, admin_site)) and not all((admin, admin_site)):
                raise RuntimeError("admin and admin_site are mutually inclusive")
        else:
            pattern_or_name = el
        di = {}
        try:
            app_label, model = re.split(r"[\.-]", pattern_or_name)
            di = {"app_label": app_label, "model": model}
        except ValueError:
            di = {"app_label": pattern_or_name}
        for ct in ContentType.objects.filter(**di):
            filters["%s.%s" % (ct.app_label, ct.model)] = {
                "content_type": ct,
                "form": form,
                "admin": admin,
                "admin_site": admin_site
            }

    if exclude is not None:
        raise NotImplementedError

    SETTINGS = get_settings()
    for di in filters.values():
        ct = di["content_type"]
        pth = r"%s-%s" % (ct.app_label, ct.model)

        # Skip over blacklisted app_label / model pairs
        if pth in SETTINGS["blacklist"]:
            continue

        form = di.pop("form", None)
        admin = di.pop("admin", None)
        admin_site = di.pop("admin_site", None)
        model = ct.model_class()

        # We can't handle a model without a manager
        if not hasattr(model, "objects"):
            continue

        prefix = "%s%s" % (ct.app_label.capitalize(), model.__name__)
        serializer_klass = type(
            str("%sSerializer" % prefix),
            (HyperlinkedModelSerializer,),
            {
                "model": model,
                "form": form,
                "admin": admin,
                "admin_site": admin_site
            }
        )
        viewset_klass = type(
            str("%sViewSet" % prefix),
            (viewsets.ModelViewSet,),
            {
                "serializer_class": serializer_klass,
                "queryset": model.objects.all(),
                "authentication_classes": SETTINGS["authentication-classes"],
                "permission_classes": SETTINGS["permission-classes"]
            }
        )
        logger.info("DRFE: registering API url %s" % pth)
        router.register(pth, viewset_klass)
    return True


def register(router, mapping=None):
    """Register all viewsets known to app, overriding any items already
    registered with the same name."""

    # Import late because apps may not be loaded yet
    from rest_framework_extras.users.viewsets import UsersViewSet

    if mapping is None:
        mapping =  (
            ("auth-user", UsersViewSet),
        )

    for pth, klass in mapping:
        keys = [tu[0] for tu in router.registry]
        try:
            i = keys.index(pth)
            del router.registry[i]
        except ValueError:
            pass
        # Leave default handling intact until view_name issues are resolved
        router.register(
            r"%s" % pth,
            klass
        )
        # Provide a base_name to consider app_label as well
        router.register(
            r"%s" % pth,
            klass,
            base_name=pth
        )
