from crewai import Agent
from crewai.tools import tool
from datetime import datetime
from app.tools.baserow import criar_linha

# Define a Tool usando apenas o decorator do CrewAI
@tool
def salvar_preferencias(
    voucher: str,
    frutas: list[str] = [],
    paes_salgados: list[str] = [],
    paes_sem_gluten: list[str] = [],
    acompanhamentos: list[str] = [],
    frios: list[str] = [],
    bolos_doces: list[str] = []
) -> str:
    """
    Salva as preferências do hóspede no banco de dados.
    """
    payload = {
        "voucher": voucher,
        "frutas": ", ".join(frutas),
        "paes_salgados": ", ".join(paes_salgados),
        "paes_sem_gluten": ", ".join(paes_sem_gluten),
        "acompanhamentos": ", ".join(acompanhamentos),
        "frios": ", ".join(frios),
        "bolos_doces": ", ".join(bolos_doces),
        "data_resposta": datetime.now().isoformat()
    }

    return criar_linha(payload, table_id="622163", usar_mapa=True)


class CafeAgent(Agent):
    def __init__(self, contexto_reserva: dict):
        prompt = self._gerar_prompt(contexto_reserva)

        super().__init__(
            role="Agente de Café da Manhã",
            goal="Personalizar o café da manhã para o hóspede com base nas preferências",
            backstory="Você é um concierge digital especializado em entender preferências alimentares com empatia e clareza.",
            verbose=True,
            allow_delegation=False,
            tools=[salvar_preferencias],
            prompt=prompt  # ✅ aqui!
        )

    def _gerar_prompt(self, ctx):
        return f"""
Você está interagindo com {ctx.get('nome')} (quarto {ctx.get('quarto')}) para personalizar o café da manhã.

Coleta obrigatória:
- frutas
- pães e salgados
- pães sem glúten
- acompanhamentos
- frios
- bolos e doces

O estilo da conversa deve ser amigável, acolhedor e eficiente. Sempre confirme cada etapa.

Ao final, use a Tool `salvar_preferencias` com um dicionário contendo as escolhas. Não invente valores.

Identificador da reserva: {ctx.get("voucher")}
Check-in: {ctx.get("checkin")} – Checkout: {ctx.get("checkout")}
"""

