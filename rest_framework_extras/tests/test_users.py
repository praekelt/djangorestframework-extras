import unittest
import json


from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test.client import Client, RequestFactory

from rest_framework.test import APIRequestFactory, APIClient

from rest_framework_extras.tests import models


class UsersTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = APIRequestFactory()
        cls.client = APIClient()
        cls.user_model = get_user_model()

        # Superuser
        cls.superuser = cls.user_model.objects.create(
            username="superuser",
            email="superuser@test.com",
            is_superuser=True,
            is_staff=True
        )
        cls.superuser.set_password("password")
        cls.superuser.save()

        # Staff
        cls.staff = cls.user_model.objects.create(
            username="staff",
            email="staff@test.com",
            is_staff=True
        )
        cls.staff.set_password("password")
        cls.staff.save()

        # Plain user
        cls.user = cls.user_model.objects.create(
            username="user",
            email="user@test.com"
        )
        cls.user.set_password("password")
        cls.user.save()

    def setUp(self):
        self.client.logout()
        super(UsersTestCase, self).setUp()

    def test_anonymous_create_user(self):
        data = {
            "username": "tacu",
            "password": "password"
        }
        response = self.client.post("/auth-user/")
        self.assertEqual(response.status_code, 403)

    def test_superuser_create_user(self):
        self.client.login(username="superuser", password="password")
        new_pk = self.user_model.objects.all().last().id + 1
        data = {
            "username": "tsucu",
            "password": "password"
        }
        response = self.client.post("/auth-user/", data)
        as_json = json.loads(response.content)
        self.assertEqual(as_json["username"], "tsucu")
        query = self.user_model.objects.filter(pk=new_pk)
        self.assertTrue(query.exists())
        obj = query[0]
        # Password must exist and be hashed
        self.assertNotEqual(obj.password, None)
        self.failIf(obj.password, "password")
