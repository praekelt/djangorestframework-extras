import unittest

from django.core.urlresolvers import reverse

from rest_framework_extras import SETTINGS


class DiscoverTestCase(unittest.TestCase):

    def test_discovered(self):
        # Must import late
        from rest_framework_extras.tests.urls import router
        n = 0
        for name, klass, model_name in router.registry:
            if name == u"tests-vanilla":
                self.assertEqual(klass.__name__, "TestsVanillaViewSet")
                n += 1
            elif name == u"tests-withform":
                self.assertEqual(klass.__name__, "TestsWithFormViewSet")
                n += 1
            elif name == u"tests-withadminclass":
                self.assertEqual(klass.__name__, "TestsWithAdminClassViewSet")
                n += 1
            elif name == u"tests-bar":
                self.assertEqual(klass.__name__, "TestsBarViewSet")
                n += 1

        if n != 4:
            self.fail("Found %s of 4 items in router registry" % n)

    def test_blacklist(self):
        # Must import late
        from rest_framework_extras.tests.urls import router

        for name, klass, model_name in router.registry:
            self.failIf(name in SETTINGS["blacklist"])

