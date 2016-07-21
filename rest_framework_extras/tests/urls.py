from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from rest_framework import routers

from rest_framework_extras import discover, register
from rest_framework_extras.tests import forms


router = routers.SimpleRouter()

discover(router,
    override=[
        ("tests.withform", dict(form=forms.WithFormForm)),
        ("tests.withtrickyform", dict(form=forms.WithFormTrickyForm)),
        #("tests.shoo", dict(admin=ModelBaseAdmin, admin_site=admin.site)),
    ],
)
register(router)

urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework"))
]
