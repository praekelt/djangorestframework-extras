Django Rest Framework Extras
############################
.. image:: https://travis-ci.org/praekelt/djangorestframework-extras.svg?branch=develop
    :target: https://travis-ci.org/praekelt/djangorestframework-extras?branch=develop
.. image:: https://coveralls.io/repos/github/praekelt/djangorestframework-extras/badge.svg
    :target: https://coveralls.io/github/praekelt/djangorestframework-extras

**DRFE generates RESTful API's for any Django models.**

.. contents:: Table of Contents
   :depth: 1

Prerequisite
============
#. pip install ``djangorestframework``

#. Add ``rest_framework`` to your ``INSTALLED_APPS`` setting in ``settings.py``.


Installation
============

#. Install or add ``djangorestframework-extras`` to your Python path.

#. Add ``rest_framework_extras`` to your ``INSTALLED_APPS`` setting in ``settings.py``.


Feature List
============

- Generating default serializers and viewsets for all known applications to create RESTful API's.
- Registering all viewsets known to the application with the Django Rest Framework router.
- Custom serializers and permissions for the default user, the staff users and superusers.
- Custom FormMixin that Delegates validation to a normal Django form.
- Custom Hyperlink fields and serializer, ``HyperlinkedRelatedField`` and ``HyperlinkedModelSerializer``


Usage
=====

User permissions and the custom UsersViewSet
--------------------------------------------

``djangorestframework-extras`` provides a custom ViewSet ``UsersViewSet`` with serializers and permissions for the default user, the staff user and the superuser.

Register UsersViewSet through the DefaultRouter::

    from rest_framework_extras.users.viewsets import UsersViewSet

    router = routers.DefaultRouter()

    router.register(r'users', UsersViewSet, 'user')

Discovery and registration of ViewSets
--------------------------------------

Enable discovery and registration of default serializers and viewsets by adding the following to ``urls.py``::

    from rest_framework import routers
    import rest_framework_extras
    router = routers.DefaultRouter()

    rest_framework_extras.discover(router)
    rest_framework_extras.register(router)

    urlpatterns = [
        url(r"^api/(?P<version>(v1))/", include(router.urls))
    ]

**Going through the code line by line:**

#. Line 1 & 3: The router and DefaultRouter classes connects the views and urls automatically and also creates the API root.
#. Line 5: The new discover function generates default serializers and viewsets. This function should be run before normal registration.
#. Line 6: The new register function registers all viewsets (including the UsersViewSet), overriding any items already registered with the same name.
#. Line 9: Define the urls by including router.urls.

Available Settings
------------------

``REST_FRAMEWORK_EXTRAS``

**blacklist**: A dictionary of the models to blacklist. By default the following models are blacklisted::

   "REST_FRAMEWORK_EXTRAS": {
      "blacklist": {
           "sessions-session": {},
           "admin-logentry": {}
      }
   }

Tips
====

Change the name of the registered user model by changing the ``mapping`` parameter, such as::

    rest_framework_extras.register(router, mapping=(("user", UsersViewSet),))

Restrict models that will be displayed through the Django Rest Framework by using the ``only`` and ``overwrite`` parameters. Define a comma separated list, such as::

    rest_framework_extras.discover(router, only=["auth-user", "auth-permission"])

Unit Testing
============

Run tests by using the following command::

    python manage.py test rest_framework_extras.tests --settings=rest_framework_extras.tests.settings.19

License
=======

Please see the License requirements in the LICENSE file of this repository.

