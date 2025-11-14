from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from dotenv import load_dotenv
import random
import uvicorn
import os
from openai import OpenAI
import requests
import xml.etree.ElementTree as ET

# Carregar variáveis de ambiente
load_dotenv()

# Instanciar cliente OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configurar Brapi (API Brasileira para B3)
BRAPI_TOKEN = os.getenv("BRAPI_TOKEN", "")
BRAPI_BASE_URL = "https://brapi.dev/api"

app = FastAPI(
    title="Taze AI API",
    description="API inteligente para análise de investimentos da B3",
    version="2.0.0"  # Atualizado para v2.0 com dados reais
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL do Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CACHE GLOBAL ====================
# Cache em memória para evitar requisições excessivas ao yfinance
stocks_cache = {
    "data": None,
    "timestamp": None,
    "ttl": 300  # 5 minutos em segundos
}

# Cache de análises de IA (por dia para economizar tokens)
# Estrutura: { "PETR4_2025-11-14": { "analysis": {...}, "timestamp": datetime } }
ai_analysis_cache = {}

# Cache de notícias (15 minutos)
news_cache = {
    "data": None,
    "timestamp": None,
    "ttl": 900  # 15 minutos
}

def is_cache_valid():
    """Verifica se o cache ainda é válido"""
    if stocks_cache["data"] is None or stocks_cache["timestamp"] is None:
        return False
    
    elapsed = (datetime.now() - stocks_cache["timestamp"]).total_seconds()
    return elapsed < stocks_cache["ttl"]

def update_cache(data):
    """Atualiza o cache com novos dados"""
    stocks_cache["data"] = data
    stocks_cache["timestamp"] = datetime.now()

# ==================== DADOS REAIS COM YFINANCE ====================

# Lista de ações da B3 que vamos monitorar
B3_STOCKS = ["PETR4", "VALE3", "ITUB4", "WEGE3", "BBAS3"]

def generate_mock_stock_data():
    """
    Gera dados mockados realistas para fallback
    Usado quando yfinance falha ou está muito lento
    """
    print("[FALLBACK] Usando dados mockados realistas")
    
    mock_stocks = [
        {"symbol": "PETR4", "name": "Petrobras PN", "base_price": 38.50, "sector": "Energia"},
        {"symbol": "VALE3", "name": "Vale ON", "base_price": 61.20, "sector": "Mineracao"},
        {"symbol": "ITUB4", "name": "Itau Unibanco PN", "base_price": 26.80, "sector": "Financeiro"},
        {"symbol": "WEGE3", "name": "WEG ON", "base_price": 42.15, "sector": "Industria"},
        {"symbol": "BBAS3", "name": "Banco do Brasil ON", "base_price": 28.90, "sector": "Financeiro"}
    ]
    
    stocks_data = []
    
    for stock in mock_stocks:
        # Gerar histórico de 30 dias
        history = []
        current_date = datetime.now() - timedelta(days=30)
        current_price = stock["base_price"] * random.uniform(0.9, 0.95)
        
        for day in range(30):
            daily_change = random.uniform(-0.02, 0.02)
            current_price = current_price * (1 + daily_change)
            history.append({
                "date": (current_date + timedelta(days=day)).strftime("%Y-%m-%d"),
                "value": round(current_price, 2)
            })
        
        # Variação diária
        last_price = history[-1]["value"]
        prev_price = history[-2]["value"]
        daily_variation = ((last_price - prev_price) / prev_price) * 100
        
        stocks_data.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "sector": stock["sector"],
            "currentPrice": round(last_price, 2),
            "dailyVariation": round(daily_variation, 2),
            "history": history
        })
        
        print(f"[MOCK] Dados gerados: {stock['symbol']} - R$ {last_price:.2f}")
    
    return stocks_data

