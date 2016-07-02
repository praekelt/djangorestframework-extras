from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_extras.users.permissions import UserPermissions
from rest_framework_extras.users.serializers import UserSerializerForSuperUser, \
    UserSerializerForStaff, UserSerializerForUser


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
