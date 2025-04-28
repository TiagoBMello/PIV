from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

# Conexão com o MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["lia_database"]
usuarios = db["usuarios"]

# Função para cadastrar um novo usuário
def cadastrar_usuario(nome, email, senha):
    if usuarios.find_one({"email": email}):
        return {"erro": "Email já cadastrado!"}

    senha_hash = generate_password_hash(senha)
    usuarios.insert_one({
        "nome": nome,
        "email": email,
        "senha": senha_hash
    })
    return {"mensagem": "Usuário cadastrado com sucesso!"}

# Função para autenticar usuário
def autenticar_usuario(email, senha):
    usuario = usuarios.find_one({"email": email})
    if not usuario:
        return False

    if check_password_hash(usuario["senha"], senha):
        return True
    return False
