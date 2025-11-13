from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

