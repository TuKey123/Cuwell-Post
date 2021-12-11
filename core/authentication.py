from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework import exceptions
from django.conf import settings
import jwt


def verify_token(token):
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=['HS256'], options={'verify_aud': False})

        return payload
    except Exception as e:
        return None


def get_data_in_token(request):
    try:
        token = request.META.get('HTTP_AUTHORIZATION')
        token = token.split(' ')[1]

        data = verify_token(token)
        return data

    except Exception as e:
        return None


class Authentication(BaseAuthentication):
    def authenticate(self, request):
        data = get_data_in_token(request)

        if not data:
            raise exceptions.AuthenticationFailed('token is invalid')

        return data['user']


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        data = get_data_in_token(request)

        if not data:
            raise exceptions.AuthenticationFailed('token is invalid')

        role = data['role']

        if 'Admin' in role or 'admin' in role:
            return True

        raise exceptions.AuthenticationFailed('you must have admin permission to perform this action')

