from rest_framework import permissions
from rest_framework.authtoken.admin import User

from .redis import session_storage

from rest_framework import authentication
from rest_framework import exceptions


class AuthenticationBySessionID(authentication.BaseAuthentication):
    def authenticate(self, request):
        session_id = request.COOKIES["session_id"]
        if session_id is None:
            raise exceptions.AuthenticationFailed('No session_id')

        try:
            username = session_storage.get(session_id).decode('utf-8')
        except Exception as e:
            raise exceptions.AuthenticationFailed('session_id not found')

        user = User.objects.get(username=username)
        if user is None:
            raise exceptions.AuthenticationFailed('No such user')

        return user, None


class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        session_id = request.COOKIES["session_id"]
        if session_id is None:
            return False
        try:
            session_storage.get(session_id).decode('utf-8')
        except Exception as e:
            return False
        return True