def fetch_real_stock_data():
    """
    Busca dados reais das ações usando Brapi.dev (API Brasileira B3)
    Se falhar, usa fallback mockado
    """
    stocks_data = []
    
    print("[BRAPI] Buscando dados reais da B3 via Brapi.dev...")
    
    for symbol in B3_STOCKS:
        try:
            # Construir URL da Brapi
            # Endpoint: /quote/{ticker}?range=3mo&interval=1d&token=YOUR_TOKEN
            url = f"{BRAPI_BASE_URL}/quote/{symbol}"
            params = {
                "range": "3mo",  # 3 meses (máximo no plano gratuito)
                "interval": "1d",  # Diário
                "token": BRAPI_TOKEN
            }
            
            # Fazer requisição
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code != 200:
                print(f"[AVISO] Brapi retornou {response.status_code} para {symbol}")
                continue
            
            data = response.json()
            
            # Verificar se há resultados
            if not data.get("results") or len(data["results"]) == 0:
                print(f"[AVISO] Sem dados para {symbol}")
                continue
            
            stock_data = data["results"][0]
            
            # Extrair informações
            current_price = stock_data.get("regularMarketPrice", 0)
            previous_close = stock_data.get("regularMarketPreviousClose", current_price)
            
            # Calcular variação diária
            if previous_close > 0:
                daily_variation = ((current_price - previous_close) / previous_close) * 100
            else:
                daily_variation = 0
            
            # Histórico
            history = []
            historical_data = stock_data.get("historicalDataPrice", [])
            
            if historical_data:
                # Pegar últimos 30 dias
                for item in historical_data[-30:]:
                    history.append({
                        "date": datetime.fromtimestamp(item["date"]).strftime("%Y-%m-%d"),
                        "value": round(float(item["close"]), 2)
                    })
            
            # Nome e setor
            long_name = stock_data.get("longName", stock_data.get("shortName", symbol))
            sector = stock_data.get("sector", "N/A")
            
            # Fallback para setores conhecidos se N/A
            if sector == "N/A":
                sector_map = {
                    "PETR4": "Energia",
                    "VALE3": "Mineração",
                    "ITUB4": "Financeiro",
                    "WEGE3": "Indústria",
                    "BBAS3": "Financeiro"
                }
                sector = sector_map.get(symbol, "N/A")
            
            stocks_data.append({
                "symbol": symbol,
                "name": long_name,
                "sector": sector,
                "currentPrice": round(float(current_price), 2),
                "dailyVariation": round(float(daily_variation), 2),
                "history": history
            })
            
            print(f"[OK] Dados carregados: {symbol} - R$ {current_price:.2f}")
            
        except requests.Timeout:
            print(f"[TIMEOUT] Brapi demorou muito para {symbol}")
            continue
        except Exception as e:
            print(f"[ERRO] Erro ao buscar {symbol}: {str(e)}")
            continue
    
    # Se conseguiu pelo menos 1 ação real, retornar
    if len(stocks_data) > 0:
        print(f"[SUCESSO] {len(stocks_data)} acoes carregadas da Brapi")
        return stocks_data
    
    # Se não conseguiu nenhuma, usar fallback
    print("[FALLBACK] Nenhuma acao encontrada na Brapi, usando dados mockados")
    return generate_mock_stock_data()

