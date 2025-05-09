from flask import Flask, request, jsonify
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from pymongo import MongoClient
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ← importante para permitir chamadas do navegador


# Inicializa Flask
app = Flask(__name__)

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.lia_db
colecao_quiz = db.quiz_respostas

# Rota para calcular o perfil
@app.route('/perfil', methods=['POST'])
def calcular_perfil():
    try:
        dados = request.get_json(force=True)
        print("🔍 Dados recebidos:", dados)

        respostas = dados.get('respostas')
        user_id = dados.get('user_id')

        if not respostas or len(respostas) != 6:
            print("❌ Respostas inválidas:", respostas)
            return jsonify({'erro': 'Respostas inválidas.'}), 400

        # resto do código continua normalmente...

        # (retorno final do perfil fica depois)
    
    except Exception as e:
        print("❗ Erro interno na rota /perfil:", str(e))
        return jsonify({'erro': 'Erro interno no servidor.'}), 500


    # Coletar todas as respostas
    todas_respostas = [doc["respostas"] for doc in colecao_quiz.find({}, {"_id": 0, "respostas": 1})]
    X = np.array(todas_respostas)

    # Aplicar PCA se necessário
    if len(X) > 10:
        X = PCA(n_components=2).fit_transform(X)

    # Clusterização
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X)
    cluster = int(kmeans.predict([X[-1]])[0])

    # Perfis
    perfis = {
        0: {
            "perfil": "Conservador",
            "descricao": "Você valoriza segurança, previsibilidade e liquidez nos seus investimentos.",
            "detalhes": [
                "Monte uma reserva de emergência com 6 meses de despesas em Tesouro Selic.",
                "Invista em CDBs de bancos grandes com liquidez diária.",
                "Considere LCIs e LCAs para isenção de IR em renda fixa.",
                "Evite ativos voláteis como ações ou criptomoedas.",
                "Use corretoras seguras como NuInvest ou Itaú para acompanhar seus rendimentos.",
                "Avalie sua carteira a cada 6 ou 12 meses com foco em estabilidade.",
                "Evite produtos com taxa de administração acima de 1% ao ano."
            ]
        },
        1: {
            "perfil": "Moderado",
            "descricao": "Você busca equilíbrio entre risco e retorno, aceitando pequenas oscilações.",
            "detalhes": [
                "Combine Tesouro IPCA e Fundos Multimercado com Fundos Imobiliários (FIIs).",
                "Invista parte em ações blue chips como PETR4, ITUB4.",
                "Diversifique entre setores (financeiro, energia, consumo).",
                "Use aportes mensais e rebalanceie a carteira semestralmente.",
                "Explore ETFs como BOVA11 e IVVB11.",
                "Utilize simuladores como Kinvo ou Grana Capital para visualizar metas.",
                "Mantenha disciplina e não reaja emocionalmente a quedas pequenas."
            ]
        },
        2: {
            "perfil": "Agressivo",
            "descricao": "Você está disposto a correr riscos para buscar maior rentabilidade.",
            "detalhes": [
                "Invista em ações de crescimento, small caps e startups via Seedrs.",
                "Explore criptomoedas como Bitcoin e Ethereum com até 10% da carteira.",
                "Utilize ferramentas como TradingView para análise técnica.",
                "Avalie aportes em ETFs internacionais (QQQ, ARKK).",
                "Estude estratégias como Buy and Hold e Value Investing.",
                "Acompanhe relatórios de casas de análise (Ex: Suno, Empiricus).",
                "Esteja preparado para fortes oscilações e mantenha foco no longo prazo."
            ]
        }
    }

    return jsonify(perfis[cluster])

# Iniciar servidor
if __name__ == "__main__":
    app.run(debug=True)
