from ninja.security import HttpBearer
from django.conf import settings
from django.contrib.auth import get_user_model
from jose import jwt, JWTError

User = get_user_model()


class TokenAuthentication(HttpBearer):
    # If this function returns any Value BUT None, means token is legit
    def authenticate(self, request, token):
        try:
            user_info = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=['HS256'])
            # user = User.objects.get(id=user_info['id'])
            return {'id': str(user_info['id']), 'is_verified': user_info['is_verified']}
        except JWTError:
            return None


# Password Reset
class PasswordResetTokenAuthentication(HttpBearer):
    def authenticate(self, request, token):
        try:
            user_info = jwt.decode(token=token, key=settings.SECOND_SECRET_KEY, algorithms=['HS256'])
        except JWTError:
            return None
        if user_info:
            return {'id': str(user_info['id']), 'is_verified': user_info['is_verified']}


def get_tokens_for_user(user, password_reset=False):
    user_details = {
        'id': str(user.id),
        'is_verified': user.is_verified
    }
    secret = settings.SECOND_SECRET_KEY if password_reset else settings.SECRET_KEY
    token = jwt.encode(user_details, key=secret, algorithm='HS256')
    return str(token)
