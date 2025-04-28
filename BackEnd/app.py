# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from mongo_handler import cadastrar_usuario, autenticar_usuario

# Inicializa o Flask
app = Flask(__name__)
CORS(app)  # Libera o acesso entre front-end e back-end

# -------------------------------
# Rota padrão para testar a API
@app.route('/')
def home():
    return '<h1>✅ API do LIA está rodando!</h1>'

# -------------------------------
# Rota para cadastrar um novo usuário
@app.route('/cadastrar', methods=['POST'])
def rota_cadastrar():
    dados = request.get_json()

    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({'erro': 'Todos os campos são obrigatórios!'}), 400

    resultado = cadastrar_usuario(nome, email, senha)

    if 'erro' in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 201

# -------------------------------
# Rota para autenticar/login do usuário
@app.route('/login', methods=['POST'])
def rota_login():
    dados = request.get_json()

    email = dados.get('email')
    senha = dados.get('senha')

    if not email or not senha:
        return jsonify({'erro': 'Todos os campos são obrigatórios!'}), 400

    autenticado = autenticar_usuario(email, senha)

    if autenticado:
        return jsonify({'mensagem': 'Login realizado com sucesso!'}), 200
    else:
        return jsonify({'erro': 'Email ou senha incorretos!'}), 401

# -------------------------------
# Executa o app Flask
if __name__ == "__main__":
    app.run(debug=True)