@app.get("/")
async def root():
    """Endpoint de boas-vindas"""
    return {
        "message": "Bem-vindo à Taze AI API! 🚀",
        "status": "online",
        "version": "2.0.0",
        "data_source": "Brapi.dev (API Brasileira B3)"
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    cache_status = "valid" if is_cache_valid() else "expired"
    return {
        "status": "healthy",
        "service": "Taze AI Backend",
        "cache_status": cache_status,
        "data_source": "brapi",
        "brapi_configured": bool(BRAPI_TOKEN)
    }

@app.get("/api/news")
async def get_news():
    """
    Busca notícias do feed RSS do Investing.com
    Cache de 15 minutos para não sobrecarregar o servidor
    """
    # Verificar cache
    if news_cache["data"] is not None and news_cache["timestamp"] is not None:
        elapsed = (datetime.now() - news_cache["timestamp"]).total_seconds()
        if elapsed < news_cache["ttl"]:
            print("[NEWS CACHE] Retornando notícias do cache")
            return {
                "news": news_cache["data"],
                "cached": True,
                "cache_age_seconds": elapsed
            }
    
    # Buscar notícias do RSS
    print("[NEWS] Buscando notícias do Investing.com RSS...")
    
    try:
        rss_url = "https://br.investing.com/rss/stock_Fundamental.rss"
        response = requests.get(rss_url, timeout=10)
        
        if response.status_code != 200:
            print(f"[NEWS ERROR] RSS retornou {response.status_code}")
            return {"news": [], "error": "Erro ao buscar RSS"}
        
        # Parsear XML
        root = ET.fromstring(response.content)
        
        news_items = []
        
        # Extrair itens do RSS
        for item in root.findall(".//item")[:10]:  # Pegar até 10 notícias
            title = item.find("title")
            link = item.find("link")
            pub_date = item.find("pubDate")
            author = item.find("author")
            
            # Calcular tempo relativo
            if pub_date is not None and pub_date.text:
                try:
                    # Formato: "Aug 08, 2025 14:08 GMT"
                    pub_datetime = datetime.strptime(pub_date.text, "%b %d, %Y %H:%M GMT")
                    now = datetime.utcnow()
                    diff = now - pub_datetime
                    
                    if diff.days > 0:
                        time_ago = f"{diff.days} dia{'s' if diff.days > 1 else ''} atrás"
                    elif diff.seconds >= 3600:
                        hours = diff.seconds // 3600
                        time_ago = f"{hours} hora{'s' if hours > 1 else ''} atrás"
                    else:
                        minutes = diff.seconds // 60
                        time_ago = f"{minutes} minuto{'s' if minutes > 1 else ''} atrás"
                except:
                    time_ago = "Recente"
            else:
                time_ago = "Recente"
            
            news_items.append({
                "title": title.text if title is not None else "Sem título",
                "link": link.text if link is not None else "#",
                "author": author.text if author is not None else "Investing.com",
                "time_ago": time_ago,
                "source": "Investing.com"
            })
        
        # Atualizar cache
        news_cache["data"] = news_items
        news_cache["timestamp"] = datetime.now()
        
        print(f"[NEWS] {len(news_items)} notícias carregadas do Investing.com")
        
        return {
            "news": news_items,
            "cached": False,
            "count": len(news_items),
            "source": "Investing.com RSS"
        }
        
    except Exception as e:
        print(f"[NEWS ERROR] {str(e)}")
        return {
            "news": [],
            "error": str(e),
            "fallback": True
        }

@app.get("/api/stocks")
async def get_stocks():
    """
    Retorna lista de ações com dados REAIS da B3 via yfinance
    Implementa cache de 5 minutos para otimizar performance
    """
    # Verificar se o cache é válido
    if is_cache_valid():
        print("[CACHE] Retornando dados do cache")
        return {
            "stocks": stocks_cache["data"],
            "timestamp": datetime.now().isoformat(),
            "count": len(stocks_cache["data"]),
            "source": "cache",
            "cache_age_seconds": (datetime.now() - stocks_cache["timestamp"]).total_seconds()
        }
    
    # Cache expirado, buscar novos dados
    print("[ATUALIZANDO] Cache expirado, buscando dados do yfinance...")
    stocks_data = fetch_real_stock_data()
    
    # Atualizar cache
    update_cache(stocks_data)
    
    return {
        "stocks": stocks_data,
        "timestamp": datetime.now().isoformat(),
        "count": len(stocks_data),
        "source": "brapi" if BRAPI_TOKEN else "fallback",
        "cache_ttl_seconds": stocks_cache["ttl"]
    }

@app.get("/api/stocks/{symbol}")
async def get_stock_detail(symbol: str):
    """
    Retorna detalhes de uma ação específica com dados reais da Brapi
    """
    symbol_upper = symbol.upper()
    
    if symbol_upper not in B3_STOCKS:
        return {"error": "Ação não encontrada"}, 404
    
    try:
        # Buscar dados da Brapi
        url = f"{BRAPI_BASE_URL}/quote/{symbol_upper}"
        params = {
            "range": "3mo",
            "interval": "1d",
            "token": BRAPI_TOKEN
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            return {"error": "Erro ao buscar dados da Brapi"}, 500
        
        data = response.json()
        
        if not data.get("results") or len(data["results"]) == 0:
            return {"error": "Sem dados para esta ação"}, 404
        
        stock_data = data["results"][0]
        
        # Extrair informações
        current_price = stock_data.get("regularMarketPrice", 0)
        previous_close = stock_data.get("regularMarketPreviousClose", current_price)
        
        # Calcular variação diária
        daily_variation = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
        
        # Histórico
        history = []
        historical_data = stock_data.get("historicalDataPrice", [])
        
        if historical_data:
            for item in historical_data:
                history.append({
                    "date": datetime.fromtimestamp(item["date"]).strftime("%Y-%m-%d"),
                    "value": round(float(item["close"]), 2)
                })
            
            # Calcular variação semanal (últimos 7 dias)
            if len(historical_data) >= 7:
                week_ago_price = historical_data[-7]["close"]
                week_variation = ((current_price - week_ago_price) / week_ago_price) * 100
            else:
                week_variation = 0
            
            # Calcular variação mensal (últimos 30 dias)
            if len(historical_data) >= 30:
                month_ago_price = historical_data[-30]["close"]
                month_variation = ((current_price - month_ago_price) / month_ago_price) * 100
            else:
                month_variation = 0
        else:
            week_variation = 0
            month_variation = 0
        
        return {
            "symbol": symbol_upper,
            "name": stock_data.get("longName", stock_data.get("shortName", symbol_upper)),
            "sector": stock_data.get("sector", "N/A"),
            "currentPrice": round(float(current_price), 2),
            "dailyVariation": round(float(daily_variation), 2),
            "weekVariation": round(float(week_variation), 2),
            "monthVariation": round(float(month_variation), 2),
            "history": history,
            "volume": int(stock_data.get("regularMarketVolume", 0)),
            "marketCap": stock_data.get("marketCap", 0)
        }
        
    except Exception as e:
        return {"error": f"Erro ao buscar dados: {str(e)}"}, 500

@app.get("/api/portfolio/summary")
async def get_portfolio_summary():
    """
    Retorna resumo da carteira
    Por enquanto, calcula baseado nas ações monitoradas (dados reais)
    """
    try:
        # Buscar dados atuais
        if not is_cache_valid():
            stocks_data = fetch_real_stock_data()
            update_cache(stocks_data)
        else:
            stocks_data = stocks_cache["data"]
        
        # Calcular valores (assumindo 100 ações de cada)
        shares_per_stock = 100
        total_value = sum(stock["currentPrice"] * shares_per_stock for stock in stocks_data)
        
        # Calcular variação média ponderada
        total_investment = total_value  # Simplificado
        weighted_variation = sum(stock["dailyVariation"] * (stock["currentPrice"] * shares_per_stock) 
                                for stock in stocks_data) / total_value
        
        daily_change_value = total_value * (weighted_variation / 100)
        
        return {
            "totalValue": round(total_value, 2),
            "dailyChange": round(weighted_variation, 2),
            "dailyChangeValue": round(daily_change_value, 2),
            "stocksCount": len(stocks_data),
            "totalInvested": round(total_value, 2),
            "totalProfit": 0.0,  # Simplificado por enquanto
            "profitPercentage": 0.0,
            "source": "real_data"
        }
    except Exception as e:
        # Fallback para dados mockados se houver erro
        return {
            "totalValue": 125478.90,
            "dailyChange": 2.34,
            "dailyChangeValue": 2876.45,
            "stocksCount": 5,
            "totalInvested": 110000.00,
            "totalProfit": 15478.90,
            "profitPercentage": 14.07,
            "source": "fallback"
        }

# ==================== AI ANALYSIS ENDPOINTS ====================

class AIAnalysisRequest(BaseModel):
    symbol: str
    currentPrice: float
    dailyVariation: float
    history: list

def mock_ai_analysis(symbol: str, current_price: float, daily_variation: float, history: list):
    """
    Simula uma análise de IA realista baseada nos dados da ação
    Em produção, isso seria substituído por uma chamada real à OpenAI GPT-4
    """
    
    # Calcular métricas adicionais
    prices = [h["value"] for h in history]
    avg_price = sum(prices) / len(prices)
    max_price = max(prices)
    min_price = min(prices)
    volatility = ((max_price - min_price) / avg_price) * 100
    
    # Calcular tendência (últimos 7 dias)
    recent_prices = prices[-7:] if len(prices) >= 7 else prices
    trend_up = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] > recent_prices[i-1])
    trend_down = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] < recent_prices[i-1])
    
    # Determinar recomendação e análise
    if daily_variation > 2:
        recommendation = "COMPRA FORTE"
        sentiment = "bullish"
        analysis = f"""📈 **Análise Técnica Positiva**

A ação {symbol} apresenta forte momentum de alta com variação de {daily_variation:+.2f}% no dia. 

**Indicadores Técnicos:**
- Preço atual: R$ {current_price:.2f} (acima da média móvel de R$ {avg_price:.2f})
- Resistência identificada em R$ {max_price:.2f}
- Suporte forte em R$ {min_price:.2f}
- Volatilidade: {volatility:.1f}% (moderada)

**Volume e Momentum:**
A análise de volume indica forte interesse comprador. Tendência de alta confirmada com {trend_up} sessões positivas nos últimos 7 dias.

**Fundamentos:**
Empresa sólida do setor, com bons indicadores fundamentalistas. Expectativa de valorização no curto prazo.

**Recomendação:** {recommendation} - Momento favorável para posições compradas."""

    elif daily_variation > 0.5:
        recommendation = "COMPRA"
        sentiment = "bullish"
        analysis = f"""✅ **Tendência de Alta Confirmada**

{symbol} mantém trajetória positiva com variação de {daily_variation:+.2f}% hoje.

**Análise Técnica:**
- Preço: R$ {current_price:.2f} (tendência de alta)
- Média móvel 30 dias: R$ {avg_price:.2f}
- Range: R$ {min_price:.2f} - R$ {max_price:.2f}
- Volatilidade controlada: {volatility:.1f}%

**Projeção:**
Sinais positivos indicam continuação do movimento de alta. {trend_up} de {len(recent_prices)} últimas sessões foram positivas.

**Recomendação:** {recommendation} - Bom ponto de entrada para posições compradas."""

    elif daily_variation > -0.5:
        recommendation = "MANTER"
        sentiment = "neutral"
        analysis = f"""⚖️ **Movimento Lateral - Consolidação**

{symbol} opera estável com leve variação de {daily_variation:+.2f}% no período.

**Cenário Atual:**
- Cotação: R$ {current_price:.2f}
- Faixa de negociação: R$ {min_price:.2f} - R$ {max_price:.2f}
- Volatilidade: {volatility:.1f}%

**Análise:**
Ação em fase de consolidação. Mercado aguarda catalisadores para definir próxima direção. Equilíbrio entre compradores e vendedores.

**Padrão Técnico:**
Movimento lateral pode preceder rompimento. Monitorar volumes para identificar direção.

**Recomendação:** {recommendation} - Aguardar definição de tendência antes de novas posições."""

    elif daily_variation > -2:
        recommendation = "ATENÇÃO"
        sentiment = "bearish"
        analysis = f"""⚠️ **Correção Técnica em Andamento**

{symbol} apresenta correção de {daily_variation:.2f}% hoje. Movimento dentro do esperado.

**Análise de Risco:**
- Preço atual: R$ {current_price:.2f}
- Suporte importante em R$ {min_price:.2f}
- Resistência em R$ {max_price:.2f}
- Volatilidade aumentada: {volatility:.1f}%

**Contexto:**
Correção saudável após movimento de alta. {trend_down} sessões negativas recentes indicam realização de lucros.

**Níveis Críticos:**
Importante observar o suporte em R$ {min_price:.2f}. Rompimento pode acelerar queda.

**Recomendação:** {recommendation} - Cautela. Aguardar estabilização antes de novas compras. Stop loss recomendado."""

    else:
        recommendation = "VENDA"
        sentiment = "bearish"
        analysis = f"""🔴 **Alerta de Risco - Pressão Vendedora**

{symbol} em forte queda de {daily_variation:.2f}% no dia. Sinal de alerta acionado.

**Indicadores de Risco:**
- Preço: R$ {current_price:.2f} (tendência de baixa forte)
- Rompeu suporte de R$ {min_price + (max_price - min_price) * 0.2:.2f}
- Volatilidade elevada: {volatility:.1f}%
- Pressão vendedora intensa

**Análise Técnica:**
{trend_down} das últimas {len(recent_prices)} sessões foram negativas. Momento desfavorável.

**Gestão de Risco:**
Recomenda-se proteção de posições. Mercado pode testar novos patamares de suporte.

**Próximos Suportes:**
R$ {min_price:.2f} (crítico) | R$ {min_price * 0.95:.2f} (extensão)

**Recomendação:** {recommendation} - Reduzir exposição. Aguardar reversão de tendência."""

    # Adicionar insights específicos por ação
    sector_insights = {
        "PETR4": "Setor de petróleo sensível a preços internacionais do barril.",
        "VALE3": "Mineradora impactada por demanda chinesa e preço do minério de ferro.",
        "ITUB4": "Setor financeiro beneficiado por ambiente de juros elevados.",
        "WEGE3": "Indústria de motores elétricos com forte demanda internacional.",
        "BBAS3": "Banco estatal com solidez e dividendos atrativos."
    }
    
    sector_note = sector_insights.get(symbol, "Ação com boa liquidez no mercado brasileiro.")
    
    return {
        "symbol": symbol,
        "recommendation": recommendation,
        "sentiment": sentiment,
        "confidence": round(random.uniform(75, 95), 1),
        "analysis": analysis,
        "sectorInsight": sector_note,
        "generatedAt": datetime.now().isoformat(),
        "disclaimer": "Análise automatizada para fins educacionais. Não é recomendação de investimento."
    }

