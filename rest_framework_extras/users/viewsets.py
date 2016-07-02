import logging
import json

from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import viewsets
from rest_framework.serializers import HyperlinkedModelSerializer, \
    ReadOnlyField, Serializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAdminUser, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.reverse import reverse
from rest_framework_extras.users.permissions import UserPermissions


logger = logging.getLogger("django")


class UserSerializerForSuperUser(HyperlinkedModelSerializer):

    class Meta:
        model = User
        exclude = ("password",)


class UserSerializerForStaff(HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_staff")
        readonly_fields = ("last_login", "date_joined", "is_active")


class UserSerializerForUser(HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        readonly_fields = ("last_login", "date_joined", "is_active")


'''
class CommonRoutes(object):

    @detail_route(methods=["get"])
    def images(self, request, pk, **kwargs):
        li = []
        for image in self.get_object().images.all():
            # I can't get reverse('jmbo-image-detail', args=(image.pk,),
            # request=self.request) to work, so use a workaround.
            # xxx: DRF does not prefix base_name with app_label. Investigate.
            reversed = "%s%s/" % (reverse("image-list", request=self.request), image.pk)
            li.append(reversed)
        return Response({"status": "success", "images": li})
'''

class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (UserPermissions,)

    def get_serializer_class(self):
        user = self.request.user
        if user.is_superuser:
            return UserSerializerForSuperUser
        if user.is_staff:
            return UserSerializerForStaff
        return UserSerializerForUser
