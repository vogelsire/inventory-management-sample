
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Anyone can read.
    Only staff users can create, update, or delete products.

    For Testing, python manage.py createsuperuser
    Username: admin
    Password: password

    from django.contrib.auth.models import User
    User.objects.create_user(
        username="shopper",
        password="TestPassword-123"
    )
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
