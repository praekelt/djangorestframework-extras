from rest_framework.permissions import DjangoObjectPermissions


class UserPermissions(DjangoObjectPermissions):

    def has_permission(self, request, view):
        # Grant seemingly powerful permissions. has_object_permission will
        # refine it further.
        return view.action in ("retrieve", "update", "partial_update") \
            or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        user = request.user
        #if user.username == "user":
        #    import pdb;pdb.set_trace()

        if user.is_superuser:
            return True

        if user.pk == obj.pk:
            return True

        if not user.is_staff:
            return False

        return super(UserPermissions, self).has_object_permission(
            request, view, obj
        )
