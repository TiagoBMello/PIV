import random

def gerar_quiz():
    perguntas = [
        {
            "pergunta": "O que é um ativo financeiro?",
            "opcoes": ["Algo que gera receita", "Um passivo da empresa"],
            "resposta": "Algo que gera receita"
        },
        {
            "pergunta": "O que é inflação?",
            "opcoes": ["Aumento do poder de compra", "Aumento geral dos preços"],
            "resposta": "Aumento geral dos preços"
        },
        {
            "pergunta": "Para que serve uma reserva de emergência?",
            "opcoes": ["Para pagar dívidas longas", "Para cobrir imprevistos"],
            "resposta": "Para cobrir imprevistos"
        },
        {
            "pergunta": "O que são juros compostos?",
            "opcoes": ["Juros sobre o valor inicial", "Juros sobre juros acumulados"],
            "resposta": "Juros sobre juros acumulados"
        },
        {
            "pergunta": "O que é diversificação de investimentos?",
            "opcoes": ["Investir em um único ativo", "Distribuir investimentos em várias opções"],
            "resposta": "Distribuir investimentos em várias opções"
        }
    ]
    random.shuffle(perguntas)
    return perguntas[:5]
