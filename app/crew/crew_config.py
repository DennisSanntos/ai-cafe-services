from crewai import Crew, Task
from app.crew.cafe_agent import CafeAgent, SalvarPreferenciasTool


def criar_crew_cafe(contexto_reserva: dict):
    """
    Cria o Crew AI para processar uma personalização de café
    contexto_reserva = {
        'nome': 'João',
        'voucher': '1941',
        'quarto': 'UH 33',
        'checkin': '2025-07-29',
        'checkout': '2025-07-31'
    }
    """

    agente = CafeAgent(contexto_reserva)

    tarefa = Task(
        description="Conduza uma conversa gentil e objetiva para coletar as preferências de café da manhã do hóspede.",
        expected_output="""
Um dicionário JSON com os seguintes campos:

{
  'voucher': '...',
  'frutas': [...],
  'paes_salgados': [...],
  'paes_sem_gluten': [...],
  'acompanhamentos': [...],
  'frios': [...],
  'bolos_doces': [...]
}
""",
        agent=agente,
        tools=[SalvarPreferenciasTool()]
    )

    crew = Crew(
        agents=[agente],
        tasks=[tarefa],
        verbose=True,
        process="react"
    )

    return crew

