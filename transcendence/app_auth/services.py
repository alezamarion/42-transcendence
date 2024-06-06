import os
import requests
import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings

# usa código de autorização para obter informações do usuário
def exchange_code(code: str):
    access_token = get_access_token(code)
    user_info = get_user_info(access_token)
    return user_info


# troca um código de autorização por um token de acesso usando a API da Intra.
def get_access_token(code: str):
    data = {
        "grant_type": "authorization_code",
        "client_id": os.environ.get("CLIENT_ID"),
        "client_secret": os.environ.get("CLIENT_SECRET"),
        "code": code,
        "redirect_uri": os.environ.get("REDIRECT_URI"),
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = requests.post("https://api.intra.42.fr/oauth/token", data=data, headers=headers)
    
    if response.status_code != 200:
        raise Exception("Failed to exchange code for token")    
    token_info = response.json()

    return token_info['access_token']


# obtém as informações do usuário usando o token de acesso da Intra.
def get_user_info(access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get("https://api.intra.42.fr/v2/me", headers=headers)
    
    if response.status_code != 200:
        raise Exception("Failed to get user info")
    
    user_info = response.json()
    return user_info


# gera um token JWT a partir das informações do usuário.
def generate_jwt_token(user_data):
    payload = {
        'id_42':  user_data['id'],
        'exp': datetime.now(timezone.utc) + timedelta(days=10),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')



class JWTVerificationFailed(Exception):
    pass

# verifica a validade de um token JWT.
def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise JWTVerificationFailed("Token has expired")
    except jwt.InvalidTokenError:
        raise JWTVerificationFailed("Invalid token")
    except Exception:
        raise JWTVerificationFailed("An unexpected error occurred during JWT verification")

