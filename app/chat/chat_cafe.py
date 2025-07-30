from datetime import datetime
from app.tools.baserow import criar_linha

# ⚠️ Memória volátil (recarregamentos zeram isso)
estado_chat = {}  # {reserva_id: {"etapa": 0, "respostas": {...}, "contexto": {...}}}

PERGUNTAS = [
    {
        "campo": "frutas",
        "mensagem": "Quais frutas você gostaria de receber no seu café da manhã?",
        "opcoes": ["Mamão", "Melancia", "Banana", "Abacaxi", "Maçã", "Sem preferência"]
    },
    {
        "campo": "paes_salgados",
        "mensagem": "Tem algum tipo de pão ou salgado que você prefira?",
        "opcoes": ["Pão francês", "Croissant", "Pão de queijo", "Torrada", "Sem preferência"]
    },
    {
        "campo": "paes_sem_gluten",
        "mensagem": "Você gostaria de opções sem glúten?",
        "opcoes": ["Pão de mandioca", "Tapioca", "Pão sem glúten", "Sem necessidade"]
    },
    {
        "campo": "acompanhamentos",
        "mensagem": "Gostaria de algum acompanhamento específico?",
        "opcoes": ["Manteiga", "Requeijão", "Geleia", "Mel", "Nenhum"]
    },
    {
        "campo": "frios",
        "mensagem": "Tem preferência por algum frio?",
        "opcoes": ["Queijo branco", "Presunto", "Peito de peru", "Queijo prato", "Sem frios"]
    },
    {
        "campo": "bolos_doces",
        "mensagem": "Gostaria de incluir algo mais doce?",
        "opcoes": ["Bolo de cenoura", "Pão doce", "Rosquinha", "Sem doces"]
    }
]

def iniciar_fluxo(reserva_id, contexto):
    campo = "frutas"
    opcoes = ["Mamão", "Melancia", "Banana", "Abacaxi", "Maçã", "Sem preferência"]
    return f"""::checkbox:: 
campo={campo} 
opcoes={json.dumps(opcoes, ensure_ascii=False)} 
mensagem=Quais suas preferências para {campo}?"""


def processar_mensagem(reserva_id: str, mensagem: str) -> str:
    if reserva_id not in estado_chat:
        return "Reserva não iniciada. Recarregue a página."

    etapa = estado_chat[reserva_id]["etapa"]
    respostas = estado_chat[reserva_id]["respostas"]

    # Se for resposta estruturada (via checkbox)
    try:
        import json
        parsed = json.loads(mensagem)
        if isinstance(parsed, dict) and "campo" in parsed and "valor" in parsed:
            respostas[parsed["campo"]] = parsed["valor"]
            estado_chat[reserva_id]["etapa"] += 1
    except:
        pass  # Ignora mensagens livres por enquanto

    etapa = estado_chat[reserva_id]["etapa"]
    if etapa < len(PERGUNTAS):
        pergunta = PERGUNTAS[etapa]
        return f"""::checkbox::
campo={pergunta['campo']}
opcoes={pergunta['opcoes']}
mensagem={pergunta['mensagem']}
"""
    else:
        # Finaliza e salva
        return finalizar(reserva_id)

def finalizar(reserva_id: str) -> str:
    dados = estado_chat.pop(reserva_id, None)
    if not dados:
        return "Erro ao recuperar informações da reserva."

    contexto = dados["contexto"]
    respostas = dados["respostas"]

    payload = {
        "voucher": contexto.get("voucher"),
        "frutas": ", ".join(respostas.get("frutas", [])),
        "paes_salgados": ", ".join(respostas.get("paes_salgados", [])),
        "paes_sem_gluten": ", ".join(respostas.get("paes_sem_gluten", [])),
        "acompanhamentos": ", ".join(respostas.get("acompanhamentos", [])),
        "frios": ", ".join(respostas.get("frios", [])),
        "bolos_doces": ", ".join(respostas.get("bolos_doces", [])),
        "data_resposta": datetime.now().isoformat()
    }

    criar_linha(payload, table_id="622163", usar_mapa=True)

    return "✅ Suas preferências foram registradas com sucesso! Agradecemos por personalizar seu café conosco. 😊"
