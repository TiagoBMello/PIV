from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from pymongo import MongoClient
import numpy as np
from datetime import datetime

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
            "criada_em": datetime.utcnow()
        }
        db.metas.insert_one(meta)
        print(f"✅ Meta '{meta['nome']}' cadastrada para o usuário {meta['user_id']}.")
        return jsonify({"mensagem": "Meta cadastrada com sucesso."}), 201
    except Exception as e:
        print("❗ Erro ao cadastrar meta:", str(e))  # ← Aqui vamos ver o erro real no terminal
        return jsonify({"erro": "Erro ao cadastrar a meta."}), 500


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
    
from sklearn.linear_model import LinearRegression
import numpy as np

from sklearn.linear_model import LinearRegression
import numpy as np

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
            historico = sorted(meta.get("historico_aportes", []), key=lambda x: x["data"])

            progresso = round((acumulado / valor_total) * 100, 2)

            if len(historico) >= 2:
                # Preparar dados para regressão
                X = np.array(range(1, len(historico) + 1)).reshape(-1, 1)
                y = np.cumsum([h["valor"] for h in historico]).reshape(-1, 1)

                modelo = LinearRegression().fit(X, y)

                inclinacao = modelo.coef_[0][0]
                intercepto = modelo.intercept_[0]

                if inclinacao <= 0:
                    meses_estimados = "-"
                    recomendacao = valor_total - acumulado
                    status = "Atrasado"
                else:
                    passos_para_concluir = (valor_total - intercepto) / inclinacao
                    meses_estimados = max(0, round(passos_para_concluir - len(historico)))

                    status = "Em dia" if meses_estimados + len(historico) <= prazo else "Atrasado"

                    recomendacao = inclinacao  # valor médio estimado por aporte

            else:
                meses_estimados = "-"
                recomendacao = (valor_total - acumulado) if acumulado < valor_total else 0
                status = "Atrasado" if acumulado < valor_total else "Concluído"

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
        print("❗ Erro na análise:", str(e))
        return jsonify({"erro": str(e)}), 500



from dateutil.relativedelta import relativedelta

from sklearn.linear_model import LinearRegression

@app.route('/projecao', methods=['POST'])
def analisar_meta():
    try:
        dados = request.get_json()
        user_id = dados.get("user_id")
        nome_meta = dados.get("nome")

        meta = colecao_metas.find_one({"user_id": user_id, "nome": nome_meta})
        historico = sorted(meta.get("historico_aportes", []), key=lambda x: x["data"])

        if len(historico) < 2:
            return jsonify({"erro": "Pouco histórico para gerar a regressão."}), 400

        labels = []
        acumulado_ate_agora = []
        soma = 0

        for idx, h in enumerate(historico):
            label = f"Mês {idx + 1}"
            labels.append(label)

            soma += h["valor"]
            acumulado_ate_agora.append(round(soma, 2))

        # Dados para regressão
        X = np.array(range(1, len(acumulado_ate_agora) + 1)).reshape(-1, 1)
        y = np.array(acumulado_ate_agora).reshape(-1, 1)

        modelo = LinearRegression().fit(X, y)
        inclinacao = modelo.coef_[0][0]
        intercepto = modelo.intercept_[0]

        # Fazer projeção para mais 12 meses (ou aportes futuros)
        quantidade_futura = 12
        X_futuro = np.array(range(len(acumulado_ate_agora) + 1, len(acumulado_ate_agora) + quantidade_futura + 1)).reshape(-1, 1)
        y_futuro = modelo.predict(X_futuro).flatten().tolist()

        labels_futuro = [f"Mês {i}" for i in range(len(acumulado_ate_agora) + 1, len(acumulado_ate_agora) + quantidade_futura + 1)]

        return jsonify({
            "labels": labels,
            "acumulado": acumulado_ate_agora,
            "labels_futuro": labels_futuro,
            "acumulado_futuro": y_futuro,
            "inclinacao": round(inclinacao, 2),
            "intercepto": round(intercepto, 2)
        })

    except Exception as e:
        print("❗ Erro na projeção:", str(e))
        return jsonify({"erro": str(e)}), 500




