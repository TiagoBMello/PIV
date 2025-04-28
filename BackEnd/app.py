from flask import Flask, request, jsonify
from flask_cors import CORS
from mongo_handler import cadastrar_usuario, autenticar_usuario

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "<h1>✅ API do LIA está funcionando!</h1>"

@app.route("/cadastro", methods=["POST"])
def rota_cadastro():
    dados = request.json
    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")

    resultado = cadastrar_usuario(nome, email, senha)
    return jsonify(resultado)

@app.route("/login", methods=["POST"])
def rota_login():
    dados = request.json
    email = dados.get("email")
    senha = dados.get("senha")

    if autenticar_usuario(email, senha):
        return jsonify({"mensagem": "Login realizado com sucesso!"})
    return jsonify({"erro": "Credenciais inválidas"}), 401

if __name__ == "__main__":
    app.run(debug=True)
