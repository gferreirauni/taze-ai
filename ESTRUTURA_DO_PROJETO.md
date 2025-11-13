# 📂 Estrutura do Projeto Taze AI

## 🎯 Visão Geral

```
tazeai/
│
├── 📱 frontend/                      # Aplicação Next.js 14
│   ├── app/                         # App Router
│   │   ├── layout.tsx              # Layout principal
│   │   ├── page.tsx                # Página inicial
│   │   └── globals.css             # Estilos globais
│   ├── node_modules/               # Dependências Node
│   ├── public/                     # Arquivos estáticos
│   ├── package.json                # Config do projeto
│   ├── tsconfig.json               # Config TypeScript
│   ├── next.config.ts              # Config Next.js
│   ├── tailwind.config.ts          # Config Tailwind CSS
│   └── postcss.config.mjs          # Config PostCSS
│
├── 🐍 backend/                      # API FastAPI
│   ├── venv/                       # Ambiente virtual Python
│   ├── main.py                     # Aplicação FastAPI principal
│   └── requirements.txt            # Dependências Python
│
├── 📄 Arquivos de Configuração
│   ├── .gitignore                  # Arquivos ignorados pelo Git
│   ├── package.json                # Scripts do monorepo
│   ├── README.md                   # Documentação principal
│   ├── NEXT_STEPS.md               # Próximos passos detalhados
│   └── ESTRUTURA_DO_PROJETO.md     # Este arquivo
│
└── 🚀 Scripts de Inicialização (PowerShell)
    ├── setup.ps1                   # Setup completo do projeto
    ├── start-backend.ps1           # Iniciar backend
    └── start-frontend.ps1          # Iniciar frontend
```

## ✅ O Que Foi Criado

### 1. Frontend (Next.js 14)
- ✅ Next.js 14 com App Router
- ✅ TypeScript configurado
- ✅ Tailwind CSS instalado
- ✅ ESLint configurado
- ✅ Estrutura de pastas otimizada

### 2. Backend (FastAPI)
- ✅ Ambiente virtual Python criado
- ✅ main.py com endpoints de exemplo:
  - `GET /` - Boas-vindas
  - `GET /health` - Health check
  - `GET /api/stocks` - Lista de ações (dados de exemplo)
- ✅ CORS configurado para o frontend
- ✅ requirements.txt com:
  - FastAPI
  - Uvicorn
  - Pandas
  - OpenAI
  - Python-dotenv

### 3. Documentação
- ✅ README.md completo com instruções
- ✅ NEXT_STEPS.md com guia de desenvolvimento
- ✅ .gitignore configurado
- ✅ Scripts PowerShell para facilitar inicialização

## 🎯 Dependências Principais

### Frontend
```json
{
  "next": "^16.0.3",
  "react": "^19.x",
  "react-dom": "^19.x",
  "typescript": "^5.x",
  "tailwindcss": "^3.x"
}
```

### Backend
```txt
fastapi==0.115.0
uvicorn==0.32.0
pandas==2.2.3
openai==1.54.3
python-dotenv==1.0.1
```

## 🚀 Como Iniciar

### Opção 1: Setup Automático (Recomendado)

```powershell
# Execute o script de setup uma vez
.\setup.ps1
```

### Opção 2: Manual

**Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

**Frontend (em outro terminal):**
```powershell
cd frontend
npm run dev
```

### Opção 3: Scripts Rápidos

**Terminal 1 - Backend:**
```powershell
.\start-backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
.\start-frontend.ps1
```

## 🌐 URLs de Acesso

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Docs API (Swagger):** http://localhost:8000/docs
- **Docs API (ReDoc):** http://localhost:8000/redoc

## 📦 Próximas Adições Sugeridas

1. **Shadcn UI** - Componentes bonitos
2. **Lucide React** - Ícones
3. **Recharts** - Gráficos para o dashboard
4. **YFinance** - Dados reais da B3
5. **NextAuth** - Autenticação (futuro)
6. **Prisma** - ORM para banco de dados (futuro)

## 🎨 Funcionalidades a Desenvolver

- [ ] Dashboard principal
- [ ] Listagem de ações da B3
- [ ] Gráficos de preços
- [ ] Análise de ações com IA (GPT-4)
- [ ] Carteira de investimentos
- [ ] Alertas de preço
- [ ] Sistema de autenticação

---

**Status:** ✅ Projeto inicializado e pronto para desenvolvimento!

