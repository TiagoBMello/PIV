from datetime import datetime
from pymongo import MongoClient
import pprint

# Conexão com MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.lia_db
colecao_metas = db.metas

user_id = "usuario123"  # Pode ser ajustado dinamicamente

# Inserir metas
def inserir_metas():
    metas = [
        {
            "user_id": user_id,
            "nome": "Viagem para o Nordeste",
            "valor": 4000,
            "prazo": 8,
            "prioridade": "alta",
            "acumulado": 0,
            "criada_em": datetime.utcnow()
        },
        {
            "user_id": user_id,
            "nome": "Notebook novo",
            "valor": 3000,
            "prazo": 12,
            "prioridade": "media",
            "acumulado": 0,
            "criada_em": datetime.utcnow()
        }
    ]
    colecao_metas.insert_many(metas)
    print("✅ Metas inseridas com sucesso!")

# Listar metas
def listar_metas():
    print("📋 Metas do usuário:")
    metas = list(colecao_metas.find({"user_id": user_id}, {"_id": 0}))
    pprint.pprint(metas)

# Editar meta
def editar_meta(nome_meta, novo_valor, novo_prazo):
    resultado = colecao_metas.update_one(
        {"user_id": user_id, "nome": nome_meta},
        {"$set": {"valor": novo_valor, "prazo": novo_prazo}}
    )
    if resultado.modified_count:
        print(f"✏️ Meta '{nome_meta}' atualizada!")
    else:
        print(f"⚠️ Meta '{nome_meta}' não encontrada ou sem alterações.")

# Deletar meta
def deletar_meta(nome_meta):
    resultado = colecao_metas.delete_one({"user_id": user_id, "nome": nome_meta})
    if resultado.deleted_count:
        print(f"🗑️ Meta '{nome_meta}' deletada!")
    else:
        print(f"⚠️ Meta '{nome_meta}' não encontrada.")

# Executar testes apenas se rodar diretamente
if __name__ == "__main__":
    inserir_metas()
    listar_metas()
    editar_meta("Notebook novo", 2500, 10)
    listar_metas()
    deletar_meta("Viagem para o Nordeste")
    listar_metas()
