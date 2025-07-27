from flask import Blueprint, request, jsonify, render_template
import os
from app.tools.ingestor import processar_planilhas
from app.tools.baserow import buscar_por_voucher
from app.crew.crew_config import criar_crew_cafe

main = Blueprint('main', __name__)

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
    return jsonify(resultado)

@main.route('/chat')
def chat():
    reserva_id = request.args.get("reserva_id")
    if not reserva_id:
        return "reserva_id ausente na URL", 400

    reserva = buscar_por_voucher(reserva_id)
    if not reserva or "nome_hospede" not in reserva:
        return "Reserva não encontrada", 404

    return render_template("chat.html", reserva=reserva)

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

    contexto = {
        "nome": reserva.get("nome_hospede"),
        "voucher": reserva.get("voucher"),
        "quarto": reserva.get("apartamento"),
        "checkin": reserva.get("checkin"),
        "checkout": reserva.get("checkout")
    }

    crew = criar_crew_cafe(contexto)
    resposta = crew.chat(msg_usuario)

    return jsonify({"resposta": resposta})

@main.route('/painel')
def painel():
    from app.tools.baserow import listar_reservas
    reservas = listar_reservas()
    return render_template("painel.html", reservas=reservas)

