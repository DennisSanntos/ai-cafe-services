import os
import requests

BASEROW_TOKEN = os.getenv("BASEROW_API_TOKEN")
TABLE_ID = os.getenv("BASEROW_TABLE_ID", "621432")

BASE_URL = f"https://api.baserow.io/api/database/rows/table/{TABLE_ID}/"
HEADERS = {
    "Authorization": f"Token {BASEROW_TOKEN}",
    "Content-Type": "application/json"
}

def listar_reservas(limit=200):
    try:
        r = requests.get(BASE_URL, headers=HEADERS, params={"size": limit})
        if r.status_code == 200:
            return r.json()["results"]
        else:
            return {"erro": r.text}
    except Exception as e:
        return {"erro": str(e)}

def buscar_por_voucher(voucher):
    try:
        r = requests.get(BASE_URL, headers=HEADERS, params={
            "user_field_names": "true",
            "filter__voucher__equal": voucher
        })
        if r.status_code == 200:
            results = r.json()["results"]
            return results[0] if results else None
        return {"erro": r.text}
    except Exception as e:
        return {"erro": str(e)}

def atualizar_linha(row_id, campos: dict):
    try:
        r = requests.patch(f"{BASE_URL}{row_id}/", headers=HEADERS, json=campos)
        if r.status_code in [200, 204]:
            return {"status": "ok"}
        return {"erro": r.text}
    except Exception as e:
        return {"erro": str(e)}

def criar_linha(campos: dict, table_id=None):
    tid = table_id or TABLE_ID
    url = f"https://api.baserow.io/api/database/rows/table/{tid}/"
    try:
        r = requests.post(url, headers=HEADERS, json=campos)
        if r.status_code in [200, 201]:
            return r.json()
        return {"erro": r.text}
    except Exception as e:
        return {"erro": str(e)}

