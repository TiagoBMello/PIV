from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from pymongo import MongoClient
import numpy as np

app = Flask(__name__)
CORS(app)  # ← agora isso vai funcionar corretamente!

# Conexão com o MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.lia_db
colecao_quiz = db.quiz_respostas

@app.route('/perfil', methods=['POST'])
def calcular_perfil():
    try:
        dados = request.get_json(force=True)
        respostas = dados.get('respostas')
        user_id = dados.get('user_id')

        if not respostas or len(respostas) != 6:
            return jsonify({'erro': 'Respostas inválidas.'}), 400

        # Armazena as respostas
        colecao_quiz.insert_one({"user_id": user_id, "respostas": respostas})

        # Busca todas as respostas para clusterizar
        todas_respostas = [doc["respostas"] for doc in colecao_quiz.find({}, {"_id": 0, "respostas": 1})]
        X = np.array(todas_respostas)

        if len(X) > 10:
            X = PCA(n_components=2).fit_transform(X)

        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(X)
        cluster = int(kmeans.predict([X[-1]])[0])

        perfis = {
            0: {
                "perfil": "Conservador",
                "descricao": "Você valoriza segurança, previsibilidade e liquidez nos seus investimentos.",
                "detalhes": [
                    "Monte uma reserva de emergência com 6 meses de despesas.",
                    "Invista em CDBs de bancos grandes com liquidez diária.",
                    "Considere LCIs e LCAs com isenção de IR.",
                    "Evite ativos voláteis como ações ou criptomoedas.",
                    "Use corretoras seguras como NuInvest ou Itaú.",
                    "Avalie a carteira a cada 6 ou 12 meses.",
                    "Evite produtos com taxas de administração acima de 1% ao ano."
                ]
            },
            1: {
                "perfil": "Moderado",
                "descricao": "Você busca equilíbrio entre risco e retorno, aceitando pequenas oscilações.",
                "detalhes": [
                    "Combine Tesouro IPCA e Fundos Multimercado com FIIs.",
                    "Invista em ações blue chips como PETR4, ITUB4.",
                    "Diversifique entre setores como energia e consumo.",
                    "Use aportes mensais e rebalanceie semestralmente.",
                    "Explore ETFs como BOVA11 e IVVB11.",
                    "Utilize simuladores como Kinvo ou Grana Capital.",
                    "Mantenha disciplina e não reaja a quedas pequenas."
                ]
            },
            2: {
                "perfil": "Agressivo",
                "descricao": "Você está disposto a correr riscos para buscar maior rentabilidade.",
                "detalhes": [
                    "Invista em small caps e startups via Seedrs.",
                    "Explore criptos como Bitcoin e Ethereum (máx. 10% da carteira).",
                    "Use TradingView para análise técnica.",
                    "Avalie ETFs internacionais como QQQ, ARKK.",
                    "Estude estratégias como Value Investing.",
                    "Leia relatórios de casas como Suno e Empiricus.",
                    "Esteja preparado para oscilações fortes."
                ]
            }
        }

        return jsonify(perfis[cluster])
    
    except Exception as e:
        print("❗ Erro interno:", str(e))
        return jsonify({'erro': 'Erro interno no servidor.'}), 500

# Roda o servidor
if __name__ == '__main__':
    app.run(debug=True)
