from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Any, Optional, Tuple
import random
import uvicorn
import os
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import re
import httpx
import asyncio

from cache_manager import CacheManager

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
cache = CacheManager()

STOCKS_CACHE_KEY = "stocks:aggregated"
STOCKS_CACHE_TTL = int(os.getenv("CACHE_STOCKS_TTL", "300"))
NEWS_CACHE_KEY = "news:latest"
NEWS_CACHE_TTL = int(os.getenv("CACHE_NEWS_TTL", "900"))
AI_ANALYSIS_CACHE_TTL = int(os.getenv("CACHE_AI_TTL", str(60 * 60 * 24)))


def current_iso_timestamp() -> str:
    return datetime.now().isoformat()


def cache_age_seconds(stored_at: Optional[str]) -> Optional[float]:
    if not stored_at:
        return None
    try:
        stored_dt = datetime.fromisoformat(stored_at)
        return (datetime.now() - stored_dt).total_seconds()
    except ValueError:
        return None

# ==================== DADOS REAIS COM TRADEBOX API ====================

# Lista de ações da B3 que vamos monitorar
B3_STOCKS = ["PETR4", "BBAS3", "VALE3", "MGLU3", "WEGE3"]

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
            intraday_latest = intraday_data["data"][0] if intraday_data and "data" in intraday_data and len(intraday_data["data"]) > 0 else {}
            
            # Verificar se intraday está vazio (API retorna erro)
            if not intraday_latest:
                print(f"[TRADEBOX] ⚠️ Intraday vazio para {symbol}, usando fallback")
            
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
            
            # Verificar fundamentals
            if fundamentals:
                print(f"[TRADEBOX] ✅ Fundamentals: {len(fundamentals)} indicadores (P/L: {fundamentals.get('indicators_pl')}, DY: {fundamentals.get('indicators_div_yield')}%)")
            else:
                print(f"[TRADEBOX] ⚠️ Fundamentals vazios para {symbol}")
            
            # Calcular variação de 30 dias
            month_variation = 0
            if len(history) >= 30:
                current_price = history[-1]["value"]
                price_30_days_ago = history[-30]["value"]
                if price_30_days_ago > 0:
                    month_variation = ((current_price - price_30_days_ago) / price_30_days_ago) * 100
            
            # CORREÇÃO: Se intraday estiver vazio, usar dados do histórico e fundamentals
            if not intraday_latest or not intraday_latest.get("price"):
                print(f"[TRADEBOX] ⚠️ Intraday vazio para {symbol}, usando fallback (histórico + fundamentals)")
                # Preço atual = último valor do histórico
                current_price_value = history[-1]["value"] if history else 0
                # Variação diária = oscillations_day dos fundamentals
                daily_variation_value = fundamentals.get("oscillations_day", 0) if fundamentals else 0
            else:
                # Usar dados do intraday normalmente
                current_price_value = float(intraday_latest.get("price", 0))
                daily_variation_value = float(intraday_latest.get("percent", 0))
            
            # Montar resultado agregado
            result = {
                "symbol": asset_info.get("asset_code", symbol),
                "name": asset_info.get("company", symbol),
                "sector": asset_info.get("sector", "N/A"),
                "currentPrice": round(current_price_value, 2),
                "dailyVariation": round(daily_variation_value, 2),
                "monthVariation": round(month_variation, 2),
                "history": history,
                "fundamentals": fundamentals
            }
            
            print(f"[TRADEBOX] ✅ Dados finais: {symbol} - R$ {result['currentPrice']:.2f} ({result['dailyVariation']:+.2f}%) | Fundamentals: {len(fundamentals)} indicadores")
            return result
            
        except Exception as e:
            print(f"[TRADEBOX ERROR] Erro ao processar {symbol}: {str(e)}")
            return None

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