@app.route('/dados_clusterizados')
def dados_clusterizados():
    try:
        # Buscar todas as respostas do quiz
        dados = list(colecao_quiz.find({}, {"_id": 0, "respostas": 1}))

        if len(dados) < 2:
            return jsonify({"erro": "Poucos dados para análise."}), 400

        # Extrair as respostas
        respostas_lista = [doc["respostas"] for doc in dados]
        X = np.array(respostas_lista)

        # Aplicar PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)

        # Aplicar KMeans
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(X_pca)
        labels = kmeans.labels_

        # Definir os nomes dos perfis
        nomes_perfil = ["Conservador", "Moderado", "Agressivo"]

        # Montar os dados para o gráfico
        pontos = []
        for (x, y), cluster, respostas in zip(X_pca, labels, respostas_lista):
            pontos.append({
                "x": float(x),
                "y": float(y),
                "cluster": int(cluster),
                "perfil": nomes_perfil[cluster],
                "respostas": respostas
            })

        return jsonify(pontos)

    except Exception as e:
        print("❗ Erro na rota /dados_clusterizados:", str(e))
        return jsonify({"erro": str(e)}), 500


@app.route('/metas/deletar/<user_id>/<nome_meta>', methods=['DELETE'])
def deletar_meta(user_id, nome_meta):
    try:
        resultado = colecao_metas.delete_one({"user_id": user_id, "nome": nome_meta})
        if resultado.deleted_count == 1:
            return jsonify({"mensagem": "Meta deletada com sucesso!"})
        else:
            return jsonify({"erro": "Meta não encontrada."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/metas/<user_id>/atualizar', methods=['POST'])
def atualizar_acumulado(user_id):
    try:
        dados = request.get_json()
        nome = dados.get("nome")
        valor = float(dados.get("valor"))

        resultado = colecao_metas.update_one(
            {"user_id": user_id, "nome": nome},
            {"$inc": {"acumulado": valor}}
        )

        if resultado.modified_count == 1:
            return jsonify({"mensagem": "Acumulado atualizado com sucesso."})
        else:
            return jsonify({"erro": "Meta não encontrada."}), 404

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Coleção de usuários
colecao_usuarios = db.usuarios

# Rota de cadastro de usuário
@app.route('/cadastrar', methods=['POST'])
def cadastrar_usuario():
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')

        if not nome or not email or not senha:
            return jsonify({"erro": "Todos os campos são obrigatórios."}), 400

        if colecao_usuarios.find_one({'email': email}):
            return jsonify({"erro": "Email já cadastrado."}), 400

        colecao_usuarios.insert_one({
            'nome': nome,
            'email': email,
            'senha': senha
        })

        return jsonify({"mensagem": "Usuário cadastrado com sucesso."}), 201

    except Exception as e:
        print('❗ Erro no cadastro:', str(e))
        return jsonify({"erro": "Erro ao cadastrar usuário."}), 500


# Rota de login
@app.route('/login', methods=['POST'])
def login():
    try:
        dados = request.get_json()
        email = dados.get('email')
        senha = dados.get('senha')

        usuario = colecao_usuarios.find_one({'email': email, 'senha': senha})
        if usuario:
            return jsonify({
                "mensagem": "Login realizado com sucesso.",
                "user_id": str(usuario["_id"]),
                "nome": usuario["nome"]
            })
        else:
            return jsonify({"erro": "Email ou senha incorretos."}), 401

    except Exception as e:
        print('❗ Erro no login:', str(e))
        return jsonify({"erro": "Erro no login."}), 500
    


@app.route('/historico', methods=['POST'])
def adicionar_ao_historico():
    try:
        dados = request.get_json()
        user_id = dados.get("user_id")
        nome = dados.get("nome")
        valor = float(dados.get("valor"))

        meta = colecao_metas.find_one({"user_id": user_id, "nome": nome})
        if not meta:
            return jsonify({"erro": "Meta não encontrada."}), 404

        historico = meta.get("historico_aportes", [])
        historico.append({
            "valor": valor,
            "data": datetime.utcnow().isoformat()
        })

        colecao_metas.update_one(
            {"user_id": user_id, "nome": nome},
            {"$set": {"historico_aportes": historico}}
        )

        return jsonify({"mensagem": "Aporte registrado no histórico."})
    except Exception as e:
        print('❗ Erro ao adicionar no histórico:', str(e))
        return jsonify({"erro": str(e)}), 500



# Inicia o servidor
if __name__ == '__main__':
    app.run(debug=True)
