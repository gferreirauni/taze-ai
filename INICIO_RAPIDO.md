# ⚡ Guia de Início Rápido - Taze AI

**Tempo estimado:** 5 minutos

---

## 🎯 Pré-requisitos

- ✅ Python 3.13+
- ✅ Node.js 18+
- ✅ Chave da OpenAI API
- ✅ Credenciais Tradebox API

---

## 🚀 Configuração em 4 Passos

### **1. Clone o Repositório**
```bash
git clone https://github.com/seu-usuario/tazeai.git
cd tazeai
```

### **2. Configure o Backend**

```bash
cd backend

# Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env
echo "OPENAI_API_KEY=sk-proj-..." > .env
echo "TRADEBOX_API_USER=TradeBox" >> .env
echo "TRADEBOX_API_PASS=TradeBoxAI@2025" >> .env
echo "REDIS_URL=redis://localhost:6379/0" >> .env  # Opcional: cache compartilhado
```

> Observacao: se voce nao tiver Redis rodando localmente, o backend usa automaticamente o cache em memoria.

### **3. Configure o Frontend**

```bash
cd ../frontend

# Instalar dependências
npm install
```

### **4. Inicie os Servidores**

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```
✅ Rodando em: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
✅ Rodando em: http://localhost:3000

---

## 🎉 Pronto! Acesse o Dashboard

Abra seu navegador em: **http://localhost:3000**

---

## 🧪 Teste Rápido

### **1. Gerar Análise de IA**
1. Na homepage, localize um card sem análise
2. Clique em **"Gerar Análise"**
3. Aguarde 10-15 segundos
4. Veja os 3 scores aparecerem (Warren, Trader, Viper)

### **2. Testar Chat Inteligente**
1. Clique no botão flutuante verde (chat)
2. Pergunte: "O que acha de PETR4?"
3. A IA busca dados automaticamente
4. Resposta personalizada com preço atual

### **3. Navegar pelos Carrosséis**
- **Ações**: Troca automaticamente a cada 15s
- **Notícias**: Desce automaticamente a cada 10s
- Use os botões laterais (← →) ou dots para navegar

### **4. Sidebar Colapsável**
- Clique na setinha (← / →) ao lado da logo
- Sidebar reduz para apenas ícones
- Passe o mouse para ver tooltips

---

## 🐛 Problemas Comuns

### ❌ Backend não inicia
**Erro:** `ModuleNotFoundError: No module named 'fastapi'`  
**Solução:** Certifique-se de ativar o venv: `venv\Scripts\activate`

### ❌ Frontend com erro
**Erro:** `Module not found: Can't resolve '@/components/...'`  
**Solução:** Execute `npm install` novamente

### ❌ Chat retorna erro
**Erro:** "HTTP 422"  
**Solução:** Verifique se OPENAI_API_KEY está configurada no .env

### ❌ Sem análises geradas
**Causa:** Cache vazio  
**Solução:** Gere manualmente clicando em "Gerar Análise"

---

## 📚 Próximos Passos

1. ✅ Leia o [README.md](README.md) completo
2. ✅ Veja o [Raio-X Técnico](RAIO_X_TECNICO_ATUAL.md)
3. ✅ Explore a [documentação de sessões](docs/sessoes-antigas/)
4. ✅ Acesse a [API Docs](http://localhost:8000/docs)

---

## 📞 Suporte

Dúvidas? Abra uma issue no GitHub ou consulte a documentação.

---

**Bom desenvolvimento! 🚀**

