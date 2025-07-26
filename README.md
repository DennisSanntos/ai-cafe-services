🏨 AI Café Services
Sistema inteligente de personalização de café da manhã para hotelaria, usando IA com CrewAI e integração com Baserow.

🚀 Visão Geral
O sistema permite que hóspedes personalizem seu café da manhã antes do check-in via um link único enviado por WhatsApp. As respostas são processadas por um agente IA e armazenadas automaticamente no Baserow. Um painel administrativo permite acompanhar o status de cada reserva.

🛠️ Tecnologias Utilizadas
🧠 CrewAI + OpenAI – Agente de personalização

🐍 Flask – Backend web

📊 Baserow – Banco de dados low-code

📁 Pandas / openpyxl – ETL das planilhas HITS

🌐 Render.com – Hospedagem gratuita

📦 Instalação Local
1. Clonar o repositório
bash
Copiar
Editar
git clone https://github.com/DennisSanntos/ai-cafe-services.git
cd ai-cafe-services
2. Criar ambiente virtual e instalar dependências
bash
Copiar
Editar
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
3. Configurar variáveis de ambiente
bash
Copiar
Editar
cp .env.template .env
# Preencha .env com suas chaves e IDs
4. Rodar o servidor local
bash
Copiar
Editar
python main.py
☁️ Deploy no Render
1. Conectar com GitHub
Acesse Render.com

Clique em New Web Service

Escolha seu repositório ai-cafe-services

2. Configure o serviço
Build Command: pip install -r requirements.txt

Start Command: gunicorn main:app --config gunicorn.conf.py

Environment: Python 3.10

Environment Variables: copie de .env

💬 Funcionalidades
✅ Upload das planilhas do HITS
http
Copiar
Editar
POST /ingest
Form Data:
- arquivo_periodo (.xlsx)
- arquivo_apto (.xlsx)
✅ Acesso ao chat do hóspede
h
Copiar
Editar
GET /chat?reserva_id=1941
✅ Resposta IA (usado pelo chat.html)
http
Copiar
Editar
POST /chat/ia
{
  "reserva_id": "1941",
  "mensagem": "Não quero frutas, mas gosto de bolo de fubá"
}
✅ Painel administrativo
http
Copiar
Editar
GET /painel
📁 Estrutura do Projeto
bash
Copiar
Editar
ai_cafe_services/
├── app/                         # Lógica principal da aplicação
│   ├── __init__.py              # Inicialização do Flask
│   ├── routes.py                # Rotas (chat, ingestão, status)
│   ├── crew/                    # Agentes e tarefas CrewAI
│   │   ├── cafe_agent.py
│   │   ├── tasks.py
│   │   └── crew_config.py
│   ├── tools/                   # Baserow, ingestores etc.
│   │   ├── ingestor.py
│   │   └── baserow.py
│   └── utils.py                 # Auxiliares
├── templates/                   # HTML do chat e painel admin
│   ├── chat.html
│   └── painel.html
├── static/                      # CSS, JS e imagens (se necessário)
│   └── style.css
├── .env.template                # Variáveis de ambiente
├── requirements.txt             # Dependências
├── Procfile                     # Configuração do Render
├── gunicorn.conf.py             # Configuração gunicorn
├── main.py                      # Entry point do Flask
├── README.md                    # Documentação do projeto
└── runtime.txt                  # Versão do Python
🤝 Créditos
Denis Santos – Coordenação e integração hoteleira

OpenAI + CrewAI – Motor IA

Baserow – Banco de dados inteligente

📄 Licença
MIT License
