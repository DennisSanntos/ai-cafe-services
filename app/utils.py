from datetime import datetime, date
import hashlib

def calcular_dias_para_checkin(data_checkin: date) -> int:
    """Retorna o número de dias entre hoje e o check-in"""
    hoje = datetime.now().date()
    return (data_checkin - hoje).days

def normalizar_lista(lista: list) -> str:
    """Converte uma lista de itens em string separada por vírgula"""
    return ", ".join(lista) if isinstance(lista, list) else str(lista)

def gerar_token_reserva(voucher: str) -> str:
    """Gera um hash curto a partir do voucher para usar como ID de chat"""
    return hashlib.sha256(voucher.encode()).hexdigest()[:10]

def gerar_link_chat(voucher: str, base_url: str) -> str:
    """Monta o link de chat com ID gerado"""
    token = gerar_token_reserva(voucher)
    return f"{base_url}/chat?reserva_id={voucher}"

def formatar_data_br(data_str):
    """Converte '2025-07-28' para '28/07/2025'"""
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return data_str

