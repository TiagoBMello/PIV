import sys
import os

# Adiciona o diretório atual no path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mongo_handler import autenticar_usuario

# Teste de login
email = "tiago@lia.com"    # mesmo email que você cadastrou
senha = "123456"           # mesma senha que você cadastrou

resultado = autenticar_usuario(email, senha)
print("Login bem-sucedido!" if resultado else "Falha no login!")
