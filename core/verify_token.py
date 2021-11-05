from django.conf import settings
import jwt


def verify_token(bearer_token):
    try:
        token = bearer_token.split()[1]
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=['HS256'])
        return True
    except Exception as e:
        return False
