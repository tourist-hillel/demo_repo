import jwt
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

JWT_SETTINGS = getattr(settings, 'SIMPLE_JWT', {})
ACCESS_TOKEN_LIFETIME = JWT_SETTINGS.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=2))
REFRESH_TOKEN_LIFETIME = JWT_SETTINGS.get('REFRESH_TOKEN_LIFETIME', timedelta(minutes=6))

def create_access_token(user):
    return jwt.encode({
        'user_id': user.id,
        'cell_phone': user.cell_phone,
        'exp': timezone.now() + ACCESS_TOKEN_LIFETIME,
        'iat': timezone.now(),
        'token_type': 'access'
    }, settings.SECRET_KEY, algorithm='HS256')


def create_refresh_token(user):
    return jwt.encode({
        'user_id': user.id,
        'exp': timezone.now() + REFRESH_TOKEN_LIFETIME,
        'iat': timezone.now(),
        'token_type': 'refresh'
    }, settings.SECRET_KEY, algorithm='HS256')
