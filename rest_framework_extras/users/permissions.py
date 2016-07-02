from rest_framework.permissions import DjangoObjectPermissions


class UserPermissions(DjangoObjectPermissions):

    def has_permission(self, request, view):
        # Grant seemingly powerful permissions. has_object_permission willl
        # refine it further.
        return view.action in ("retrieve", "update") or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        if user == obj:
            return True

        if not user.is_staff:
            return False

        return super(UserPermissions, self).has_object_permission(
            request, view, obj
        )
