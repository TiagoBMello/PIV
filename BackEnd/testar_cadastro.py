import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mongo_handler import cadastrar_usuario

# Teste de cadastro
nome = "Tiago Teste"
email = "tiago@lia.com"
senha = "123456"

resultado = cadastrar_usuario(nome, email, senha)
print(resultado)
