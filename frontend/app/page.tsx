'use client'

import { useEffect, useState } from 'react'
import { Wallet, TrendingUp, Activity } from 'lucide-react'
import Sidebar from '@/components/dashboard/Sidebar'
import SummaryCard from '@/components/dashboard/SummaryCard'
import StockList from '@/components/dashboard/StockList'
import StockChart from '@/components/dashboard/StockChart'
import AIInsights from '@/components/dashboard/AIInsights'

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

export default function Dashboard() {
  const [stocks, setStocks] = useState<Stock[]>([])
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null)
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        // Buscar ações
        const stocksResponse = await fetch('http://localhost:8000/api/stocks')
        const stocksData = await stocksResponse.json()
        setStocks(stocksData.stocks)
        
        // Selecionar primeira ação por padrão
        if (stocksData.stocks.length > 0) {
          setSelectedStock(stocksData.stocks[0])
        }

        // Buscar resumo da carteira
        const portfolioResponse = await fetch('http://localhost:8000/api/portfolio/summary')
        const portfolioData = await portfolioResponse.json()
        setPortfolio(portfolioData)
      } catch (error) {
        console.error('Erro ao buscar dados:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    
    // Atualizar dados a cada 30 segundos
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
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
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
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
            change="5 empresas"
            changeType="neutral"
            icon={Activity}
          />
        </div>

        {/* Chart and AI Analysis */}
        {selectedStock && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2">
              <StockChart
                data={selectedStock.history}
                stockName={selectedStock.name}
                stockSymbol={selectedStock.symbol}
              />
            </div>
            <div className="lg:col-span-1">
              <AIInsights stock={selectedStock} />
            </div>
          </div>
        )}

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
    </div>
  )
}
