from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from pymongo import MongoClient
from flask import Flask, request, jsonif
import numpy as np


# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.lia_db
colecao_quiz = db.quiz_respostas
app = Flask(__name__)

@app.route('/perfil', methods=['POST'])
def calcular_perfil():
    dados = request.get_json()
    respostas = dados.get('respostas')  # Lista de 6 respostas do quiz
    user_id = dados.get('user_id')

    if not respostas or len(respostas) != 6:
        return jsonify({'erro': 'Respostas inválidas.'}), 400

    # Salvar no MongoDB
    colecao_quiz.insert_one({
        "user_id": user_id,
        "respostas": respostas
    })

    # Coletar todas as respostas para treinar o modelo
    todas_respostas = [doc["respostas"] for doc in colecao_quiz.find({}, {"_id": 0, "respostas": 1})]
    X = np.array(todas_respostas)

    # Reduz dimensionalidade se necessário
    if len(X) > 10:
        X = PCA(n_components=2).fit_transform(X)

    # Clusterização com KMeans (3 perfis)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X)
    cluster = int(kmeans.predict([X[-1]])[0])

    # Mapear cluster para perfil
    perfis = {
        0: {
            "perfil": "Conservador",
            "descricao": "Foque em segurança: Tesouro Selic, CDBs grandes bancos.",
            "detalhes": [
                "Monte uma reserva de emergência (6 meses de despesas).",
                "Evite ativos voláteis como ações ou criptos.",
                "Reavalie sua carteira a cada 6 meses."
            ]
        },
        1: {
            "perfil": "Moderado",
            "descricao": "Equilibre FIIs, fundos multimercado e renda fixa.",
            "detalhes": [
                "Diversifique entre setores e prazos.",
                "Busque ativos que ofereçam rendimento mensal.",
                "Evite concentração em poucos ativos."
            ]
        },
        2: {
            "perfil": "Agressivo",
            "descricao": "Busque rentabilidade: ETFs, ações e criptos.",
            "detalhes": [
                "Invista com visão de longo prazo.",
                "Estude volatilidade e rebalanceamento.",
                "Alocar parte em mercados internacionais pode ajudar."
            ]
        }
    }

    return jsonify(perfis[cluster])
