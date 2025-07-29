from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel
from datetime import datetime
from app.tools.baserow import criar_linha

# Schema para validação de entrada
class PreferenciasInput(BaseModel):
    voucher: str
    frutas: Optional[list[str]] = []
    paes_salgados: Optional[list[str]] = []
    paes_sem_gluten: Optional[list[str]] = []
    acompanhamentos: Optional[list[str]] = []
    frios: Optional[list[str]] = []
    bolos_doces: Optional[list[str]] = []

class SalvarPreferenciasTool(BaseTool):
    name: str = "salvar_preferencias"
    description: str = "Salva as preferências do hóspede no Baserow"
    args_schema: Type[BaseModel] = PreferenciasInput

    def _run(self, voucher, frutas=None, paes_salgados=None, paes_sem_gluten=None,
             acompanhamentos=None, frios=None, bolos_doces=None):
        payload = {
            "voucher": voucher,
            "frutas": ", ".join(frutas or []),
            "paes_salgados": ", ".join(paes_salgados or []),
            "paes_sem_gluten": ", ".join(paes_sem_gluten or []),
            "acompanhamentos": ", ".join(acompanhamentos or []),
            "frios": ", ".join(frios or []),
            "bolos_doces": ", ".join(bolos_doces or []),
            "data_resposta": datetime.now().isoformat()
        }

        return criar_linha(payload, table_id="622163", usar_mapa=True)

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async não suportado")



class CafeAgent(Agent):
    def __init__(self, contexto_reserva: dict):
        """
        contexto_reserva = {
            'nome': 'João Silva',
            'voucher': '1941',
            'quarto': 'UH 22',
            'checkin': '2025-07-28',
            'checkout': '2025-07-30'
        }
        """
        prompt = self._gerar_prompt(contexto_reserva)

        tool = SalvarPreferenciasTool()

        super().__init__(
            role="Agente de Café da Manhã",
            goal="Personalizar o café da manhã para o hóspede com base nas preferências",
            backstory="Você é um concierge digital especializado em entender preferências alimentares com empatia e clareza.",
            verbose=True,
            allow_delegation=False,
            tools=[tool]
        )
        self.prompt = prompt

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

Ao final, use a Tool `SalvarPreferenciasTool` com um dicionário contendo as escolhas. Não invente valores.

Identificador da reserva: {ctx.get("voucher")}
Check-in: {ctx.get("checkin")} – Checkout: {ctx.get("checkout")}
"""


