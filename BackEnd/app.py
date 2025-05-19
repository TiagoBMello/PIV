from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from pymongo import MongoClient
import numpy as np
import datetime

app = Flask(__name__)
CORS(app)

# Conexão com o MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.lia_db
colecao_quiz = db.quiz_respostas
colecao_metas = db.metas  # ← MOVIDO para depois da definição do db

# Rota de previsão de saldo futuro
@app.route('/prever', methods=['POST'])
def prever():
    try:
        dados = request.get_json()
        valor_inicial = float(dados.get("valorInicial", 0))
        aporte_mensal = float(dados.get("aporteMensal", 0))
        taxa_juros = float(dados.get("taxaJuros", 0)) / 100
        duracao = int(dados.get("duracao", 0))

        valores = []
        saldo = valor_inicial

        for _ in range(duracao):
            saldo = saldo * (1 + taxa_juros) + aporte_mensal
            valores.append(round(saldo, 2))

        return jsonify({"valores": valores, "previsaoFinal": round(saldo, 2)})

    except Exception as e:
        print("❗ Erro na rota /prever:", str(e))
        return jsonify({"erro": "Erro ao processar previsão."}), 500

# Dicionário de dicas personalizadas
dicas_personalizadas = {
    "Conservador": {
        "base": {
            "descricao": "Você busca segurança e previsibilidade.",
            "detalhes": [
                "Monte sua reserva de emergência com liquidez diária.",
                "Priorize CDBs de grandes bancos e Tesouro Selic.",
                "Evite ativos com alta volatilidade, como ações e criptomoedas."
            ],
            "links": [
                {"titulo": "Como investir no Tesouro Direto", "url": "https://www.tesourodireto.com.br"},
                {"titulo": "O que é um CDB?", "url": "https://www.nubank.com.br/blog/o-que-e-cdb/"}
            ]
        },
        "subtipos": {
            "curto_prazo": {
                "condicao": lambda r: r[3] == 1,
                "extra": "Como seu foco é o curto prazo, prefira aplicações com vencimento em até 12 meses e liquidez diária."
            },
            "longa_duracao_estavel": {
                "condicao": lambda r: r[3] == 3 and r[4] == 2,
                "extra": "Mesmo conservador, seu perfil de longo prazo permite explorar LCIs e LCAs com isenção de IR."
            }
        }
    },
    "Moderado": {
        "base": {
            "descricao": "Você busca equilíbrio entre segurança e retorno, aceitando certa oscilação.",
            "detalhes": [
                "Combine Tesouro IPCA com fundos multimercado e FIIs.",
                "Diversifique em setores como energia, saúde e consumo.",
                "Explore ETFs como BOVA11 ou IVVB11."
            ],
            "links": [
                {"titulo": "Fundos Multimercado", "url": "https://www.infomoney.com.br/guias/fundos-multimercado/"},
                {"titulo": "Guia de FIIs", "url": "https://www.fundsexplorer.com.br/artigos/o-que-sao-fundos-imobiliarios/"}
            ]
        },
        "subtipos": {
            "foco_diversificacao": {
                "condicao": lambda r: r[2] == 2 and r[4] == 2,
                "extra": "Diversifique entre diferentes classes de ativos para diluir riscos sem abrir mão da rentabilidade."
            },
            "experiente_equilibrado": {
                "condicao": lambda r: r[2] == 3 and r[0] == 2,
                "extra": "Seu conhecimento permite balancear ações com renda fixa para estabilidade com ganho real."
            }
        }
    },
    "Agressivo": {
        "base": {
            "descricao": "Você tolera riscos elevados em busca de alta rentabilidade.",
            "detalhes": [
                "Explore small caps, criptomoedas e ETFs internacionais.",
                "Use TradingView para análise técnica.",
                "Considere setores como tecnologia e saúde digital."
            ],
            "links": [
                {"titulo": "Como investir em ações", "url": "https://www.tororadar.com.br/artigos/como-investir-em-acoes"},
                {"titulo": "Introdução ao Bitcoin", "url": "https://www.mercadobitcoin.com.br/bitcoin/"}
            ]
        },
        "subtipos": {
            "curioso_tecnologico": {
                "condicao": lambda r: r[2] == 3 and r[5] == 3,
                "extra": "Você pode se aprofundar em estratégias como value investing e criptoativos emergentes."
            },
            "investidor_global": {
                "condicao": lambda r: r[3] == 3 and r[1] == 3,
                "extra": "Considere diversificação internacional com ETFs como QQQ ou ARKK."
            }
        }
    }
}

