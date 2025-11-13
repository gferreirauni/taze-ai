from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import uvicorn

app = FastAPI(
    title="Taze AI API",
    description="API inteligente para análise de investimentos da B3",
    version="1.0.0"
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL do Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_price_history(base_price: float, days: int = 30) -> list:
    """
    Gera histórico de preços realista para os últimos N dias
    """
    history = []
    current_date = datetime.now() - timedelta(days=days)
    current_price = base_price * random.uniform(0.85, 0.95)  # Começa um pouco abaixo
    
    for day in range(days):
        # Simula volatilidade diária (-3% a +3%)
        daily_change = random.uniform(-0.03, 0.03)
        current_price = current_price * (1 + daily_change)
        
        # Adiciona alguma tendência suave
        trend = random.uniform(-0.005, 0.01)
        current_price = current_price * (1 + trend)
        
        history.append({
            "date": (current_date + timedelta(days=day)).strftime("%Y-%m-%d"),
            "value": round(current_price, 2)
        })
    
    return history

def calculate_daily_variation(history: list) -> float:
    """
    Calcula a variação percentual do dia (último vs penúltimo)
    """
    if len(history) < 2:
        return 0.0
    
    last_price = history[-1]["value"]
    previous_price = history[-2]["value"]
    variation = ((last_price - previous_price) / previous_price) * 100
    
    return round(variation, 2)

# Dados mockados das ações
MOCK_STOCKS = [
    {
        "symbol": "PETR4",
        "name": "Petrobras PN",
        "base_price": 38.50,
        "sector": "Petróleo e Gás"
    },
    {
        "symbol": "VALE3",
        "name": "Vale ON",
        "base_price": 61.20,
        "sector": "Mineração"
    },
    {
        "symbol": "ITUB4",
        "name": "Itaú Unibanco PN",
        "base_price": 26.80,
        "sector": "Financeiro"
    },
    {
        "symbol": "WEGE3",
        "name": "WEG ON",
        "base_price": 42.15,
        "sector": "Indústria"
    },
    {
        "symbol": "BBAS3",
        "name": "Banco do Brasil ON",
        "base_price": 28.90,
        "sector": "Financeiro"
    }
]

@app.get("/")
async def root():
    """Endpoint de boas-vindas"""
    return {
        "message": "Bem-vindo à Taze AI API! 🚀",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "service": "Taze AI Backend"
    }

@app.get("/api/stocks")
async def get_stocks():
    """
    Retorna lista de ações com dados mockados realistas incluindo histórico
    """
    stocks_data = []
    
    for stock in MOCK_STOCKS:
        history = generate_price_history(stock["base_price"], days=30)
        current_price = history[-1]["value"]
        daily_variation = calculate_daily_variation(history)
        
        stocks_data.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "sector": stock["sector"],
            "currentPrice": current_price,
            "dailyVariation": daily_variation,
            "history": history
        })
    
    return {
        "stocks": stocks_data,
        "timestamp": datetime.now().isoformat(),
        "count": len(stocks_data)
    }

@app.get("/api/stocks/{symbol}")
async def get_stock_detail(symbol: str):
    """
    Retorna detalhes de uma ação específica
    """
    stock = next((s for s in MOCK_STOCKS if s["symbol"] == symbol.upper()), None)
    
    if not stock:
        return {"error": "Ação não encontrada"}, 404
    
    history = generate_price_history(stock["base_price"], days=90)
    current_price = history[-1]["value"]
    daily_variation = calculate_daily_variation(history)
    
    # Calcula métricas adicionais
    week_ago_price = history[-7]["value"] if len(history) >= 7 else history[0]["value"]
    week_variation = ((current_price - week_ago_price) / week_ago_price) * 100
    
    month_ago_price = history[-30]["value"] if len(history) >= 30 else history[0]["value"]
    month_variation = ((current_price - month_ago_price) / month_ago_price) * 100
    
    return {
        "symbol": stock["symbol"],
        "name": stock["name"],
        "sector": stock["sector"],
        "currentPrice": current_price,
        "dailyVariation": daily_variation,
        "weekVariation": round(week_variation, 2),
        "monthVariation": round(month_variation, 2),
        "history": history,
        "volume": random.randint(10000000, 50000000),
        "marketCap": round(current_price * random.uniform(50, 200) * 1000000000, 2)
    }

@app.get("/api/portfolio/summary")
async def get_portfolio_summary():
    """
    Retorna resumo da carteira (dados mockados para demo)
    """
    return {
        "totalValue": 125478.90,
        "dailyChange": 2.34,
        "dailyChangeValue": 2876.45,
        "stocksCount": 5,
        "totalInvested": 110000.00,
        "totalProfit": 15478.90,
        "profitPercentage": 14.07
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

@app.post("/api/ai/analyze")
async def analyze_stock(request: AIAnalysisRequest):
    """
    Endpoint de análise de ações com IA (versão mockada)
    Em produção, integraria com OpenAI GPT-4
    """
    analysis = mock_ai_analysis(
        request.symbol,
        request.currentPrice,
        request.dailyVariation,
        request.history
    )
    
    return analysis

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

