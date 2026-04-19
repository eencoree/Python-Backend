from rest_framework import permissions


class CanViewVideo(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_published:
            True

        return request.user.is_authenticated and request.user == obj.owner
