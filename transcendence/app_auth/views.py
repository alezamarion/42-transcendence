import os
from django.shortcuts import redirect, render
from django.http import HttpRequest, JsonResponse
from django.contrib.auth import login, logout
from .services import exchange_code, generate_jwt_token
from .auth import IntraAuthenticationBackend


# renderiza a página de login e se o usuário já estiver autenticado, redireciona para a página de sucesso.
def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('app_auth:success')    

    auth_url = os.environ.get("AUTH_URL_INTRA")
    return render(request, 'app_auth/login.html', {'auth_url': auth_url}) #passa a url de intra para o template


# redireciona o usuário para a URL de autenticação da Intra.
def intra_login(request: HttpRequest):
    auth_url = os.environ.get("AUTH_URL_INTRA")
    return redirect(auth_url)


# callback para o redirecionamento da Intra 
# troca o código de autorização por informações do usuário, gera um token JWT, autentica o usuário
# e redireciona para a página de sucesso.
def intra_login_redirect(request: HttpRequest):
    code = request.GET.get("code")
    
    try:
        user_intra = exchange_code(code) 
        jwt_token = generate_jwt_token(user_intra)

        # se retona user, significa que autenticação na intra foi bem sucedida 
        # retorna instância de user definido em models.py
        user = IntraAuthenticationBackend().authenticate(   
            jwt_token=jwt_token, user_intra=user_intra
        )

        if user:
            # loga usuário no projeto: salva id de usuário na sessão
            login(request, user, "app_auth.auth.IntraAuthenticationBackend") # salva cookie sessionid
            response = redirect("app_auth:success")
            response.set_cookie("jwt_token", jwt_token, httponly=True, samesite="Lax") # cookie com JWT token gerado, pode ser usado para auth em solicitações subsequentes
            return response
        else:
            return JsonResponse({"error": "Authentication failed"}, status=401)
    except Exception as e:
        print(f"Error during authentication: {e}")
        return JsonResponse({"error": "Authentication failed"}, status=401)


# renderiza a página de sucesso após a autenticação bem-sucedida.
def success_view(request: HttpRequest):
    return render(request, 'app_auth/success.html')


# encerra a sessão do usuário, remove os cookies de autenticação e redireciona para a página de login.
def logout_view(request):
    print("Logging out user:", request.user)
    logout(request)  # encerra a sessão do usuário no Django
    response = redirect('app_auth:login')  
    response.delete_cookie('jwt_token')  
    response.delete_cookie('sessionid')  
    request.session.flush()  # adicionalmente, limpa a sessão do usuário

    # Remover cookies específicos da Intra
    cookies_to_delete = ['_intra_42_session_production', '_mkra_stck', 'intra', 'locale', 'user.id']
    for cookie in cookies_to_delete:
        response.delete_cookie(cookie)
        print(f"Cookie {cookie} deleted")  # Debug

    return response


