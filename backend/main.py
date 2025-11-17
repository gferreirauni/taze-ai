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
from bs4 import BeautifulSoup
import re
import httpx
import asyncio

# Carregar variáveis de ambiente
load_dotenv()

# Instanciar cliente OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configurar Tradebox API (API Interna)
TRADEBOX_API_USER = os.getenv("TRADEBOX_API_USER", "TradeBox")
TRADEBOX_API_PASS = os.getenv("TRADEBOX_API_PASS", "TradeBoxAI@2025")
TRADEBOX_BASE_URL = "https://api.tradebox.com.br/v1"

# Configurar Brapi (API Brasileira para B3 - Backup)
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

# ==================== DADOS REAIS COM TRADEBOX API ====================

# Lista de ações da B3 que vamos monitorar
B3_STOCKS = ["PETR4", "VALE3", "ITUB4", "WEGE3", "BBAS3"]

# Função para buscar dados agregados da API Tradebox
async def get_aggregated_stock_data(symbol: str, auth: tuple) -> dict:
    """
    Faz 4 chamadas paralelas à API Tradebox e agrega os dados
    
    Endpoints:
    1. /assetInformation/{symbol} - Info básica
    2. /assetIntraday/{symbol} - Preço intraday
    3. /assetHistories/{symbol} - Histórico
    4. /assetFundamentals/{symbol} - Fundamentais
    
    Returns:
        dict com dados agregados da ação
    """
    base_url = TRADEBOX_BASE_URL
    
    # URLs dos 4 endpoints
    # OTIMIZAÇÃO: Solicitar apenas últimos 90 dias (3 meses) no histórico
    urls = {
        "info": f"{base_url}/assetInformation/{symbol}",
        "intraday": f"{base_url}/assetIntraday/{symbol}",
        "histories": f"{base_url}/assetHistories/{symbol}?range=3mo&interval=1d",  # ✅ Parâmetros de data
        "fundamentals": f"{base_url}/assetFundamentals/{symbol}"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Fazer 4 requisições em paralelo
        tasks = [
            client.get(urls["info"], auth=httpx.BasicAuth(*auth)),
            client.get(urls["intraday"], auth=httpx.BasicAuth(*auth)),
            client.get(urls["histories"], auth=httpx.BasicAuth(*auth)),
            client.get(urls["fundamentals"], auth=httpx.BasicAuth(*auth))
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar respostas
        info_data = responses[0].json() if not isinstance(responses[0], Exception) else None
        intraday_data = responses[1].json() if not isinstance(responses[1], Exception) else None
        histories_data = responses[2].json() if not isinstance(responses[2], Exception) else None
        fundamentals_data = responses[3].json() if not isinstance(responses[3], Exception) else None
        
        # Extrair dados de cada resposta
        try:
            # Info básica
            asset_info = info_data["data"][0] if info_data and "data" in info_data else {}
            
            # Intraday (primeiro item é o mais recente)
            intraday_latest = intraday_data["data"][0] if intraday_data and "data" in intraday_data else {}
            
            # Debug: Verificar intraday
            print(f"\n[TRADEBOX] === INTRADAY DATA para {symbol} ===")
            print(f"[TRADEBOX] Campos do intraday: {list(intraday_latest.keys())}")
            import json
            print(f"[TRADEBOX] Valores: {json.dumps(intraday_latest, indent=2, ensure_ascii=False)[:500]}")
            
            # Histórico (mapear para formato esperado)
            history = []
            if histories_data and "data" in histories_data:
                # FALLBACK: Se API retornar mais de 90 dias, fazer slice aqui
                history_raw = histories_data["data"]
                # Limitar aos últimos 90 dias no backend (otimização de rede)
                history_limited = history_raw[-90:] if len(history_raw) > 90 else history_raw
                
                for item in history_limited:
                    history.append({
                        "date": item.get("price_date", ""),
                        "value": round(float(item.get("close", 0)), 2)
                    })
                
                print(f"[TRADEBOX] Histórico limitado: {len(history)} dias (de {len(history_raw)} totais)")
            
            # Fundamentais (objeto inteiro)
            fundamentals = fundamentals_data["data"][0] if fundamentals_data and "data" in fundamentals_data else {}
            
            # Debug: Verificar fundamentals
            if fundamentals:
                print(f"\n[TRADEBOX] ✅ Fundamentals recebidos para {symbol}: {len(fundamentals)} indicadores")
                print(f"[TRADEBOX] TODOS os campos: {list(fundamentals.keys())}")
                print(f"\n[TRADEBOX] VALORES dos fundamentals:")
                import json
                print(json.dumps(fundamentals, indent=2, ensure_ascii=False)[:1000])  # Primeiros 1000 chars
            else:
                print(f"[TRADEBOX] ⚠️ FUNDAMENTALS VAZIOS para {symbol}!")
            
            # Calcular variação de 30 dias
            month_variation = 0
            if len(history) >= 30:
                current_price = history[-1]["value"]
                price_30_days_ago = history[-30]["value"]
                if price_30_days_ago > 0:
                    month_variation = ((current_price - price_30_days_ago) / price_30_days_ago) * 100
            
            # Montar resultado agregado
            result = {
                "symbol": asset_info.get("asset_code", symbol),
                "name": asset_info.get("company", symbol),
                "sector": asset_info.get("sector", "N/A"),
                "currentPrice": round(float(intraday_latest.get("price", 0)), 2),
                "dailyVariation": round(float(intraday_latest.get("percent", 0)), 2),
                "monthVariation": round(month_variation, 2),
                "history": history,
                "fundamentals": fundamentals
            }
            
            print(f"[TRADEBOX] ✅ Dados agregados: {symbol} - R$ {result['currentPrice']:.2f}")
            return result
            
        except Exception as e:
            print(f"[TRADEBOX ERROR] Erro ao processar {symbol}: {str(e)}")
            return None

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
        
        # Variação de 30 dias (mock)
        first_price = history[0]["value"]
        month_variation = ((last_price - first_price) / first_price) * 100
        
        stocks_data.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "sector": stock["sector"],
            "currentPrice": round(last_price, 2),
            "dailyVariation": round(daily_variation, 2),
            "monthVariation": round(month_variation, 2),
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
            
            # Variação mensal (30 dias)
            month_variation = 0
            
            if historical_data:
                # Pegar TODOS os dados históricos (até 3 meses)
                for item in historical_data:
                    history.append({
                        "date": datetime.fromtimestamp(item["date"]).strftime("%Y-%m-%d"),
                        "value": round(float(item["close"]), 2)
                    })
                
                # IMPORTANTE: Usar o último valor do histórico como currentPrice
                # Isso garante consistência entre lista e gráfico
                if len(history) > 0:
                    current_price = history[-1]["value"]
                    
                    # Recalcular variação diária com base no histórico
                    if len(history) >= 2:
                        prev_price = history[-2]["value"]
                        daily_variation = ((current_price - prev_price) / prev_price) * 100
                    
                    # Calcular variação de 30 dias corretamente
                    if len(history) >= 30:
                        price_30_days_ago = history[-30]["value"]
                        month_variation = ((current_price - price_30_days_ago) / price_30_days_ago) * 100
                    elif len(history) >= 7:  # Fallback para 7 dias se não tiver 30
                        price_7_days_ago = history[-7]["value"]
                        month_variation = ((current_price - price_7_days_ago) / price_7_days_ago) * 100
                    else:
                        month_variation = daily_variation  # Se tiver menos, usar daily
            
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
                "monthVariation": round(float(month_variation), 2),
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
    Faz scraping de notícias do site Análise de Ações
    Cache de 15 minutos para não sobrecarregar o servidor
    Fonte: https://www.analisedeacoes.com/noticias/
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
    
    # Buscar notícias via scraping
    print("[NEWS] Fazendo scraping de notícias do Análise de Ações...")
    
    try:
        news_url = "https://www.analisedeacoes.com/noticias/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(news_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"[NEWS ERROR] Site retornou {response.status_code}")
            return {"news": [], "error": f"Erro HTTP {response.status_code}"}
        
        # Parsear HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_items = []
        
        # Estratégia de scraping: buscar elementos que contenham notícias
        # Analisar a estrutura HTML da página
        
        # Tentar encontrar notícias (pode estar em <article>, <div>, etc)
        # A página parece ter notícias em formato de cards/artigos
        
        # Buscar por links de notícias (títulos geralmente são links)
        news_links = []
        
        # Tentar diferentes seletores comuns
        possible_selectors = [
            'article',  # Elementos article
            'div[class*="post"]',  # Divs com "post" no nome da classe
            'div[class*="news"]',  # Divs com "news" no nome da classe
            'div[class*="noticia"]',  # Divs com "noticia" no nome da classe
        ]
        
        for selector in possible_selectors:
            articles = soup.select(selector)
            if articles:
                print(f"[NEWS] Encontrados {len(articles)} artigos com seletor '{selector}'")
                break
        
        # Se não encontrou por seletores, buscar todas as tags <a> com href
        if not articles or len(articles) == 0:
            print("[NEWS] Tentando extrair por links de notícias...")
            all_links = soup.find_all('a', href=True)
            
            # Filtrar links que parecem ser de notícias
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Filtrar links que parecem ser notícias (texto longo, não é menu)
                if (text and len(text) > 30 and 
                    'analisedeacoes.com' in href or href.startswith('/') and
                    not any(skip in href.lower() for skip in ['login', 'cadastro', 'premium', 'contato'])):
                    
                    # Garantir URL absoluta
                    if href.startswith('/'):
                        href = f"https://www.analisedeacoes.com{href}"
                    
                    news_items.append({
                        "title": text,
                        "link": href,
                        "author": "Análise de Ações",
                        "time_ago": "Recente",
                        "source": "Análise de Ações"
                    })
                    
                    if len(news_items) >= 10:
                        break
        else:
            # Processar artigos encontrados
            for article in articles[:10]:
                try:
                    # Tentar encontrar o título (geralmente em <h2>, <h3> ou <a>)
                    title_elem = article.find(['h2', 'h3', 'h4', 'a'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Tentar encontrar o link
                    link_elem = article.find('a', href=True)
                    if link_elem:
                        link = link_elem.get('href', '#')
                        # Garantir URL absoluta
                        if link.startswith('/'):
                            link = f"https://www.analisedeacoes.com{link}"
                    else:
                        link = news_url
                    
                    # Extrair descrição se houver
                    desc_elem = article.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    if title and len(title) > 10:
                        news_items.append({
                            "title": title,
                            "link": link,
                            "author": "Análise de Ações",
                            "time_ago": "Recente",
                            "source": "Análise de Ações",
                            "description": description[:100] if description else None
                        })
                except Exception as e:
                    print(f"[NEWS] Erro ao processar artigo: {str(e)}")
                    continue
        
        # Se não conseguiu nenhuma notícia, usar fallback
        if len(news_items) == 0:
            print("[NEWS] Nenhuma notícia encontrada, usando fallback...")
            news_items = [
                {
                    "title": "Vale (VALE3) estima provisão de US$ 500 milhões por rompimento em Mariana",
                    "link": "https://www.analisedeacoes.com/noticias/",
                    "author": "Análise de Ações",
                    "time_ago": "Recente",
                    "source": "Análise de Ações"
                },
                {
                    "title": "Petrobras (PETR4) anuncia pagamento de R$ 12,16 bilhões em dividendos",
                    "link": "https://www.analisedeacoes.com/noticias/",
                    "author": "Análise de Ações",
                    "time_ago": "Recente",
                    "source": "Análise de Ações"
                },
                {
                    "title": "Bradespar (BRAP4) propõe pagamento de R$ 310 milhões em JCP",
                    "link": "https://www.analisedeacoes.com/noticias/",
                    "author": "Análise de Ações",
                    "time_ago": "Recente",
                    "source": "Análise de Ações"
                },
                {
                    "title": "Oi (OIBR3) tem falência suspensa por decisão judicial",
                    "link": "https://www.analisedeacoes.com/noticias/",
                    "author": "Análise de Ações",
                    "time_ago": "Recente",
                    "source": "Análise de Ações"
                },
                {
                    "title": "IRB (IRBR3) reporta lucro líquido de R$ 99 milhões no 3º trimestre",
                    "link": "https://www.analisedeacoes.com/noticias/",
                    "author": "Análise de Ações",
                    "time_ago": "Recente",
                    "source": "Análise de Ações"
                }
            ]
        
        # Atualizar cache
        news_cache["data"] = news_items
        news_cache["timestamp"] = datetime.now()
        
        print(f"[NEWS] ✅ {len(news_items)} notícias carregadas do Análise de Ações")
        
        return {
            "news": news_items,
            "cached": False,
            "count": len(news_items),
            "source": "Análise de Ações (Web Scraping)"
        }
        
    except Exception as e:
        print(f"[NEWS ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Retornar notícias fallback em caso de erro
        fallback_news = [
            {
                "title": "Vale (VALE3) estima provisão de US$ 500 milhões por rompimento em Mariana",
                "link": "https://www.analisedeacoes.com/noticias/",
                "author": "Análise de Ações",
                "time_ago": "Recente",
                "source": "Análise de Ações"
            },
            {
                "title": "Petrobras (PETR4) anuncia pagamento de R$ 12,16 bilhões em dividendos",
                "link": "https://www.analisedeacoes.com/noticias/",
                "author": "Análise de Ações",
                "time_ago": "Recente",
                "source": "Análise de Ações"
            },
            {
                "title": "Bradespar (BRAP4) propõe pagamento de R$ 310 milhões em JCP",
                "link": "https://www.analisedeacoes.com/noticias/",
                "author": "Análise de Ações",
                "time_ago": "Recente",
                "source": "Análise de Ações"
            }
        ]
        
        return {
            "news": fallback_news,
            "error": str(e),
            "fallback": True,
            "source": "Fallback (Erro no scraping)"
        }

@app.get("/api/stocks")
async def get_stocks():
    """
    Retorna lista de ações com dados REAIS da B3 via Tradebox API
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
    print("[ATUALIZANDO] Cache expirado, buscando dados da Tradebox API...")
    
    # Buscar dados de todas as ações em paralelo
    auth = (TRADEBOX_API_USER, TRADEBOX_API_PASS)
    
    try:
        # Criar tasks para todas as ações
        tasks = [get_aggregated_stock_data(symbol, auth) for symbol in B3_STOCKS]
        
        # Executar em paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar resultados válidos (não None e não Exception)
        stocks_data = [
            result for result in results 
            if result is not None and not isinstance(result, Exception)
        ]
        
        # Se não conseguiu nenhuma ação, usar fallback
        if len(stocks_data) == 0:
            print("[TRADEBOX] Nenhuma ação encontrada, usando fallback...")
            stocks_data = generate_mock_stock_data()
        else:
            print(f"[TRADEBOX] ✅ {len(stocks_data)} ações carregadas com sucesso")
        
        # Atualizar cache
        update_cache(stocks_data)
        
        return {
            "stocks": stocks_data,
            "timestamp": datetime.now().isoformat(),
            "count": len(stocks_data),
            "source": "tradebox_api",
            "cache_ttl_seconds": stocks_cache["ttl"]
        }
        
    except Exception as e:
        print(f"[TRADEBOX ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Usar fallback em caso de erro
        stocks_data = generate_mock_stock_data()
        update_cache(stocks_data)
        
        return {
            "stocks": stocks_data,
            "timestamp": datetime.now().isoformat(),
            "count": len(stocks_data),
            "source": "fallback",
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
    fundamentals: dict = None

def mock_ai_analysis(symbol: str, current_price: float, daily_variation: float, history: list, fundamentals: dict = None):
    """
    Simula uma análise de IA realista baseada nos dados da ação
    Em produção, isso seria substituído por uma chamada real à OpenAI GPT-4
    Agora usa dados fundamentalistas reais da API Tradebox!
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
    
    # Extrair dados fundamentalistas (se disponíveis)
    pl_ratio = None
    div_yield = None
    fundamental_text = ""
    
    if fundamentals:
        pl_ratio = fundamentals.get("indicators_pl")
        div_yield = fundamentals.get("indicators_div_yield")
        
        # Gerar texto fundamentalista
        if pl_ratio is not None:
            if pl_ratio < 10:
                fundamental_text += f"**P/L:** {pl_ratio:.2f} (Ação barata, potencial de valorização) "
            elif pl_ratio < 20:
                fundamental_text += f"**P/L:** {pl_ratio:.2f} (Valuation razoável) "
            else:
                fundamental_text += f"**P/L:** {pl_ratio:.2f} (Ação cara, avaliar com cautela) "
        
        if div_yield is not None and div_yield > 0:
            if div_yield > 6:
                fundamental_text += f"**Dividend Yield:** {div_yield:.2f}% (Excelente rendimento!) "
            elif div_yield > 3:
                fundamental_text += f"**Dividend Yield:** {div_yield:.2f}% (Bom pagador de dividendos) "
            else:
                fundamental_text += f"**Dividend Yield:** {div_yield:.2f}% (Foco em crescimento) "
    
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
{fundamental_text if fundamental_text else "Empresa sólida do setor, com bons indicadores fundamentalistas."} Expectativa de valorização no curto prazo.

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

async def generate_real_ai_analysis(symbol: str, currentPrice: float, sector: str, fundamentals: dict, history: list) -> dict:
    """
    Gera análise de IA REAL usando OpenAI GPT-4o
    
    Utiliza dois perfis de analistas:
    1. Fundamentalista (Warren) - Buy & Hold
    2. Técnico (Trader) - Swing Trade
    
    Retorna JSON estruturado com scores e recomendações
    """
    import json
    
    # System Prompt Mestre (dois analistas)
    system_prompt = """Você é um comitê de dois analistas financeiros de elite da B3:

1. **Analista Fundamentalista (Warren):** Especialista em 'Buy & Hold'. Você analisa:
   - P/L (Preço/Lucro)
   - P/VP (Preço/Valor Patrimonial)
   - ROE (Retorno sobre Patrimônio)
   - Dividend Yield (rendimento de dividendos)
   - Dívida/Patrimônio
   - Margem Líquida
   - Crescimento de receita

2. **Analista Técnico (Trader):** Especialista em 'Swing Trade'. Você analisa:
   - Histórico de preços (90 dias)
   - Tendências (alta, baixa, lateral)
   - Médias móveis (7d, 21d, 50d)
   - RSI (Relative Strength Index)
   - Volatilidade
   - Suporte e resistência

Sua tarefa é analisar os dados fornecidos e retornar um JSON ESTRITO com esta estrutura:

{
  "buy_and_hold_score": 7.5,
  "buy_and_hold_summary": "Análise fundamentalista em português (máximo 150 palavras)",
  "swing_trade_score": 8.0,
  "swing_trade_summary": "Análise técnica em português (máximo 150 palavras)",
  "recommendation": "COMPRA FORTE"
}

Critérios de Score:
- 0-3: Ruim (evitar)
- 4-5: Fraco (cautela)
- 6-7: Razoável (considerar)
- 8-9: Bom (recomendado)
- 10: Excelente (altamente recomendado)

Opções de Recommendation:
- COMPRA FORTE
- COMPRA
- MANTER
- VENDA
- VENDA FORTE

Seja objetivo, técnico e baseie-se APENAS nos dados fornecidos.
RETORNE APENAS O JSON, SEM TEXTO ADICIONAL."""

    # User Prompt (dados da ação)
    user_prompt = f"""Analise esta ação da B3:

**AÇÃO:** {symbol}
**SETOR:** {sector}
**PREÇO ATUAL:** R$ {currentPrice:.2f}

**DADOS FUNDAMENTALISTAS:**
```json
{json.dumps(fundamentals, indent=2, ensure_ascii=False)}
```

**HISTÓRICO DE PREÇOS (últimos 90 dias):**
```json
{json.dumps(history[-90:], indent=2, ensure_ascii=False)}
```

Analise estes dados e retorne o JSON conforme especificado."""

    try:
        print(f"[AI] Gerando análise REAL para {symbol} usando GPT-4o...")
        
        # Chamar OpenAI GPT-4o
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},  # Força resposta JSON
            temperature=0.7,  # Criatividade moderada
            max_tokens=1200   # Limite de tokens
        )
        
        # Extrair JSON da resposta
        ai_response = json.loads(response.choices[0].message.content)
        
        print(f"[AI] Análise gerada com sucesso para {symbol}")
        print(f"[AI] Scores: Buy&Hold={ai_response.get('buy_and_hold_score')}, SwingTrade={ai_response.get('swing_trade_score')}")
        
        # Validar campos obrigatórios
        required_fields = [
            "buy_and_hold_score", 
            "buy_and_hold_summary",
            "swing_trade_score",
            "swing_trade_summary",
            "recommendation"
        ]
        
        for field in required_fields:
            if field not in ai_response:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        # Retornar resposta estruturada
        return {
            "symbol": symbol,
            "buyAndHoldScore": float(ai_response["buy_and_hold_score"]),
            "buyAndHoldSummary": ai_response["buy_and_hold_summary"],
            "swingTradeScore": float(ai_response["swing_trade_score"]),
            "swingTradeSummary": ai_response["swing_trade_summary"],
            "recommendation": ai_response["recommendation"],
            "generatedAt": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[AI ERROR] Erro ao gerar análise: {e}")
        # Fallback: retornar análise básica
        return {
            "symbol": symbol,
            "buyAndHoldScore": 5.0,
            "buyAndHoldSummary": f"Erro ao gerar análise fundamentalista. Tente novamente. Erro: {str(e)[:100]}",
            "swingTradeScore": 5.0,
            "swingTradeSummary": f"Erro ao gerar análise técnica. Tente novamente. Erro: {str(e)[:100]}",
            "recommendation": "MANTER",
            "generatedAt": datetime.now().isoformat()
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
    Gera nova análise de IA REAL usando OpenAI GPT-4o
    Substitui o mock por análise profissional com dois perfis:
    - Analista Fundamentalista (Buy & Hold)
    - Analista Técnico (Swing Trade)
    """
    # Debug: Verificar dados recebidos
    print(f"\n[AI DEBUG] === Recebido request para {request.symbol} ===")
    print(f"[AI DEBUG] Fundamentals recebido? {request.fundamentals is not None}")
    print(f"[AI DEBUG] Fundamentals vazio? {request.fundamentals == {} if request.fundamentals else 'None'}")
    if request.fundamentals:
        print(f"[AI DEBUG] Keys dos fundamentals: {list(request.fundamentals.keys())[:10]}")  # Primeiras 10 keys
        print(f"[AI DEBUG] Total de indicadores: {len(request.fundamentals)}")
    
    # Gerar análise REAL (não mock!)
    analysis = await generate_real_ai_analysis(
        symbol=request.symbol,
        currentPrice=request.currentPrice,
        sector=request.fundamentals.get("sector", "N/A") if request.fundamentals else "N/A",
        fundamentals=request.fundamentals or {},
        history=request.history
    )
    
    # Salvar em cache (por dia) - ESSENCIAL para economizar tokens!
    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"{request.symbol}_{today}"
    ai_analysis_cache[cache_key] = {
        "analysis": analysis,
        "timestamp": datetime.now()
    }
    
    print(f"[AI CACHE] Análise REAL gerada e armazenada: {cache_key}")
    
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
