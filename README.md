# 🚀 Taze AI - Plataforma Inteligente de Análise de Investimentos

![Version](https://img.shields.io/badge/version-2.3.2-emerald)
![Python](https://img.shields.io/badge/python-3.13-blue)
![Next.js](https://img.shields.io/badge/next.js-15-black)
![License](https://img.shields.io/badge/license-MIT-green)

**Plataforma de análise de investimentos da B3 com inteligência artificial real**, utilizando OpenAI GPT-4o para gerar análises técnicas e fundamentalistas personalizadas.

---

## ✨ Principais Funcionalidades

### 🤖 **Análise de IA com 3 Perfis de Investidores**
- **🏛️ Warren (Buy & Hold)**: Análise fundamentalista para longo prazo
- **📈 Trader (Swing Trade)**: Análise técnica para médio prazo
- **⚡ Viper (Day Trade)**: Análise de volatilidade para curto prazo

### 📊 **Painel de Decisão Inteligente**
- Carrossel automático de análises (troca a cada 15s)
- Scores de 0-10 para cada perfil de investidor
- Recomendações claras: COMPRA FORTE | COMPRA | MANTER | VENDA

### 💬 **Chat Assistant com Function Calling**
- IA busca dados em tempo real quando necessário
- Respostas contextualizadas sobre ações da B3
- Detecção automática de ações mencionadas

### 📰 **Feed de Notícias Automático**
- Carrossel vertical de notícias (troca a cada 10s)
- Web scraping de fontes confiáveis
- Integração com botão de leitura completa

### 📈 **Dados em Tempo Real**
- Integração com Tradebox API (dados profissionais)
- Histórico de 90 dias para análise técnica
- Fundamentalistas completos (P/L, ROE, DY, etc)

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework Python assíncrono de alta performance
- **OpenAI GPT-4o** - IA generativa para análises profissionais
- **Tradebox API** - Dados profissionais da B3
- **httpx** - Cliente HTTP assíncrono
- **Pydantic** - Validação de dados

### Frontend
- **Next.js 15** - React framework com App Router
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização moderna
- **Embla Carousel** - Carrosséis suaves e responsivos
- **Lucide Icons** - Ícones modernos

### Integrações
- **OpenAI Function Calling** - IA que busca dados automaticamente
- **Web Scraping** - Notícias em tempo real
- **Cache Inteligente** - 24h para análises (economia de tokens)

---

## 🚀 Como Executar

### Pré-requisitos
- **Python 3.13+**
- **Node.js 18+**
- **API Keys**: OpenAI, Tradebox

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/tazeai.git
cd tazeai
```

### 2. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na pasta `backend/`:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Tradebox API
TRADEBOX_API_USER=TradeBox
TRADEBOX_API_PASS=TradeBoxAI@2025

# Brapi (Backup)
BRAPI_TOKEN=seu_token_aqui
```

### 3. Inicie o Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py
```

Backend rodará em: **http://localhost:8000**

### 4. Inicie o Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend rodará em: **http://localhost:3000**

---

## 📁 Estrutura do Projeto

```
tazeai/
├── backend/
│   ├── main.py                 # API FastAPI com endpoints
│   ├── requirements.txt        # Dependências Python
│   └── venv/                   # Ambiente virtual
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Homepage (Painel de Decisão)
│   │   ├── analises/
│   │   │   └── page.tsx        # Página de análises detalhadas
│   │   ├── layout.tsx          # Layout global
│   │   └── globals.css         # Estilos globais
│   │
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── AIScoreCard.tsx # Card de análise com 3 scores
│   │   │   ├── AIInsights.tsx  # Análise detalhada completa
│   │   │   ├── ChatWidget.tsx  # Chat com IA
│   │   │   ├── Sidebar.tsx     # Sidebar colapsável
│   │   │   └── StockChart.tsx  # Gráfico de preços
│   │   │
│   │   └── ui/
│   │       ├── carousel.tsx    # Componente de carrossel
│   │       └── button.tsx      # Componente de botão
│   │
│   ├── lib/
│   │   └── utils.ts            # Funções utilitárias
│   │
│   ├── package.json
│   └── tsconfig.json
│
├── docs/
│   └── sessoes-antigas/        # Documentação de desenvolvimento
│
├── README.md
└── LICENSE
```

---

## 🎯 Endpoints da API

### Dados de Ações
- `GET /api/stocks` - Lista todas as ações monitoradas
- `GET /api/stocks/{symbol}` - Detalhes de uma ação específica

### Análises de IA
- `POST /api/ai/analyze` - Gera análise com 3 perfis
- `GET /api/ai/analysis/{symbol}` - Busca análise em cache

### Chat Assistant
- `POST /api/ai/chat` - Conversa com IA (function calling)

### Notícias
- `GET /api/news` - Feed de notícias (scraping)

### Sistema
- `GET /` - Status da API
- `GET /health` - Health check

---

## 🎨 Funcionalidades Principais

### 1. Análise Tripla de IA
Cada ação recebe 3 análises diferentes:

| Perfil | Foco | Prazo | Analisa |
|--------|------|-------|---------|
| 🏛️ **Warren** | Fundamentalista | Anos | P/L, ROE, DY, Dívida |
| 📈 **Trader** | Técnico | Semanas/Meses | Tendências, Suporte/Resistência |
| ⚡ **Viper** | Volatilidade | 1-2 dias | Oscilações, Amplitude |

### 2. Painel de Decisão
- **Carrossel automático** de ações (15s)
- **Geração inline** de análises (sem redirect)
- **Indicadores visuais** (dots verdes)
- **Stats cards** com métricas em tempo real

### 3. Chat Inteligente
- **Function Calling**: IA busca dados automaticamente
- **Sem contexto visível**: Experiência fluida
- **Detecção automática**: Reconhece ações mencionadas
- **Paleta verde**: Design consistente

### 4. Feed de Notícias
- **Carrossel vertical** automático (10s)
- **Web scraping** de fontes confiáveis
- **Badge flutuante** "Ao vivo"
- **Botão direto** para notícia completa

---

## 🎨 Design System

### Paleta de Cores
```css
/* Verde Principal (Emerald) */
emerald-500: #10b981
emerald-600: #059669

/* Backgrounds */
zinc-950: #09090b (background principal)
zinc-900: #18181b (cards)
zinc-800: #27272a (elementos)

/* Scores */
Excelente (8-10): emerald-400
Bom (6-7): blue-400
Razoável (4-5): orange-400
Fraco (0-3): red-400
```

### Componentes Modernos
- **Glassmorphism**: `backdrop-blur-xl` com transparências
- **Gradientes**: Transições suaves verde
- **Shadows**: `shadow-emerald-500/20`
- **Animações**: `transition-all duration-300`

---

## 📊 Cache e Performance

### Otimizações Implementadas
- ✅ **Cache de Ações**: 5 minutos (evita sobrecarga de API)
- ✅ **Cache de Análises**: 24 horas (economia de tokens OpenAI)
- ✅ **Cache de Notícias**: 15 minutos
- ✅ **Histórico Limitado**: Apenas 90 dias (otimização de rede)
- ✅ **Requisições Paralelas**: AsyncIO para APIs

### Economia de Custos
- **Análises**: ~$0.02/análise (GPT-4o)
- **Cache 24h**: Reduz 95% dos custos
- **5 ações x 365 dias**: ~$36/ano (sem cache: ~$720/ano)

---

## 🔒 Segurança

- ✅ Variáveis de ambiente (.env)
- ✅ CORS configurado
- ✅ Validação de dados (Pydantic)
- ✅ Rate limiting (cache)
- ✅ Error handling completo

---

## 🚧 Roadmap

### Em Desenvolvimento
- [ ] Autenticação de usuários
- [ ] Carteira personalizada
- [ ] Alertas de preço
- [ ] Exportação de relatórios (PDF)

### Futuro
- [ ] Mais ações da B3 (top 20)
- [ ] Análise de FIIs
- [ ] Backtesting de estratégias
- [ ] App mobile (React Native)

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Gustavo F.**  
Desenvolvedor Full Stack | Entusiasta de IA

---

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:
1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📧 Suporte

Para dúvidas ou sugestões, abra uma issue no GitHub.

---

**Desenvolvido com ❤️ usando IA Real**
