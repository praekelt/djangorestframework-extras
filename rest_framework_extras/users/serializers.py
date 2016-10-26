from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework import fields


class UserSerializerForSuperUser(serializers.HyperlinkedModelSerializer):
    password = fields.CharField(allow_blank=True, write_only=True)

    class Meta:
        model = get_user_model()
        write_only_fields = ("password",)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super(UserSerializerForSuperUser, self).create(validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super(UserSerializerForSuperUser, self).update(
            instance, validated_data
        )
        if password:
            user.set_password(password)
            user.save()
        return user


class UserSerializerForStaff(serializers.HyperlinkedModelSerializer):
    password = fields.CharField(allow_blank=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "is_staff", "password")
        readonly_fields = ("last_login", "date_joined", "is_active", "is_superuser")
        write_only_fields = ("password",)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super(UserSerializerForStaff, self).create(validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super(UserSerializerForStaff, self).update(
            instance, validated_data
        )
        if password:
            user.set_password(password)
            user.save()
        return user


class UserSerializerForUser(serializers.HyperlinkedModelSerializer):
    password = fields.CharField(allow_blank=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "password")
        readonly_fields = ("last_login", "date_joined", "is_active")
        write_only_fields = ("password",)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super(UserSerializerForUser, self).update(
            instance, validated_data
        )
        if password:
            user.set_password(password)
            user.save()
        return user
