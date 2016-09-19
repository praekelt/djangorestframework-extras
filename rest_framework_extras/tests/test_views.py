import unittest
import json


from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test.client import Client, RequestFactory

from rest_framework.test import APIRequestFactory, APIClient

from rest_framework_extras.tests import models


def get_control(model="vanilla", pk=1, another_editable_field_suffix=""):
    return {
        u"url": u"http://testserver/tests-%s/%s/" % (model, pk),
        u"editable_field": u"editable_field",
        u"another_editable_field": u"another_editable_field%s" \
            % another_editable_field_suffix,
        u"many_field": [u"http://testserver/tests-bar/1/"],
        u"foreign_field": u"http://testserver/tests-foo/1/",
        u"non_editable_field": u""
     }


class ViewsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = APIRequestFactory()
        cls.client = APIClient()

        # Editor
        cls.editor = get_user_model().objects.create(
            username="editor",
            email="editor@test.com",
            is_superuser=True,
            is_staff=True
        )
        cls.editor.set_password("password")
        cls.editor.save()
        cls.client.login(username="editor", password="password")

        cls.bar = models.Bar.objects.create()
        cls.foo = models.Foo.objects.create()

        cls.vanilla = models.Vanilla.objects.create(
            editable_field="editable_field",
            another_editable_field="another_editable_field",
            foreign_field=cls.foo
        )
        cls.vanilla.many_field = [cls.bar]
        cls.vanilla.save()

        cls.with_form = models.WithForm.objects.create(
            editable_field="editable_field",
            another_editable_field="another_editable_field",
            foreign_field=cls.foo
        )
        cls.with_form.many_field = [cls.bar]
        cls.with_form.save()

        cls.with_tricky_form = models.WithTrickyForm.objects.create(
            editable_field="editable_field",
            another_editable_field="another_editable_field",
            foreign_field=cls.foo
        )
        cls.with_tricky_form.many_field = [cls.bar]
        cls.with_tricky_form.save()

    def test_vanilla_list(self):
        response = self.client.get("/tests-vanilla/")
        as_json = json.loads(response.content)
        self.assertEqual(as_json[0], get_control())

    def test_vanilla_get(self):
        response = self.client.get("/tests-vanilla/%s/" % self.vanilla.pk)
        as_json = json.loads(response.content)
        self.assertEqual(as_json, get_control())

    def test_vanilla_create(self):
        new_pk = models.Vanilla.objects.all().last().id + 1
        data = {
            "editable_field": "editable_field",
            "another_editable_field": "another_editable_field",
            "foreign_field": "http://testserver/tests-foo/1/",
            "many_field": ["http://testserver/tests-bar/1/"],
        }
        response = self.client.post("/tests-vanilla/", data)
        as_json = json.loads(response.content)
        self.assertEqual(as_json, get_control(pk=new_pk))
        self.assertTrue(models.Vanilla.objects.filter(pk=new_pk).exists())

    def test_vanilla_patch(self):
        data = {
            "editable_field": "editable_field_x",
        }
        response = self.client.patch(
            "/tests-vanilla/%s/" % self.vanilla.pk,
            data,
        )
        as_json = json.loads(response.content)
        self.assertEqual(as_json["editable_field"], "editable_field_x")
        self.assertEqual(
            models.Vanilla.objects.get(pk=self.vanilla.pk).editable_field,
            "editable_field_x"
        )

    def test_with_form_list(self):
        response = self.client.get("/tests-withform/")
        as_json = json.loads(response.content)
        self.assertEqual(as_json[0], get_control(model="withform"))

    def test_with_form_get(self):
        response = self.client.get("/tests-withform/%s/" % self.with_form.pk)
        as_json = json.loads(response.content)
        self.assertEqual(as_json, get_control(model="withform"))

    def test_with_form_create(self):
        new_pk = models.WithForm.objects.all().last().id + 1
        data = {
            "editable_field": "editable_field",
            "another_editable_field": "another_editable_field",
            "foreign_field": "http://testserver/tests-foo/1/",
            "many_field": ["http://testserver/tests-bar/1/"],
        }
        response = self.client.post("/tests-withform/", data)
        as_json = json.loads(response.content)
        self.assertEqual(as_json, get_control(model="withform", pk=new_pk))
        self.assertTrue(models.WithForm.objects.filter(pk=new_pk).exists())

    def test_with_form_patch(self):
        data = {
            "editable_field": "editable_field_x",
        }
        response = self.client.patch(
            "/tests-withform/%s/" % self.vanilla.pk,
            data,
        )
        as_json = json.loads(response.content)
        self.assertEqual(as_json["editable_field"], "editable_field_x")
        self.assertEqual(
            models.WithForm.objects.get(pk=self.with_form.pk).editable_field,
            "editable_field_x"
        )

    def test_with_tricky_form_list(self):
        response = self.client.get("/tests-withtrickyform/")
        as_json = json.loads(response.content)
        self.assertEqual(as_json[0], get_control(model="withtrickyform"))

    def test_with_tricky_form_create(self):
        """We cannot handle declared form fields yet"""
        new_pk = models.WithTrickyForm.objects.all().last().id + 1
        data = {
            "editable_field": "editable_field",
            "another_editable_field": "another_editable_field",
            "foreign_field": "http://testserver/tests-foo/1/",
            "many_field": ["http://testserver/tests-bar/1/"],
            "an_integer": 777,
        }
        response = self.client.post("/tests-withtrickyform/", data)
        as_json = json.loads(response.content)
        self.assertEqual(as_json, {u"an_integer": [u"This field is required."]})
