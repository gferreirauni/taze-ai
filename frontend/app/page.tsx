'use client'

import { useEffect, useState } from 'react'
import { Newspaper, Sparkles, TrendingUp } from 'lucide-react'
import Sidebar from '@/components/dashboard/Sidebar'
import ChatWidget from '@/components/dashboard/ChatWidget'
import AIScoreCard from '@/components/dashboard/AIScoreCard'

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

  useEffect(() => {
    async function fetchData() {
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
    <div className="flex min-h-screen bg-zinc-950">
      <Sidebar />

      <div className="ml-64 flex-1 p-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="w-8 h-8 text-purple-500" />
            <h1 className="text-4xl font-bold text-white">Painel de Decisão Taze AI</h1>
          </div>
          <p className="text-zinc-400 text-lg">
            Análises de IA para os principais ativos da B3, atualizadas diariamente
          </p>
          <p className="text-zinc-600 text-sm mt-1">
            Scores inteligentes para Buy & Hold e Swing Trade
          </p>
        </div>

        {/* AI Score Cards Grid */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-500" />
              Análises Inteligentes
            </h2>
            <span className="text-xs text-zinc-500">
              {stocks.filter(s => s.ai_analysis).length} de {stocks.length} com análise de IA
            </span>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {stocks.map((stock) => (
              <AIScoreCard key={stock.symbol} stock={stock} />
            ))}
          </div>
        </div>

        {/* News Section */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Newspaper className="w-5 h-5 text-blue-500" />
            Últimas Notícias Relevantes
            <span className="text-xs text-zinc-500 font-normal ml-auto">via Análise de Ações</span>
          </h2>
          
          {newsLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex gap-4 p-4 bg-zinc-800/50 rounded-lg border border-zinc-700">
                  <div className="flex-shrink-0 w-16 h-16 bg-zinc-700 rounded-lg animate-pulse"></div>
                  <div className="flex-1 space-y-2">
                    <div className="h-5 bg-zinc-700 rounded animate-pulse w-3/4"></div>
                    <div className="h-4 bg-zinc-700 rounded animate-pulse w-full"></div>
                    <div className="h-3 bg-zinc-700 rounded animate-pulse w-1/2"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : news.length > 0 ? (
            <div className="space-y-4">
              {news.map((item, index) => (
                <a
                  key={index}
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex gap-4 p-4 bg-zinc-800/50 rounded-lg border border-zinc-700 hover:bg-zinc-800 hover:border-blue-500/50 transition-all cursor-pointer group"
                >
                  <div className="flex-shrink-0 w-16 h-16 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform">
                    <Newspaper className="w-8 h-8 text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-white mb-1 group-hover:text-blue-400 transition-colors line-clamp-2">
                      {item.title}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-zinc-500">
                      <span>📰 {item.author}</span>
                      <span>•</span>
                      <span>{item.time_ago}</span>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-zinc-500">
              <Newspaper size={48} className="mx-auto mb-4 opacity-50" />
              <p>Nenhuma notícia disponível no momento</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-zinc-600">
          <p>Análises atualizadas diariamente • Dados em tempo real via Tradebox API</p>
        </div>
      </div>

      {/* Chat Assistant */}
      <ChatWidget />
    </div>
  )
}

