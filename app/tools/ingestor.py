import pandas as pd
import requests
from datetime import datetime
import os

# Carregar variáveis de ambiente
BASEROW_TOKEN = os.getenv("BASEROW_API_TOKEN")
TABLE_ID = os.getenv("BASEROW_TABLE_ID", "621432")
CHAT_BASE_URL = os.getenv("CHAT_BASE_URL", "https://chat.seusistema.com")

HEADERS = {
    "Authorization": f"Token {BASEROW_TOKEN}",
    "Content-Type": "application/json"
}
API_URL = f"https://api.baserow.io/api/database/rows/table/{TABLE_ID}/"

def processar_planilhas(path_periodo, path_apartamentos):
    df_periodo = pd.read_excel(path_periodo, sheet_name="Reservas")
    df_apto = pd.read_excel(path_apartamentos, sheet_name="Reservas por apartamento")

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

    # Merge dos dois
    df = pd.merge(df_apto, df_periodo[["voucher", "nome_hospede", "telefone"]], on="voucher", how="left")

    # Formatar campos
    df["checkin"] = pd.to_datetime(df["checkin"]).dt.date
    df["checkout"] = pd.to_datetime(df["checkout"]).dt.date
    df["dias_para_checkin"] = df["checkin"].apply(lambda d: (d - datetime.now().date()).days)
    df["personalizacao_concluida"] = False
    df["link_chat"] = df["voucher"].apply(lambda v: f"{CHAT_BASE_URL}/?reserva_id={v}")

    campos = [
        "voucher", "nome_hospede", "telefone",
        "checkin", "checkout",
        "apartamento", "categoria_apartamento",
        "hospedes_apartamento", "email_hospede",
        "dias_para_checkin", "personalizacao_concluida", "link_chat"
    ]

    enviados, erros = 0, 0

    for _, row in df.iterrows():
        payload = {k: row[k] for k in campos if pd.notna(row[k])}
        try:
            response = requests.post(API_URL, json=payload, headers=HEADERS, timeout=15)
            if response.status_code in [200, 201]:
                enviados += 1
            else:
                print(f"❌ Erro no voucher {row['voucher']}: {response.text}")
                erros += 1
        except Exception as e:
            print(f"⚠️ Falha ao enviar {row['voucher']}: {str(e)}")
            erros += 1

    return {
        "status": "concluido",
        "enviados": enviados,
        "erros": erros,
        "total": len(df)
    }