# Rota para calcular perfil de investidor
@app.route('/perfil', methods=['POST'])
def calcular_perfil():
    try:
        dados = request.get_json(force=True)
        respostas = dados.get('respostas')
        user_id = dados.get('user_id')

        if not respostas or len(respostas) != 6:
            return jsonify({'erro': 'Respostas inválidas.'}), 400

        colecao_quiz.insert_one({"user_id": user_id, "respostas": respostas})

        todas_respostas = [doc["respostas"] for doc in colecao_quiz.find({}, {"_id": 0, "respostas": 1})]
        X = np.array(todas_respostas)

        if len(X) > 10:
            X = PCA(n_components=2).fit_transform(X)

        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(X)
        cluster = int(kmeans.predict([X[-1]])[0])

        nomes = ["Conservador", "Moderado", "Agressivo"]
        perfil_nome = nomes[cluster]
        dados_perfil = dicas_personalizadas[perfil_nome]["base"]
        mensagem_extra = ""

        for subtipo in dicas_personalizadas[perfil_nome]["subtipos"].values():
            if subtipo["condicao"](respostas):
                mensagem_extra = subtipo["extra"]
                break

        return jsonify({
            "perfil": perfil_nome,
            "descricao": dados_perfil["descricao"],
            "detalhes": dados_perfil["detalhes"],
            "extra": mensagem_extra,
            "links": dados_perfil["links"]
        })

    except Exception as e:
        print("❗ Erro interno:", str(e))
        return jsonify({'erro': 'Erro interno no servidor.'}), 500

