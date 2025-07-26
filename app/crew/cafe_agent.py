from crewai import Agent, Task
from app.tools.baserow import atualizar_linha
import os

class SalvarPreferenciasTool:
    def __init__(self):
        pass

    def run(self, preferencias: dict):
        """
        preferencias = {
            'voucher': '1941',
            'frutas': [...],
            'paes_salgados': [...],
            'paes_sem_gluten': [...],
            'acompanhamentos': [...],
            'frios': [...],
            'bolos_doces': [...]
        }
        """
        from app.tools.baserow import buscar_por_voucher
        reserva = buscar_por_voucher(preferencias.get("voucher"))
        if not reserva or "id" not in reserva:
            return {"erro": "Reserva não encontrada"}

        # Atualizar linha com preferências
        row_id = reserva["id"]
        campos = {
            "personalizacao_concluida": True,
            "frutas": ", ".join(preferencias.get("frutas", [])),
            "paes_salgados": ", ".join(preferencias.get("paes_salgados", [])),
            "paes_sem_gluten": ", ".join(preferencias.get("paes_sem_gluten", [])),
            "acompanhamentos": ", ".join(preferencias.get("acompanhamentos", [])),
            "frios": ", ".join(preferencias.get("frios", [])),
            "bolos_doces": ", ".join(preferencias.get("bolos_doces", []))
        }

        return atualizar_linha(row_id, campos)


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


