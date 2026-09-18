import jwt
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

User = get_user_model()
JWT_SETTINGS = getattr(settings, 'SIMPLE_JWT', {})



class EventsAppJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION')
        if not header:
            return None

        try:
            prefix, token = header.split()
        except ValueError:
            raise AuthenticationFailed('Wrong header')

        if prefix not in JWT_SETTINGS.get('AUTH_HEADER_TYPES', ('Bearer',)):
            return None

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!!!', code='token_expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token!', code='invalid_token')

        if payload.get('token_type') != 'access':
            raise AuthenticationFailed('Wrong type', code='wrong_token_type')

        try:
            user = User.objects.get(id=payload['user_id'], cell_phone=payload['cell_phone'], is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed('No user mathces given info')

        return (user, token)
