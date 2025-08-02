from collections.abc import Sequence
from functools import partialmethod


class AdminModelPermissionMixin:
    permissions: dict[str, Sequence[str] | str] = {}

    def get_user_status_permissions(self, request) -> Sequence[str] | str | None:
        return self.permissions.get(getattr(request.user, 'status', None), [])

    @classmethod
    def _check_superuser_permissions(cls, request) -> bool:
        return request.user and request.user.is_authenticated and request.user.is_superuser

    def has_permission(self, request, *args, action: str, **kwargs) -> bool:
        perms = self.get_user_status_permissions(request) or []
        if perms == "__all__":
            return True
        return self._check_superuser_permissions(request) or action in perms

    def has_any_permissions(self, request, *args, actions: Sequence[str], **kwargs) -> bool:
        perms = self.get_user_status_permissions(request)
        if perms == "__all__":
            return True
        return self._check_superuser_permissions(request) or any(action in perms for action in actions)

    has_view_permission = partialmethod(has_permission, action="view")
    has_add_permission = partialmethod(has_permission, action="add")
    has_change_permission = partialmethod(has_permission, action="change")
    has_delete_permission = partialmethod(has_permission, action="delete")
    has_view_or_change_permission = partialmethod(has_any_permissions, actions=["view", "change"])
    has_module_permission = partialmethod(has_permission, action="module")
