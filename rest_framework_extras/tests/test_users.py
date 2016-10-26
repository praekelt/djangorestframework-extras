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

    def test_anonymous_get_user(self):
        response = self.client.get("/auth-user/")
        self.assertEqual(response.status_code, 403)
        response = self.client.get("/auth-user/1/")
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
        self.failIf("password" in as_json)
        query = self.user_model.objects.filter(pk=new_pk)
        self.assertTrue(query.exists())

        # Password must exist and be hashed
        obj = query[0]
        self.assertNotEqual(obj.password, None)
        self.assertNotEqual(obj.password, "password")

    def test_superuser_get_user(self):
        self.client.login(username="superuser", password="password")
        response = self.client.get("/auth-user/")
        as_json = json.loads(response.content)
        self.failIf("password" in as_json[0])
        response = self.client.get("/auth-user/1/")
        as_json = json.loads(response.content)
        self.failIf("password" in as_json)

    def test_staff_create_user(self):
        self.client.login(username="staff", password="password")
        new_pk = self.user_model.objects.all().last().id + 1
        data = {
            "username": "tscu",
            "password": "password"
        }
        response = self.client.post("/auth-user/", data)
        as_json = json.loads(response.content)
        self.assertEqual(as_json["username"], "tscu")
        self.failIf("password" in as_json)
        query = self.user_model.objects.filter(pk=new_pk)
        self.assertTrue(query.exists())

        # Password must exist and be hashed
        obj = query[0]
        self.assertNotEqual(obj.password, None)
        self.assertNotEqual(obj.password, "password")

        # Staff can't create superusers. That field is discarded.
        new_pk = self.user_model.objects.all().last().id + 1
        data = {
            "username": "tscu1",
            "password": "password",
            "is_superuser": True
        }
        response = self.client.post("/auth-user/", data)
        as_json = json.loads(response.content)
        self.failIf("is_superuser" in as_json)
        query = self.user_model.objects.filter(pk=new_pk)
        self.assertTrue(query.exists())
        obj = query[0]
        self.failIf(obj.is_superuser)

    def test_staff_update_user(self):
        # Staff can't bump users to superuser
        self.client.login(username="staff", password="password")
        data = {
            "is_superuser": True
        }
        response = self.client.patch("/auth-user/%s/" % self.staff.pk, data)
        as_json = json.loads(response.content)
        self.failIf("is_superuser" in as_json)
        self.failIf(self.user_model.objects.get(pk=self.staff.pk).is_superuser)

    def test_staff_update_superuser(self):
        # Staff can't edit superusers
        self.client.login(username="staff", password="password")
        data = {
            "email": "superuser@foo.com"
        }
        response = self.client.patch("/auth-user/%s/" % self.superuser.pk, data)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(
            self.user_model.objects.get(pk=self.superuser.pk).email,
            "superuser@foo.com"
        )

    def test_staff_get_user(self):
        self.client.login(username="staff", password="password")
        response = self.client.get("/auth-user/")
        as_json = json.loads(response.content)
        self.failIf("password" in as_json[0])
        response = self.client.get("/auth-user/1/")
        as_json = json.loads(response.content)
        self.failIf("password" in as_json)

    def test_user_create_user(self):
        self.client.login(username="user", password="password")
        data = {
            "username": "tucu",
            "password": "password"
        }
        response = self.client.post("/auth-user/", data)
        self.assertEqual(response.status_code, 403)

    def test_user_get_user(self):
        # User may only get himself
        self.client.login(username="user", password="password")
        response = self.client.get("/auth-user/")
        self.assertEqual(response.status_code, 403)
        response = self.client.get("/auth-user/%s/" % self.staff.pk)
        self.assertEqual(response.status_code, 403)
        response = self.client.get("/auth-user/%s/" % self.user.pk)
        as_json = json.loads(response.content)
        self.assertEqual(as_json["username"], self.user.username)
        self.failIf("password" in as_json)

    def test_user_update_user(self):
        # User may only update himself
        self.client.login(username="user", password="password")
        data = {
            "email": "user@foo.com"
        }
        response = self.client.patch("/auth-user/%s/" % self.staff.pk, data)
        self.assertEqual(response.status_code, 403)
        response = self.client.patch("/auth-user/%s/" % self.user.pk, data)
        as_json = json.loads(response.content)
        self.assertEqual(as_json["email"], "user@foo.com")
        self.assertEqual(
            self.user_model.objects.get(pk=self.user.pk).email, "user@foo.com"
        )

        # User may not bump himself to superuser or staff
        data = {
            "is_superuser": True
        }
        response = self.client.patch("/auth-user/%s/" % self.user.pk, data)
        as_json = json.loads(response.content)
        self.failIf("is_superuser" in as_json)
        self.failIf(self.user_model.objects.get(pk=self.user.pk).is_superuser)
        data = {
            "is_staff": True
        }
        response = self.client.patch("/auth-user/%s/" % self.user.pk, data)
        self.failIf("is_staff" in as_json)
        self.failIf(self.user_model.objects.get(pk=self.user.pk).is_staff)
