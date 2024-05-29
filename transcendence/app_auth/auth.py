# app_auth/auth.py

from django.contrib.auth.backends import BaseBackend
from app_auth.models import User
from app_auth.services import verify_jwt_token
import logging


# autentica um usuário usando o token JWT e as informações da Intra. Se o usuário não existir, cria um novo.
# obtém um usuário pelo ID.
class IntraAuthenticationBackend(BaseBackend):
    def authenticate(self, jwt_token, user_intra):
        if not isinstance(user_intra, dict):
            return None
        
        if jwt_token:
            user_data = verify_jwt_token(jwt_token)
            try:
                user = User.objects.get(username=user_data['id_42'])
            except User.DoesNotExist:
                user = User.objects.create_new_intra_user(user_intra)
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
