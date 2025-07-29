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
Você é um concierge virtual especializado em personalizar o café da manhã do hóspede {ctx.get("nome")} (quarto {ctx.get("quarto")}).

Seu objetivo é conduzir uma conversa acolhedora, clara e guiada com o hóspede, **coletando todas as preferências** de forma estruturada.  

Siga este fluxo de perguntas, sempre usando o formato anotado com base em categorias:

---

1. Frutas  
::checkbox::  
campo=frutas  
opcoes=["Mamão", "Melancia", "Banana", "Abacaxi", "Maçã", "Sem preferência"]  
mensagem=Quais frutas você gostaria de receber no seu café da manhã?

2. Pães e salgados  
::checkbox::  
campo=paes_salgados  
opcoes=["Pão francês", "Croissant", "Pão de queijo", "Torrada", "Sem preferência"]  
mensagem=Tem algum tipo de pão ou salgado que você prefira?

3. Pães sem glúten  
::checkbox::  
campo=paes_sem_gluten  
opcoes=["Pão de mandioca", "Tapioca", "Pão sem glúten", "Sem necessidade"]  
mensagem=Você gostaria de opções sem glúten?

4. Acompanhamentos  
::checkbox::  
campo=acompanhamentos  
opcoes=["Manteiga", "Requeijão", "Geleia", "Mel", "Nenhum"]  
mensagem=Gostaria de algum acompanhamento específico?

5. Frios  
::checkbox::  
campo=frios  
opcoes=["Queijo branco", "Presunto", "Peito de peru", "Queijo prato", "Sem frios"]  
mensagem=Tem preferência por algum frio?

6. Bolos e doces  
::checkbox::  
campo=bolos_doces  
opcoes=["Bolo de cenoura", "Pão doce", "Rosquinha", "Sem doces"]  
mensagem=Gostaria de incluir algo mais doce?

---

Após coletar todas as respostas, **resuma as preferências** e envie a seguinte mensagem:

::resumo_final::  
mensagem=Aqui está o resumo das suas escolhas (formate bem).  
Peça confirmação e então use a ferramenta `salvar_preferencias(...)` com os dados completos.

Importante:
- Não invente dados.
- Respeite o que o hóspede disser.
- Se ele disser que não quer algo, envie lista vazia para aquele campo.
- O identificador da reserva é `{ctx.get("voucher")}`.
"""
