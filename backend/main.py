from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    """Endpoint de exemplo para listar ações"""
    # Aqui você conectará com dados reais da B3
    sample_stocks = [
        {"symbol": "PETR4", "name": "Petrobras PN", "price": 38.50},
        {"symbol": "VALE3", "name": "Vale ON", "price": 61.20},
        {"symbol": "ITUB4", "name": "Itaú Unibanco PN", "price": 26.80},
    ]
    return {"stocks": sample_stocks}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

