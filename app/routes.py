from flask import Blueprint, request, jsonify, render_template, redirect
import os
import json
from datetime import datetime

from app.tools.ingestor import processar_planilhas
from app.tools.baserow import buscar_por_voucher, listar_reservas
from app.crew.crew_config import criar_crew_cafe

main = Blueprint('main', __name__)
agentes_chat = {}  # memória temporária para sessões
respostas_parciais = {}  # reserva_id -> respostas acumuladas

CAMPOS_ORDEM = [
    "frutas",
    "paes_salgados",
    "paes_sem_gluten",
    "acompanhamentos",
    "frios",
    "bolos_doces"
]

OPCOES_PADRAO = {
    "frutas": ["Mamão", "Melancia", "Banana", "Abacaxi", "Maçã", "Sem preferência"],
    "paes_salgados": ["Pão francês", "Croissant", "Pão de queijo", "Torrada", "Sem preferência"],
    "paes_sem_gluten": ["Pão de mandioca", "Tapioca", "Pão sem glúten", "Sem necessidade"],
    "acompanhamentos": ["Manteiga", "Requeijão", "Geleia", "Mel", "Nenhum"],
    "frios": ["Queijo branco", "Presunto", "Peito de peru", "Queijo prato", "Sem frios"],
    "bolos_doces": ["Bolo de cenoura", "Pão doce", "Rosquinha", "Sem doces"]
}

# HOME
@main.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "AI Café Services backend funcionando."
    })

# UPLOAD DE PLANILHAS
@main.route('/ingest', methods=['POST'])
def ingestar():
    if 'arquivo_periodo' not in request.files or 'arquivo_apto' not in request.files:
        return jsonify({"erro": "Envie os dois arquivos com os campos 'arquivo_periodo' e 'arquivo_apto'"}), 400

    file1 = request.files['arquivo_periodo']
    file2 = request.files['arquivo_apto']

    path1 = f"/tmp/{file1.filename}"
    path2 = f"/tmp/{file2.filename}"

    file1.save(path1)
    file2.save(path2)

    resultado = processar_planilhas(path1, path2)
    status = "ok" if resultado["erros"] == 0 else "parcial"
    return redirect(f"/painel?upload={status}&enviados={resultado['enviados']}&erros={resultado['erros']}")

# PAINEL HTML
@main.route('/painel')
def painel():
    reservas = listar_reservas()
    return render_template("painel.html", reservas=reservas)

# CHAT HTML
@main.route('/chat')
def chat():
    reserva_id = request.args.get("reserva_id")
    if not reserva_id:
        return "reserva_id ausente na URL", 400
    return render_template("chat.html")

# CONTEXTO DA RESERVA
@main.route('/chat/contexto')
def obter_contexto():
    reserva_id = request.args.get("reserva_id")
    dados = buscar_por_voucher(reserva_id)
    if not dados or "erro" in dados:
        return jsonify({"erro": "Reserva não encontrada"}), 404

    return jsonify({
        "nome": dados.get("nome_hospede_principal"),
        "quarto": dados.get("apartamento"),
        "checkin": dados.get("checkin"),
        "checkout": dados.get("checkout"),
        "voucher": dados.get("voucher")
    })

# CHAT IA
@main.route('/chat/ia', methods=['POST'])
def chat_ia():
    data = request.get_json()
    reserva_id = data.get("reserva_id")
    msg_usuario = data.get("mensagem")

    if not reserva_id or not msg_usuario:
        return jsonify({"erro": "Campos obrigatórios: reserva_id, mensagem"}), 400

    reserva = buscar_por_voucher(reserva_id)
    if not reserva:
        return jsonify({"erro": "Reserva não encontrada"}), 404

    # Inicia agente e buffer de respostas
    if reserva_id not in agentes_chat:
        contexto = {
            "nome": reserva.get("nome_hospede_principal"),
            "voucher": reserva.get("voucher"),
            "quarto": reserva.get("apartamento"),
            "checkin": reserva.get("checkin"),
            "checkout": reserva.get("checkout")
        }
        agentes_chat[reserva_id] = criar_crew_cafe(contexto)
        respostas_parciais[reserva_id] = {}

    buffer = respostas_parciais[reserva_id]

    # Detecta se é resposta de checkbox (JSON)
    try:
        dados = json.loads(msg_usuario)
        if isinstance(dados, dict) and "campo" in dados and "valor" in dados:
            campo = dados["campo"]
            buffer[campo] = dados["valor"]
    except:
        pass  # mensagem comum, ignora

    # Se já respondeu tudo
    if all(c in buffer for c in CAMPOS_ORDEM):
        agente = agentes_chat[reserva_id].agents[0]
        salvar_tool = agente.tools[0]

        resultado = salvar_tool.run({
            "voucher": reserva_id,
            **buffer
        })

        return jsonify({"resposta": "Preferências registradas com sucesso! ☕ Obrigado!"})

    # Próxima pergunta
    for campo in CAMPOS_ORDEM:
        if campo not in buffer:
            opcoes = OPCOES_PADRAO[campo]
            pergunta = gerar_mensagem_checkbox(campo, opcoes)
            return jsonify({"resposta": pergunta})

    return jsonify({"resposta": "Tudo certo."})

# GERA A MENSAGEM ESPECIAL DE CHECKBOX
def gerar_mensagem_checkbox(campo, opcoes):
    return f"""::checkbox::
campo={campo}
opcoes={json.dumps(opcoes)}
mensagem=Quais suas preferências para {campo.replace('_', ' ')}?"""
