from crewai import Crew, Task
from app.crew.cafe_agent import CafeAgent, salvar_preferencias

def criar_crew_cafe(contexto_reserva: dict):
    agente = CafeAgent(contexto_reserva)

    tarefa = Task(
        description="Conduza uma conversa gentil e objetiva para coletar as preferências de café da manhã do hóspede.",
        expected_output="""{
  'voucher': '...',
  'frutas': [...],
  'paes_salgados': [...],
  'paes_sem_gluten': [...],
  'acompanhamentos': [...],
  'frios': [...],
  'bolos_doces': [...]
}""",
        agent=agente,
        tools=[salvar_preferencias]
    )

    crew = Crew(
        agents=[agente],
        tasks=[tarefa],
        verbose=True,
        process="sequential"
    )

    return crew

