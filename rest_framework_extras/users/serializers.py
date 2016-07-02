from django.contrib.auth.models import User

from rest_framework.serializers import HyperlinkedModelSerializer


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
