from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework import exceptions
from django.conf import settings
import jwt


def verify_token(token):
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=['HS256'], options={'verify_aud': False})

        return payload['user']
    except Exception as e:
        return None


def get_role_in_token(token):
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=['HS256'], options={'verify_aud': False})

        return payload['role']
    except Exception as e:
        return None


class Authentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            token = token.split(' ')[1]

            user = verify_token(token)
            if not user:
                raise exceptions.AuthenticationFailed('token is invalid')

            return user, None
        except Exception as e:
            raise exceptions.AuthenticationFailed('token is invalid')


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        token = token.split(' ')[1]

        role = get_role_in_token(token)

        if not role:
            raise exceptions.AuthenticationFailed('token is invalid')

        if 'Admin' in role or 'admin' in role:
            return True

        raise exceptions.AuthenticationFailed('you must have admin permission to perform this action')
