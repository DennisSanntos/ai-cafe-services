def get_contexto_reserva(reserva: dict) -> dict:
    return {
        "voucher": reserva.get("voucher"),
        "nome": reserva.get("nome_hospede_principal"),
        "quarto": reserva.get("apartamento"),
        "checkin": reserva.get("checkin"),
        "checkout": reserva.get("checkout")
    }
