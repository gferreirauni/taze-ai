'use client'

import { useEffect, useState } from 'react'
import { Activity, Newspaper, TrendingUp, Wallet } from 'lucide-react'
import Sidebar from '@/components/dashboard/Sidebar'
import SummaryCard from '@/components/dashboard/SummaryCard'
import StockList from '@/components/dashboard/StockList'
import ChatWidget from '@/components/dashboard/ChatWidget'

interface Stock {
  symbol: string
  name: string
  sector: string
  currentPrice: number
  dailyVariation: number
  history: { date: string; value: number }[]
}

interface PortfolioSummary {
  totalValue: number
  dailyChange: number
  dailyChangeValue: number
  stocksCount: number
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
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null)
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null)
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
        setStocks(stocksData.stocks)

        const portfolioResponse = await fetch('http://localhost:8000/api/portfolio/summary')
        const portfolioData = await portfolioResponse.json()
        setPortfolio(portfolioData)
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
          setNews(newsData.news.slice(0, 5))  // Mostrar apenas 5 notícias
        }
      } catch (error) {
        console.error('Erro ao buscar notícias:', error)
      } finally {
        setNewsLoading(false)
      }
    }

    fetchData()
    fetchNews()
    
    const stocksInterval = setInterval(fetchData, 30000)
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
          <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-zinc-500">Bem-vindo ao seu painel de investimentos</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <SummaryCard
            title="Patrimônio Total"
            value={portfolio ? `R$ ${portfolio.totalValue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : 'R$ 0,00'}
            change={portfolio ? `${portfolio.dailyChange >= 0 ? '+' : ''}${portfolio.dailyChange.toFixed(2)}%` : undefined}
            changeType={portfolio && portfolio.dailyChange >= 0 ? 'positive' : 'negative'}
            icon={Wallet}
          />
          <SummaryCard
            title="Rentabilidade Hoje"
            value={portfolio ? `R$ ${portfolio.dailyChangeValue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : 'R$ 0,00'}
            change={portfolio ? `${portfolio.dailyChange >= 0 ? '+' : ''}${portfolio.dailyChange.toFixed(2)}%` : undefined}
            changeType={portfolio && portfolio.dailyChange >= 0 ? 'positive' : 'negative'}
            icon={TrendingUp}
          />
          <SummaryCard
            title="Ações Monitoradas"
            value={stocks.length.toString()}
            change="5 empresas da B3"
            changeType="neutral"
            icon={Activity}
          />
        </div>

        {/* Portfolio Chart */}
        {portfolio && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-500" />
              Evolução do Patrimônio (30 dias)
            </h2>
            <div className="h-64 flex items-center justify-center text-zinc-500">
              <div className="text-center">
                <TrendingUp size={48} className="mx-auto mb-4 opacity-50" />
                <p>Gráfico de evolução será implementado em breve</p>
                <p className="text-sm mt-2">Conecte sua corretora para visualizar histórico</p>
              </div>
            </div>
          </div>
        )}

        {/* News Section */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Newspaper className="w-5 h-5 text-blue-500" />
            Últimas Notícias Relevantes
            <span className="text-xs text-zinc-500 font-normal ml-auto">via Investing.com</span>
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

              <div className="text-center mt-4">
                <a
                  href="https://br.investing.com/analysis/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700 transition-colors text-sm font-medium"
                >
                  <Newspaper size={16} />
                  Ver todas as notícias no Investing.com
                </a>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-zinc-500">
              <Newspaper size={48} className="mx-auto mb-4 opacity-50" />
              <p>Nenhuma notícia disponível no momento</p>
            </div>
          )}
        </div>

        {/* Stock List */}
        <StockList
          stocks={stocks}
          onSelectStock={setSelectedStock}
          selectedStock={selectedStock || undefined}
        />

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-zinc-600">
          <p>Dados atualizados automaticamente • Última atualização: {new Date().toLocaleTimeString('pt-BR')}</p>
        </div>
      </div>

      {/* Chat Assistant */}
      <ChatWidget selectedStock={selectedStock || undefined} />
    </div>
  )
}
