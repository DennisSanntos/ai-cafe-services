from flask import Blueprint, request, jsonify, render_template, redirect
import os
import json
from datetime import datetime

from app.tools.ingestor import processar_planilhas
from app.tools.baserow import buscar_por_voucher, listar_reservas
from app.chat.chat_cafe import iniciar_fluxo, processar_mensagem
from app.tools.reservas import get_contexto_reserva

main = Blueprint('main', __name__)
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

# CHAT IA SIMPLIFICADO
@main.route("/chat/ia", methods=["POST"])
def chat_ia():
    dados = request.get_json()
    reserva_id = dados.get("reserva_id")
    mensagem = dados.get("mensagem", "")

    if reserva_id not in respostas_parciais:
        respostas_parciais[reserva_id] = {}

    buffer = respostas_parciais[reserva_id]

    if mensagem == "__inicio__":
        return jsonify({"resposta": gerar_mensagem_checkbox(CAMPOS_ORDEM[0], OPCOES_PADRAO[CAMPOS_ORDEM[0]])})

    # Detecta se é resposta de checkbox
    try:
        payload = json.loads(mensagem)
        if isinstance(payload, dict) and "campo" in payload and "valor" in payload:
            buffer[payload["campo"]] = payload["valor"]
    except:
        pass

    # Se já respondeu tudo
    if all(c in buffer for c in CAMPOS_ORDEM):
        from app.chat.chat_cafe import salvar_preferencias
        salvar_preferencias(voucher=reserva_id, **buffer)
        return jsonify({"resposta": "Preferências registradas com sucesso! ☕ Obrigado!"})

    # Próxima pergunta
    for campo in CAMPOS_ORDEM:
        if campo not in buffer:
            return jsonify({"resposta": gerar_mensagem_checkbox(campo, OPCOES_PADRAO[campo])})

    return jsonify({"resposta": "Tudo certo."})

# GERA MENSAGEM COM CHECKBOX
def gerar_mensagem_checkbox(campo, opcoes):
    return f"""::checkbox::
campo={campo}
opcoes={json.dumps(opcoes, ensure_ascii=False)}
mensagem=Quais suas preferências para {campo.replace('_', ' ')}?"""


