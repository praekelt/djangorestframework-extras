Django Rest Framework Extras
============================
**Django Rest Framework Extras provide a number of features to help automate API creation.**

.. figure:: https://travis-ci.org/praekelt/djangorestframework-extras.svg?branch=develop
   :align: center
   :alt: Travis

.. contents:: Contents
    :depth: 5

Prerequisite
============
#. pip install ``djangorestframework``

#. Add ``rest_framework`` to your ``INSTALLED_APPS`` setting.


Installation
============

#. Install or add ``djangorestframework-extras`` to your Python path.

#. Add ``rest_framework_extras`` to your ``INSTALLED_APPS`` setting.


Features List
=============

- Generating default serializers and viewsets.
- Registering all viewsets known to application.
- Custom serializers and permissions for default user, staff users and superusers.
- Custom relaxed HyperlinkedRelatedField and Serializer
- FormMixin: Delegates validation to a normal Django form


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

#. Line 1 & 3: The router and DefaultRouter classes connects the views and urls automatically and also creates the API root for us.
#. Line 5: The discover function generates default serializers and viewsets. This function should be run before normal registration.
#. Line 6: The new register function registers all viewsets overriding any items already registered with the same name.
#. Line 9: Define the urls by including router.urls.

Tips
====

To change the name of the register user model change the ``mapping`` parameter, such as::

    rest_framework_extras.register(router, mapping=(("user", UsersViewSet),))

To discover only specific models define a comma separated list with the ``only`` parameter, such as::

    rest_framework_extras.discover(router, only=["auth-user", "auth-permission"])

Unit Testing
============

To run tests use the following command::

    python manage.py test rest_framework_extras.tests --settings=rest_framework_extras.tests.settings.19

License
=======

Please see the License requirements in the LICENSE file of this repository.