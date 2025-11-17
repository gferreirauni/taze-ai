'use client'

import { useEffect, useState, useRef } from 'react'
import { Newspaper, Sparkles, TrendingUp, ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react'
import Autoplay from 'embla-carousel-autoplay'
import Sidebar from '@/components/dashboard/Sidebar'
import ChatWidget from '@/components/dashboard/ChatWidget'
import AIScoreCard from '@/components/dashboard/AIScoreCard'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@/components/ui/carousel'

interface Stock {
  symbol: string
  name: string
  sector: string
  currentPrice: number
  dailyVariation: number
  monthVariation?: number
  history: { date: string; value: number }[]
  fundamentals?: any
  ai_analysis?: {
    buyAndHoldScore: number
    buyAndHoldSummary: string
    swingTradeScore: number
    swingTradeSummary: string
    recommendation: string
    generatedAt: string
  }
}

interface NewsItem {
  title: string
  link: string
  author: string
  time_ago: string
  source: string
}

export default function Dashboard() {
  const [stocks, setStocks] = useState<Stock[]>([])
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)
  const [newsLoading, setNewsLoading] = useState(true)
  const [currentSlide, setCurrentSlide] = useState(0)
  const [carouselApi, setCarouselApi] = useState<any>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  
  // Plugin de autoplay para o carousel de ações (15 segundos)
  const plugin = useRef(
    Autoplay({ delay: 15000, stopOnInteraction: true })
  )

  // Plugin de autoplay para o carousel de notícias (10 segundos)
  const newsPlugin = useRef(
    Autoplay({ delay: 10000, stopOnInteraction: true })
  )

  // Rastrear slide atual de ações
  useEffect(() => {
    if (!carouselApi) return

    setCurrentSlide(carouselApi.selectedScrollSnap())

    carouselApi.on('select', () => {
      setCurrentSlide(carouselApi.selectedScrollSnap())
    })
  }, [carouselApi])

  const fetchData = async () => {
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const stocksResponse = await fetch('http://localhost:8000/api/stocks')
      
      if (!stocksResponse.ok) {
        throw new Error(`Erro: ${stocksResponse.status}`)
      }
      
      const stocksData = await stocksResponse.json()
      
      // Buscar análises em cache para cada ação
      const stocksWithAnalysis = await Promise.all(
        stocksData.stocks.map(async (stock: Stock) => {
          try {
            const analysisResponse = await fetch(`http://localhost:8000/api/ai/analysis/${stock.symbol}`)
            const analysisData = await analysisResponse.json()
            
            if (analysisData.cached && analysisData.analysis) {
              return { ...stock, ai_analysis: analysisData.analysis }
            }
            return stock
          } catch (error) {
            console.error(`Erro ao buscar análise de ${stock.symbol}:`, error)
            return stock
          }
        })
      )
      
      setStocks(stocksWithAnalysis)
    } catch (error) {
      console.error('Erro ao buscar dados:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {

    async function fetchNews() {
      try {
        const newsResponse = await fetch('http://localhost:8000/api/news')
        const newsData = await newsResponse.json()
        
        if (newsData.news && newsData.news.length > 0) {
          setNews(newsData.news.slice(0, 5))
        }
      } catch (error) {
        console.error('Erro ao buscar notícias:', error)
      } finally {
        setNewsLoading(false)
      }
    }

    fetchData()
    fetchNews()
    
    const stocksInterval = setInterval(fetchData, 300000)  // 5 minutos
    const newsInterval = setInterval(fetchNews, 900000)  // 15 minutos
    
    return () => {
      clearInterval(stocksInterval)
      clearInterval(newsInterval)
    }
  }, [])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-950">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-zinc-400">Carregando dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-zinc-950 relative overflow-hidden">
      {/* Background Gradient Sutil */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-950/20 via-zinc-950 to-zinc-950 pointer-events-none"></div>
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>
      
      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />

      {/* Mobile Menu Button */}
      <button
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        className="md:hidden fixed top-4 left-4 z-50 w-10 h-10 bg-zinc-800 border border-zinc-700 rounded-lg flex items-center justify-center hover:bg-emerald-500 hover:border-emerald-500 transition-all"
      >
        {sidebarCollapsed ? (
          <ChevronRight className="w-5 h-5 text-white" />
        ) : (
          <ChevronLeft className="w-5 h-5 text-white" />
        )}
      </button>

      <div className={`flex-1 p-4 md:p-6 relative z-10 h-screen overflow-hidden flex flex-col justify-center transition-all duration-300 ${
        sidebarCollapsed ? 'ml-0 md:ml-20' : 'ml-0 md:ml-64'
      }`}>
        {/* Header - Limpo e Moderno */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-1">
            <div className="relative">
              <Sparkles className="w-6 h-6 text-emerald-500 animate-pulse" />
              <div className="absolute inset-0 blur-xl bg-emerald-500/30 animate-pulse"></div>
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-white via-emerald-100 to-white bg-clip-text text-transparent">
              Painel de Decisão Taze AI
            </h1>
          </div>
          <p className="text-zinc-400 text-xs">
            Análises de IA para os principais ativos da B3
          </p>
        </div>

        {/* Container Centralizado */}
        <div className="relative px-8 md:px-16">
          
          {/* AI Score Cards Carousel */}
          <div className="mb-6">
            <Carousel
              setApi={setCarouselApi}
              plugins={[plugin.current]}
              opts={{
                align: "center",
                loop: true,
              }}
              onMouseEnter={plugin.current.stop}
              onMouseLeave={plugin.current.reset}
              className="w-full"
            >
              <CarouselContent>
                {stocks.map((stock) => (
                  <CarouselItem key={stock.symbol}>
                    <div className="p-1">
                      <AIScoreCard 
                        stock={stock} 
                        onAnalysisGenerated={fetchData}
                      />
                    </div>
                  </CarouselItem>
                ))}
              </CarouselContent>
              
              {/* Botões Externos - Bem Fora */}
              <CarouselPrevious className="absolute -left-16 top-1/2 -translate-y-1/2 h-12 w-12 bg-zinc-800 border-2 border-zinc-700 text-white hover:bg-emerald-500 hover:border-emerald-500 hover:scale-110 transition-all shadow-xl" />
              <CarouselNext className="absolute -right-16 top-1/2 -translate-y-1/2 h-12 w-12 bg-zinc-800 border-2 border-zinc-700 text-white hover:bg-emerald-500 hover:border-emerald-500 hover:scale-110 transition-all shadow-xl" />
            </Carousel>

            {/* Indicadores (Dots) - Verde */}
            <div className="flex items-center justify-center gap-2 mt-4">
              {stocks.map((_, index) => (
                <button
                  key={index}
                  onClick={() => carouselApi?.scrollTo(index)}
                  className={`transition-all rounded-full ${
                    index === currentSlide
                      ? 'w-8 h-2 bg-emerald-500 shadow-lg shadow-emerald-500/50'
                      : 'w-2 h-2 bg-zinc-700 hover:bg-emerald-400 hover:scale-125'
                  }`}
                  aria-label={`Ir para slide ${index + 1}`}
                />
              ))}
            </div>
          </div>

          {/* News Section - Carousel Vertical Moderno */}
          <div className="relative bg-zinc-900/70 backdrop-blur-xl border border-zinc-800/50 rounded-2xl overflow-hidden shadow-2xl">
          {/* Badge Flutuante */}
          <div className="absolute top-4 left-4 z-10 flex items-center gap-2 px-3 py-1.5 bg-emerald-500/20 backdrop-blur-xl border border-emerald-500/30 rounded-full shadow-lg shadow-emerald-500/20">
            <Newspaper className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-xs font-semibold text-emerald-400">Últimas Notícias</span>
            <div className="w-1 h-1 bg-emerald-400 rounded-full animate-pulse ml-1"></div>
          </div>
          
          <div className="p-5 pt-14">
            {newsLoading ? (
              <div className="h-[140px] flex items-center justify-center">
                <div className="text-center">
                  <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                  <p className="text-xs text-zinc-500">Carregando notícias...</p>
                </div>
              </div>
            ) : news.length > 0 ? (
              <Carousel
                plugins={[newsPlugin.current]}
                opts={{
                  align: "start",
                  loop: true,
                }}
                orientation="vertical"
                onMouseEnter={newsPlugin.current.stop}
                onMouseLeave={newsPlugin.current.reset}
                className="w-full"
              >
                <CarouselContent className="h-[140px]">
                {news.slice(0, 5).map((item, index) => (
                  <CarouselItem key={index} className="h-[140px]">
                    <div className="relative bg-zinc-800/30 backdrop-blur-sm border border-zinc-700/50 rounded-xl hover:bg-zinc-800/50 hover:border-emerald-500/30 transition-all duration-300 h-full overflow-hidden group">
                      {/* Glow Effect */}
                      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/0 to-emerald-500/0 group-hover:from-emerald-500/5 group-hover:to-transparent transition-all duration-500"></div>
                      
                      <div className="relative p-3 h-full flex flex-col justify-between">
                        <div className="flex items-start gap-3">
                          <div className="flex-shrink-0 w-9 h-9 bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 rounded-lg flex items-center justify-center border border-emerald-500/20">
                            <Newspaper className="w-4 h-4 text-emerald-400" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-white mb-1.5 line-clamp-2 leading-tight text-sm">
                              {item.title}
                            </h3>
                            <span className="inline-block px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded-full text-[10px] font-medium">
                              {item.author}
                            </span>
                          </div>
                        </div>
                        
                        {/* Botão Ver Notícia */}
                        <a
                          href={item.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="w-full px-4 py-1.5 bg-gradient-to-r from-emerald-600/20 to-emerald-500/20 backdrop-blur-xl border border-emerald-500/30 text-white rounded-lg hover:from-emerald-600 hover:to-emerald-500 hover:border-emerald-500 hover:shadow-lg hover:shadow-emerald-500/20 transition-all duration-300 flex items-center justify-center gap-2 text-xs font-medium"
                        >
                          Ver Notícia Completa
                          <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform" />
                        </a>
                      </div>
                    </div>
                  </CarouselItem>
                ))}
              </CarouselContent>
              </Carousel>
            ) : (
              <div className="text-center py-12 text-zinc-500 h-[140px] flex flex-col items-center justify-center">
                <Newspaper size={48} className="mx-auto mb-4 opacity-30" />
                <p className="text-sm">Nenhuma notícia disponível no momento</p>
              </div>
            )}
          </div>
          </div>
        </div>
      </div>

      {/* Chat Assistant */}
      <ChatWidget />
    </div>
  )
}

