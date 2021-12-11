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
