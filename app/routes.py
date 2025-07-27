from flask import Blueprint, request, jsonify, render_template, redirect
import os
from datetime import datetime
from app.tools.ingestor import processar_planilhas
from app.tools.baserow import buscar_por_voucher, listar_reservas
from app.crew.crew_config import criar_crew_cafe

main = Blueprint('main', __name__)
agentes_chat = {}  # memória temporária para sessões

@main.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "AI Café Services backend funcionando."
    })

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


@main.route('/painel')
def painel():
    reservas = listar_reservas()
    return render_template("painel.html", reservas=reservas)


# RENDERIZA O CHAT HTML
@main.route('/chat')
def chat():
    reserva_id = request.args.get("reserva_id")
    if not reserva_id:
        return "reserva_id ausente na URL", 400
    return render_template("chat.html")


# CONSULTA DADOS DE CONTEXTO DA RESERVA
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


# CHAT IA VIA POST
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

    if reserva_id not in agentes_chat:
        contexto = {
            "nome": reserva.get("nome_hospede_principal"),
            "voucher": reserva.get("voucher"),
            "quarto": reserva.get("apartamento"),
            "checkin": reserva.get("checkin"),
            "checkout": reserva.get("checkout")
        }
        agentes_chat[reserva_id] = criar_crew_cafe(contexto)

    crew = agentes_chat[reserva_id]
    resposta = crew.chat(msg_usuario)
    return jsonify({"resposta": resposta})