@app.get("/api/ai/analysis/{symbol}")
async def get_cached_analysis(symbol: str):
    """
    Retorna análise em cache do dia (se existir)
    Economiza tokens ao não gerar análise toda vez
    """
    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"{symbol}_{today}"
    
    if cache_key in ai_analysis_cache:
        cached = ai_analysis_cache[cache_key]
        return {
            "cached": True,
            "analysis": cached["analysis"],
            "generated_at": cached["timestamp"].isoformat()
        }
    
    return {
        "cached": False,
        "message": "Nenhuma análise do dia encontrada. Clique em 'Gerar Análise'."
    }

@app.post("/api/ai/analyze")
async def analyze_stock(request: AIAnalysisRequest):
    """
    Gera nova análise de IA e salva em cache por dia
    Só deve ser chamado quando usuário clica em "Gerar/Atualizar Análise"
    """
    # Gerar análise
    analysis = mock_ai_analysis(
        request.symbol,
        request.currentPrice,
        request.dailyVariation,
        request.history
    )
    
    # Salvar em cache (por dia)
    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"{request.symbol}_{today}"
    ai_analysis_cache[cache_key] = {
        "analysis": analysis,
        "timestamp": datetime.now()
    }
    
    print(f"[AI CACHE] Análise gerada e armazenada: {cache_key}")
    
    return analysis

