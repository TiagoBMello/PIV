from flask import Flask, request, jsonify
from flask_cors import CORS
from mongo_handler import cadastrar_usuario, autenticar_usuario

# Para predição
import numpy as np
from sklearn.linear_model import LinearRegression

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
# Rota para previsão de saldo com regressão linear
@app.route('/prever', methods=['POST'])
def prever_saldo():
    dados = request.get_json()

    try:
        valor_inicial = float(dados['valorInicial'])
        aporte_mensal = float(dados['aporteMensal'])
        taxa_juros = float(dados['taxaJuros']) / 100
        meses = int(dados['duracao'])

        valores = []
        saldo = valor_inicial

        for i in range(meses + 1):
            valores.append(saldo)
            saldo = (saldo + aporte_mensal) * (1 + taxa_juros)

        X = np.array(range(len(valores))).reshape(-1, 1)
        y = np.array(valores).reshape(-1, 1)

        modelo = LinearRegression()
        modelo.fit(X, y)

        previsao_final = modelo.predict([[meses]])[0][0]

        return jsonify({
            'valores': valores,
            'previsaoFinal': round(previsao_final, 2)
        })
    except Exception as e:
        return jsonify({'erro': f'Erro na previsão: {str(e)}'}), 500

# -------------------------------
# Executa o app Flask
if __name__ == "__main__":
    app.run(debug=True)
