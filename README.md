# 🚀 Taze AI - Dashboard Inteligente para Investidores da B3

<div align="center">

![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=for-the-badge&logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3-38B2AC?style=for-the-badge&logo=tailwind-css)

**Dashboard inteligente alimentado por IA para análise de investimentos na Bolsa Brasileira (B3)**

[Documentação](#-estrutura-do-projeto) • [Começar](#-como-rodar-o-projeto) • [Próximos Passos](NEXT_STEPS.md)

</div>

---

## ✨ Features Principais

- 📊 **Dashboard Interativo** - Visualize dados do mercado em tempo real
- 🤖 **Análise com IA** - Recomendações inteligentes usando GPT-4
- 📈 **Gráficos Avançados** - Histórico de preços e análises técnicas
- 💼 **Gestão de Carteira** - Acompanhe seus investimentos
- 🔔 **Alertas Personalizados** - Notificações de preços e oportunidades
- 🎯 **Dados da B3** - Informações atualizadas do mercado brasileiro

## 📋 Stack Tecnológica

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Shadcn UI** (componentes)
- **Lucide React** (ícones)

### Backend
- **Python 3.10+**
- **FastAPI**
- **Pandas** (análise de dados)
- **OpenAI API** (inteligência artificial)

## 🏗️ Estrutura do Projeto

```
tazeai/
├── frontend/          # Aplicação Next.js
│   ├── app/          # App Router do Next.js
│   ├── components/   # Componentes React
│   ├── public/       # Arquivos estáticos
│   └── ...
├── backend/          # API FastAPI
│   ├── venv/        # Ambiente virtual Python
│   ├── main.py      # Aplicação FastAPI
│   └── requirements.txt
└── README.md
```

## 🚀 Como Rodar o Projeto

### Pré-requisitos

- **Node.js** 18+ e npm/yarn
- **Python** 3.10+
- **Git**

### 1️⃣ Backend (FastAPI)

```bash
# Navegue até a pasta do backend
cd backend

# Ative o ambiente virtual
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
.\venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# (Opcional) Configure suas variáveis de ambiente
# Copie o .env.example para .env e adicione suas chaves de API
# cp .env.example .env

# Execute o servidor
python main.py

# Ou use uvicorn diretamente:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará rodando em: **http://localhost:8000**

📚 Documentação da API: **http://localhost:8000/docs**

### 2️⃣ Frontend (Next.js)

```bash
# Em outro terminal, navegue até a pasta do frontend
cd frontend

# Instale as dependências (se necessário)
npm install

# Execute o servidor de desenvolvimento
npm run dev
```

O frontend estará rodando em: **http://localhost:3000**

## 🔗 Endpoints da API

### Base URL: `http://localhost:8000`

- `GET /` - Mensagem de boas-vindas
- `GET /health` - Health check da API
- `GET /api/stocks` - Lista de ações de exemplo

Acesse **http://localhost:8000/docs** para ver a documentação interativa completa (Swagger UI).

## 🛠️ Desenvolvimento

### Comandos Úteis

**Frontend:**
```bash
npm run dev      # Servidor de desenvolvimento
npm run build    # Build de produção
npm run start    # Executar build de produção
npm run lint     # Linter
```

**Backend:**
```bash
python main.py                    # Executar servidor
uvicorn main:app --reload         # Executar com hot reload
pip install -r requirements.txt   # Instalar dependências
pip freeze > requirements.txt     # Atualizar dependências
```

## 🎨 Próximos Passos

1. **Instalar Shadcn UI** no frontend
   ```bash
   cd frontend
   npx shadcn-ui@latest init
   ```

2. **Configurar OpenAI API** no backend
   - Adicione sua chave da OpenAI no arquivo `.env`
   - Configure os prompts para análise de ações

3. **Integrar dados da B3**
   - Implementar scraping ou API de dados financeiros
   - Conectar com Yahoo Finance ou outras fontes

4. **Desenvolver funcionalidades:**
   - Dashboard com gráficos e métricas
   - Análise de ações com IA
   - Recomendações personalizadas
   - Alertas de preço

## 📝 Licença

Este projeto está sob a licença MIT.

## 👥 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

**Desenvolvido com ❤️ para investidores inteligentes**