# ==================== CHAT ASSISTANT ENDPOINTS ====================

class ChatMessage(BaseModel):
    message: str
    context: dict = None

@app.post("/api/ai/chat")
async def chat_with_assistant(request: ChatMessage):
    """
    Chat em tempo real com o Taze AI Assistant (OpenAI GPT-4)
    """
    try:
        # System prompt poderoso para o assistente financeiro
        system_prompt = """Você é o Taze AI, um analista financeiro sênior especialista em ações da B3 (Bolsa de Valores brasileira).

**Sua Personalidade:**
- Profissional, mas acessível e amigável
- Conciso e direto ao ponto
- Usa dados técnicos e fundamentalistas para justificar opiniões
- Responde em Português do Brasil
- Usa emojis ocasionalmente para deixar a conversa mais leve

**Suas Habilidades:**
- Análise técnica (suporte, resistência, médias móveis, volume)
- Análise fundamentalista (P/L, dividend yield, ROE)
- Interpretação de notícias do mercado
- Gestão de risco e estratégias de investimento
- Conhecimento profundo sobre empresas da B3

**Formato de Resposta:**
- Use Markdown para formatação (negrito, listas, etc.)
- Seja objetivo: máximo 200 palavras por resposta
- Sempre termine com uma recomendação clara ou próximo passo

**Importante:**
- Você NÃO é uma recomendação formal de investimento
- Sempre lembre o usuário de fazer sua própria análise
- Use disclaimer quando apropriado: "Esta é uma análise educacional, não recomendação de compra/venda"
"""

        # Construir mensagem do usuário com contexto (se fornecido)
        user_message = request.message
        
        if request.context:
            # Adicionar contexto da ação que o usuário está visualizando
            context_info = f"""
**Contexto da Tela do Usuário:**
- Ação: {request.context.get('symbol', 'N/A')} - {request.context.get('name', 'N/A')}
- Preço Atual: R$ {request.context.get('currentPrice', 0):.2f}
- Variação Diária: {request.context.get('dailyVariation', 0):+.2f}%
- Setor: {request.context.get('sector', 'N/A')}

O usuário está visualizando esta ação no momento. Use essas informações para contextualizar sua resposta.

**Pergunta do Usuário:**
{user_message}
"""
            user_message = context_info
        
        # Chamar OpenAI GPT-4
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # ou gpt-3.5-turbo para economizar
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        
        assistant_reply = response.choices[0].message.content
        
        return {
            "success": True,
            "message": assistant_reply,
            "model": "gpt-4o",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Desculpe, ocorreu um erro: {str(e)}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
