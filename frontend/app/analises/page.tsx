'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Search, TrendingUp, Newspaper, BarChart3 } from 'lucide-react'
import Sidebar from '@/components/dashboard/Sidebar'
import StockChart from '@/components/dashboard/StockChart'
import AIInsights from '@/components/dashboard/AIInsights'

interface Stock {
  symbol: string
  name: string
  sector: string
  currentPrice: number
  dailyVariation: number
  monthVariation: number
  history: { date: string; value: number }[]
  fundamentals?: any
}

export default function AnalisesPage() {
  const searchParams = useSearchParams()
  const tickerFromUrl = searchParams.get('ticker')
  
  const [stocks, setStocks] = useState<Stock[]>([])
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    async function fetchStocks() {
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        const response = await fetch('http://localhost:8000/api/stocks')
        
        if (!response.ok) {
          throw new Error(`Erro: ${response.status}`)
        }
        
        const data = await response.json()
        setStocks(data.stocks)
        
        // Se há ticker na URL, selecionar automaticamente
        if (tickerFromUrl && data.stocks) {
          const stock = data.stocks.find((s: Stock) => s.symbol === tickerFromUrl.toUpperCase())
          if (stock) {
            setSelectedStock(stock)
            console.log(`[ANÁLISES] Ticker da URL: ${tickerFromUrl} - Ação selecionada automaticamente`)
          }
        }
      } catch (error) {
        console.error('Erro ao buscar ações:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStocks()
  }, [tickerFromUrl])

  const filteredStocks = stocks.filter(stock =>
    stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    stock.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-950">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-zinc-400">Carregando análises...</p>
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
          <h1 className="text-3xl font-bold text-white mb-2">Análises</h1>
          <p className="text-zinc-500">Selecione um ativo para analisar ou ver notícias</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Lista de Ações */}
          <div className="lg:col-span-1">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-500" />
                Selecionar Ativo
              </h2>

              {/* Search */}
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <input
                  type="text"
                  placeholder="Buscar ação..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              {/* Stock List */}
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {filteredStocks.map((stock) => {
                  const isSelected = selectedStock?.symbol === stock.symbol
                  const isPositive = stock.dailyVariation >= 0

                  return (
                    <button
                      key={stock.symbol}
                      onClick={() => setSelectedStock(stock)}
                      className={`w-full text-left p-4 rounded-lg transition-all ${
                        isSelected
                          ? 'bg-purple-500/20 border-2 border-purple-500'
                          : 'bg-zinc-800/50 border border-zinc-700 hover:bg-zinc-800'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <div>
                          <p className="font-semibold text-white">{stock.symbol}</p>
                          <p className="text-xs text-zinc-500">{stock.name}</p>
                        </div>
                        <span className={`text-sm font-semibold ${isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
                          {isPositive ? '+' : ''}{stock.dailyVariation.toFixed(2)}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-zinc-500">{stock.sector}</span>
                        <span className="text-white font-medium">R$ {stock.currentPrice.toFixed(2)}</span>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Análise e Gráfico */}
          <div className="lg:col-span-2 space-y-6">
            {selectedStock ? (
              <>
                {/* Gráfico */}
                <StockChart
                  data={selectedStock.history}
                  stockName={selectedStock.name}
                  stockSymbol={selectedStock.symbol}
                  currentPrice={selectedStock.currentPrice}
                  monthVariation={selectedStock.monthVariation}
                />

                {/* Análise de IA */}
                <AIInsights stock={selectedStock} />

                {/* Notícias (placeholder) */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
                  <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <Newspaper className="w-5 h-5 text-blue-500" />
                    Últimas Notícias - {selectedStock.symbol}
                  </h2>
                  <div className="space-y-4">
                    <div className="p-4 bg-zinc-800/50 rounded-lg border border-zinc-700">
                      <p className="text-sm text-zinc-400 mb-2">📰 Funcionalidade em breve</p>
                      <p className="text-zinc-500 text-sm">
                        Em breve você poderá ver as últimas notícias sobre {selectedStock.name} diretamente aqui!
                      </p>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-12 text-center">
                <TrendingUp className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">Selecione um Ativo</h3>
                <p className="text-zinc-500">
                  Escolha uma ação na lista ao lado para visualizar análises detalhadas, gráficos e notícias.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

