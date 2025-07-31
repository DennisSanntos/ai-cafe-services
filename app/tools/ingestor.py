import pandas as pd
from datetime import datetime, date
import os

from app.tools.baserow import criar_linha
from app.tools.field_map import FIELD_MAP_RESERVAS

CHAT_BASE_URL = os.getenv("CHAT_BASE_URL", "https://ai-cafe-services.onrender.com")


def processar_planilhas(path_periodo, path_apartamentos):
    # Leitura das planilhas
    df_periodo = pd.read_excel(path_periodo, sheet_name="Reservas")
    df_apto = pd.read_excel(path_apartamentos, sheet_name="Reservas por apartamento")

    # Renomeia colunas para nomes internos
    df_periodo = df_periodo.rename(columns={
        "Voucher": "voucher",
        "Hóspede principal": "nome_hospede",
        "Fone/Cel do contato": "telefone"
    })

    df_apto = df_apto.rename(columns={
        "Voucher": "voucher",
        "Apartamento": "apartamento",
        "Categoria de apartamento": "categoria_apartamento",
        "Hóspedes do apartamento": "hospedes_apartamento",
        "E-mail hóspede principal": "email_hospede",
        "Check-in": "checkin",
        "Check-out": "checkout"
    })

    # Merge apenas por 'voucher'
    df = pd.merge(df_apto, df_periodo[["voucher", "nome_hospede", "telefone"]], on="voucher", how="left")

    # Criação do campo reserva_id único por voucher + apartamento
    df["reserva_id"] = df.apply(lambda row: f"{row['voucher']}_{row['apartamento']}", axis=1)
    df["link_chat"] = df["reserva_id"].apply(lambda rid: f"{CHAT_BASE_URL}/chat?reserva_id={rid}")

    # Processa datas
    df["checkin"] = pd.to_datetime(df["checkin"]).dt.date
    df["checkout"] = pd.to_datetime(df["checkout"]).dt.date
    df["dias_para_checkin"] = df["checkin"].apply(lambda d: (d - datetime.now().date()).days)
    df["personalizacao_concluida"] = False

    # Campos esperados
    campos = [
        "reserva_id", "voucher", "nome_hospede", "telefone",
        "checkin", "checkout",
        "apartamento", "categoria_apartamento",
        "hospedes_apartamento", "email_hospede",
        "dias_para_checkin", "personalizacao_concluida", "link_chat"
    ]

    enviados, erros = 0, 0

    for _, row in df.iterrows():
        payload = {}
        for k in campos:
            if pd.notna(row.get(k)):
                valor = row[k]
                if isinstance(valor, (datetime, pd.Timestamp)):
                    valor = valor.date().isoformat()
                elif isinstance(valor, date):
                    valor = valor.isoformat()
                payload[k] = valor

        resultado = criar_linha(payload, table_id="621432", usar_mapa=True)

        if isinstance(resultado, dict) and resultado.get("erro"):
            print(f"❌ Erro no voucher {row.get('voucher', 'N/A')} - apto {row.get('apartamento')}: {resultado['erro']}")
            erros += 1
        else:
            enviados += 1

    return {
        "status": "concluido",
        "enviados": enviados,
        "erros": erros,
        "total": len(df)
    }