async def refresh_stocks_cache() -> Tuple[list[dict[str, Any]], str, str]:
    """
    Recarrega dados da Tradebox e persiste no cache distribuido.
    Retorna (dados, timestamp_iso, fonte).
    """
    auth = (TRADEBOX_API_USER, TRADEBOX_API_PASS)
    source = "tradebox_api"

    try:
        tasks = [get_aggregated_stock_data(symbol, auth) for symbol in B3_STOCKS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        stocks_data = [
            result for result in results
            if isinstance(result, dict)
        ]

        if len(stocks_data) == 0:
            print("[TRADEBOX] Nenhuma acao valida recebida, usando fallback mockado.")
            source = "fallback"
            stocks_data = generate_mock_stock_data()
        else:
            print(f"[TRADEBOX] OK {len(stocks_data)} acoes carregadas com sucesso")
    except Exception as exc:
        print(f"[TRADEBOX ERROR] {exc}")
        source = "fallback"
        stocks_data = generate_mock_stock_data()

    stored_at = current_iso_timestamp()
    await cache.set(
        STOCKS_CACHE_KEY,
        {
            "data": stocks_data,
            "stored_at": stored_at,
            "source": source,
        },
        STOCKS_CACHE_TTL,
    )
    return stocks_data, stored_at, source


async def get_cached_stocks_data(force_refresh: bool = False) -> Tuple[list[dict[str, Any]], Optional[str], bool, str]:
    """
    Recupera dados do cache compartilhado ou atualiza se necessario.
    Retorna (dados, timestamp_iso, veio_do_cache, fonte_original)
    """
    if not force_refresh:
        cached_entry = await cache.get(STOCKS_CACHE_KEY)
        if cached_entry and isinstance(cached_entry, dict) and cached_entry.get("data"):
            return (
                cached_entry["data"],
                cached_entry.get("stored_at"),
                True,
                cached_entry.get("source", "tradebox_api")
            )

    data, stored_at, source = await refresh_stocks_cache()
    return data, stored_at, False, source


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
    cache_entry = await cache.get(STOCKS_CACHE_KEY)
    cache_status = "warm" if cache_entry else "cold"
    cache_age = cache_age_seconds(cache_entry.get("stored_at")) if cache_entry else None
    return {
        "status": "healthy",
        "service": "Taze AI Backend",
        "cache_status": cache_status,
        "cache_age_seconds": cache_age,
        "data_source": "tradebox",
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
    cached_news = await cache.get(NEWS_CACHE_KEY)
    if cached_news and cached_news.get("data"):
        age = cache_age_seconds(cached_news.get("stored_at"))
        print("[NEWS CACHE] Retornando noticias do cache compartilhado")
        return {
            "news": cached_news["data"],
            "cached": True,
            "cache_age_seconds": age,
            "source": cached_news.get("source", "Analise de Acoes (cache)")
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
        
        # Atualizar cache distribu��do
        await cache.set(
            NEWS_CACHE_KEY,
            {
                "data": news_items,
                "stored_at": current_iso_timestamp(),
                "source": "Anǭlise de A����es (Web Scraping)"
            },
            NEWS_CACHE_TTL
        )
        
        print(f"[NEWS] ✅ {len(news_items)} notícias carregadas do Análise de Ações")
        
        return {
            "news": news_items,
            "cached": False,
            "count": len(news_items),
            "source": "Analise de Acoes (Web Scraping)"
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
    Retorna lista de acoes com dados REAIS da B3 via Tradebox API
    Implementa cache distribuido para otimizar performance
    """
    stocks_data, stored_at, from_cache, data_source = await get_cached_stocks_data()
    age = cache_age_seconds(stored_at)

    response = {
        "stocks": stocks_data,
        "timestamp": stored_at or current_iso_timestamp(),
        "count": len(stocks_data),
        "source": "cache" if from_cache else data_source,
        "cache_ttl_seconds": STOCKS_CACHE_TTL
    }

    if from_cache:
        response["cache_age_seconds"] = age

    return response


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
        # Buscar dados atuais (cache compartilhado)
        stocks_data, _, _, _ = await get_cached_stocks_data()
        
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

async def generate_real_ai_analysis(symbol: str, currentPrice: float, sector: str, fundamentals: dict, history: list) -> dict:
    """
    Gera análise de IA REAL usando OpenAI GPT-4o
    
    Utiliza TRÊS perfis de analistas:
    1. Fundamentalista (Warren) - Buy & Hold
    2. Técnico (Trader) - Swing Trade
    3. Volatilidade (Viper) - Day Trade
    
    Retorna JSON estruturado com scores e recomendações
    """
    import json
    
    # System Prompt Mestre (TRÊS analistas)
    system_prompt = """Você é um comitê de TRÊS analistas financeiros de elite:

1. **Analista Fundamentalista (Warren):** Focado em 'Buy & Hold' (longo prazo, anos). 
   Você ignora volatilidade diária. Sua análise foca EXCLUSIVAMENTE em fundamentalismo (P/L, P/VP, ROE, Dividend Yield e Dívida).
   
   **CAMPOS DISPONÍVEIS NOS DADOS:**
   - indicators_pl (P/L - Preço/Lucro)
   - indicators_pvp (P/VP - Preço/Valor Patrimonial)
   - indicators_roe (ROE - Retorno sobre Patrimônio)
   - indicators_div_yield (Dividend Yield %)
   - indicators_roic (ROIC %)
   - indicators_marg_liquida (Margem Líquida %)
   - indicators_div_br_patrim (Dívida Bruta/Patrimônio)
   - indicators_cresc_rec (Crescimento de Receita %)

2. **Analista Técnico (Trader):** Focado em 'Swing Trade' (médio prazo, semanas/meses). 
   Você usa o histórico de 90 dias para identificar tendências, médias móveis, suporte e resistência.

3. **Analista de Volatilidade (Viper):** Focado em 'Day Trade' (curto prazo, 1-2 dias). 
   Você analisa a volatilidade, oscillations_day e os min_52_weeks/max_52_weeks para oportunidades rápidas.

**REGRA CRÍTICA DE LÓGICA:** Sua análise técnica (suporte/resistência) DEVE ser 100% coerente com o currentPrice (preço atual) fornecido. 
Nunca diga que uma resistência (teto) é MENOR que o preço atual. Use o currentPrice como sua âncora para definir suportes (abaixo) e resistências (acima).

**Sua tarefa:** Analisar os dados fornecidos e retornar um JSON ESTRITO:

{
  "buy_and_hold_score": 7.5,
  "buy_and_hold_summary": "Análise fundamentalista (1-2 frases).",
  "swing_trade_score": 8.0,
  "swing_trade_summary": "Análise técnica de médio prazo (1-2 frases).",
  "day_trade_score": 6.5,
  "day_trade_summary": "Análise de volatilidade de curto prazo (1-2 frases).",
  "recommendation": "COMPRA FORTE"
}

**Critérios de Score:**
- 0-3: Ruim (evitar)
- 4-5: Fraco (cautela)
- 6-7: Razoável (considerar)
- 8-9: Bom (recomendado)
- 10: Excelente (altamente recomendado)

**Opções de Recommendation:**
COMPRA FORTE | COMPRA | MANTER | VENDA

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
        print(f"[AI] Scores: Buy&Hold={ai_response.get('buy_and_hold_score')}, SwingTrade={ai_response.get('swing_trade_score')}, DayTrade={ai_response.get('day_trade_score')}")
        
        # Validar campos obrigatórios
        required_fields = [
            "buy_and_hold_score", 
            "buy_and_hold_summary",
            "swing_trade_score",
            "swing_trade_summary",
            "day_trade_score",
            "day_trade_summary",
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
            "dayTradeScore": float(ai_response["day_trade_score"]),
            "dayTradeSummary": ai_response["day_trade_summary"],
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
            "dayTradeScore": 5.0,
            "dayTradeSummary": f"Erro ao gerar análise de volatilidade. Tente novamente. Erro: {str(e)[:100]}",
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
    cache_key = f"ai_analysis:{symbol.upper()}_{today}"
    
    cached_entry = await cache.get(cache_key)
    if cached_entry and cached_entry.get("analysis"):
        return {
            "cached": True,
            "analysis": cached_entry["analysis"],
            "generated_at": cached_entry.get("timestamp")
        }
    
    return {
        "cached": False,
        "message": "Nenhuma análise do dia encontrada. Clique em 'Gerar Análise'."
    }

@app.post("/api/ai/analyze")
async def analyze_stock(request: AIAnalysisRequest):
    """
    Gera nova análise de IA REAL usando OpenAI GPT-4o
    Análise profissional com TRÊS perfis:
    - Analista Fundamentalista (Buy & Hold)
    - Analista Técnico (Swing Trade)
    - Analista de Volatilidade (Day Trade)
    """
    # Log simplificado
    fund_count = len(request.fundamentals) if request.fundamentals else 0
    print(f"\n[AI] Gerando análise TRIPLA para {request.symbol} (Fundamentals: {fund_count} indicadores)")
    
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
    today = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"ai_analysis:{request.symbol.upper()}_{today}"
    await cache.set(
        cache_key,
        {
            "analysis": analysis,
            "timestamp": current_iso_timestamp()
        },
        AI_ANALYSIS_CACHE_TTL
    )
    
    print(f"[AI CACHE] Analise TRIPLA gerada e armazenada: {cache_key}")
    
    return analysis

# ==================== CHAT ASSISTANT ENDPOINTS ====================

class ChatMessage(BaseModel):
    message: str
    context: dict | None = None

@app.post("/api/ai/chat")
async def chat_with_assistant(request: ChatMessage):
    """
    Chat em tempo real com o Taze AI Assistant (OpenAI GPT-4)
    Usa Function Calling para buscar dados de ações quando necessário
    """
    try:
        # System prompt poderoso para o assistente financeiro
        system_prompt = """Você é o Taze AI, um analista financeiro sênior especialista em ações da B3 (Bolsa de Valores brasileira).

**Ações Disponíveis:** PETR4, BBAS3, VALE3, MGLU3, WEGE3

**Sua Personalidade:**
- Profissional, mas acessível e amigável
- Conciso e direto ao ponto
- Usa dados reais quando disponíveis
- Responde em Português do Brasil
- Usa emojis ocasionalmente

**Importante:**
- Quando o usuário perguntar sobre uma ação específica, você pode buscar dados em tempo real usando a função disponível
- Sempre lembre que você NÃO é uma recomendação formal de investimento
- Seja objetivo: máximo 200 palavras por resposta
"""

        # Definir tools (functions) disponíveis para a IA
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_data",
                    "description": "Busca dados em tempo real de uma ação da B3 (preço atual, variação, setor, fundamentais)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Símbolo da ação (ex: PETR4, VALE3, BBAS3, MGLU3, WEGE3)",
                                "enum": ["PETR4", "BBAS3", "VALE3", "MGLU3", "WEGE3"]
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            }
        ]
        
        # Primeira chamada à IA
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            tools=tools,
            tool_choice="auto",  # IA decide se precisa chamar função
            max_tokens=500,
            temperature=0.7,
        )
        
        response_message = response.choices[0].message
        
        # Verificar se a IA quer chamar uma função
        if response_message.tool_calls:
            # Executar a função solicitada
            tool_call = response_message.tool_calls[0]
            function_name = tool_call.function.name
            
            if function_name == "get_stock_data":
                import json
                function_args = json.loads(tool_call.function.arguments)
                symbol = function_args.get("symbol")
                
                print(f"[CHAT] IA solicitou dados de {symbol}")
                
                # Buscar dados da ação
                auth = (TRADEBOX_API_USER, TRADEBOX_API_PASS)
                stock_data = await get_aggregated_stock_data(symbol, auth)
                
                if stock_data:
                    function_response = json.dumps({
                        "symbol": stock_data.get("symbol"),
                        "name": stock_data.get("name"),
                        "currentPrice": stock_data.get("currentPrice"),
                        "dailyVariation": stock_data.get("dailyVariation"),
                        "sector": stock_data.get("sector"),
                        "fundamentals": {
                            "pl": stock_data.get("fundamentals", {}).get("indicators_pl"),
                            "pvp": stock_data.get("fundamentals", {}).get("indicators_pvp"),
                            "dividend_yield": stock_data.get("fundamentals", {}).get("indicators_div_yield"),
                            "roe": stock_data.get("fundamentals", {}).get("indicators_roe")
                        }
                    }, ensure_ascii=False)
                else:
                    function_response = json.dumps({"error": "Dados não disponíveis no momento"})
                
                # Segunda chamada com o resultado da função
                second_response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.message},
                        response_message,
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": function_response
                        }
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )
                
                assistant_reply = second_response.choices[0].message.content
        else:
            # Resposta direta sem função
            assistant_reply = response_message.content
        
        return {
            "success": True,
            "message": assistant_reply,
            "model": "gpt-4o",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"[CHAT ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Desculpe, ocorreu um erro: {str(e)}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