# Rota para adicionar nova meta
@app.route('/metas', methods=['POST'])
def adicionar_meta():
    try:
        dados = request.get_json()
        meta = {
            "user_id": dados.get("user_id"),
            "nome": dados.get("nome"),
            "valor": float(dados.get("valor")),
            "prazo": int(dados.get("prazo")),
            "prioridade": dados.get("prioridade"),
            "acumulado": 0.0,
            "criada_em": datetime.datetime.utcnow()
        }
        colecao_metas.insert_one(meta)
        return jsonify({"mensagem": "Meta cadastrada com sucesso."}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rota para listar metas de um usuário
@app.route('/metas/<user_id>', methods=['GET'])
def listar_metas(user_id):
    try:
        metas = list(colecao_metas.find({"user_id": user_id}, {"_id": 0}))
        return jsonify(metas)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rota para aplicar contribuição mensal entre metas
@app.route('/metas/contribuir', methods=['POST'])
def contribuir_para_metas():
    try:
        dados = request.get_json()
        user_id = dados.get("user_id")
        valor_mensal = float(dados.get("valor_mensal"))

        metas = list(colecao_metas.find({"user_id": user_id}))
        if not metas:
            return jsonify({"erro": "Nenhuma meta encontrada."}), 404

        pesos = {"alta": 3, "media": 2, "baixa": 1}
        soma_pesos = sum(pesos[m["prioridade"]] / m["prazo"] for m in metas)

        for m in metas:
            peso = pesos[m["prioridade"]] / m["prazo"]
            contribuicao = (peso / soma_pesos) * valor_mensal
            novo_valor = m["acumulado"] + contribuicao

            colecao_metas.update_one(
                {"user_id": user_id, "nome": m["nome"]},
                {"$set": {"acumulado": round(novo_valor, 2)}}
            )

        return jsonify({"mensagem": "Contribuição mensal aplicada com sucesso."})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route('/metas/analise/<user_id>', methods=['GET'])
def analisar_progresso(user_id):
    try:
        hoje = datetime.utcnow()
        metas = list(colecao_metas.find({"user_id": user_id}, {"_id": 0}))
        analise = []

        for meta in metas:
            valor_total = meta["valor"]
            acumulado = meta.get("acumulado", 0)
            prazo = meta["prazo"]
            criada_em = meta["criada_em"]
            meses_passados = max(1, (hoje.year - criada_em.year) * 12 + hoje.month - criada_em.month)
            media_necessaria = valor_total / prazo
            media_atual = acumulado / meses_passados

            progresso = round((acumulado / valor_total) * 100, 2)
            status = "Em dia" if media_atual >= media_necessaria else "Atrasado"

            if status == "Atrasado":
                meses_estimados = int((valor_total - acumulado) / media_atual) if media_atual > 0 else "-"
                recomendacao = round((valor_total - acumulado) / (prazo - meses_passados), 2) if prazo > meses_passados else valor_total - acumulado
            else:
                meses_estimados = "-"
                recomendacao = media_necessaria

            analise.append({
                "nome": meta["nome"],
                "progresso": progresso,
                "status": status,
                "prazo": prazo,
                "estimativa_conclusao": meses_estimados,
                "guardar_recomendado": round(recomendacao, 2)
            })

        return jsonify(analise)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
    # Cole esse bloco ANTES do "if __name__ == '__main__':"

from sklearn.linear_model import LinearRegression

@app.route('/historico', methods=['POST'])
def registrar_historico():
    try:
        dados = request.get_json()
        user_id = dados.get("user_id")
        nome_meta = dados.get("nome")
        valor = float(dados.get("valor"))

        colecao_metas.update_one(
            {"user_id": user_id, "nome": nome_meta},
            {"$push": {"historico_aportes": {"valor": valor, "data": datetime.utcnow()}}}
        )
        return jsonify({"mensagem": "Histórico registrado."})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/projecao', methods=['POST'])
def analisar_meta():
    try:
        dados = request.get_json()
        user_id = dados.get("user_id")
        nome_meta = dados.get("nome")

        meta = colecao_metas.find_one({"user_id": user_id, "nome": nome_meta})
        historico = meta.get("historico_aportes", [])

        if len(historico) < 2:
            return jsonify({"erro": "Pouco histórico para projeção."}), 400

        valores = [h["valor"] for h in historico]
        acumulado = sum(valores)
        restante = meta["valor"] - acumulado

        X = np.array(range(1, len(valores)+1)).reshape(-1, 1)
        y = np.array(valores).reshape(-1, 1)

        modelo = LinearRegression().fit(X, y)
        media = modelo.coef_[0][0]

        meses_estimados = int(np.ceil(restante / media)) if media > 0 else -1
        recomendado = round(meta["valor"] / meta["prazo"], 2)

        return jsonify({
            "acumulado": round(acumulado, 2),
            "restante": round(restante, 2),
            "media_mensal": round(media, 2),
            "meses_estimados": meses_estimados,
            "recomendado_mensal": recomendado
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/dados_clusterizados')
def dados_clusterizados():
    dados = [doc["respostas"] for doc in colecao_quiz.find({}, {"_id": 0, "respostas": 1})]
    if len(dados) < 2:
        return jsonify({"erro": "Poucos dados para análise."}), 400

    X = np.array(dados)
    X_pca = PCA(n_components=2).fit_transform(X)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(X_pca)
    labels = kmeans.labels_

    pontos = [{"x": float(x), "y": float(y), "cluster": int(c)} for (x, y), c in zip(X_pca, labels)]
    return jsonify(pontos)


# Inicia o servidor
if __name__ == '__main__':
    app.run(debug=True)
