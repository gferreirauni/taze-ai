'use client'

import { useState, useEffect } from 'react'
import { Bot, TrendingUp, TrendingDown, Sparkles, RefreshCw, Landmark, Zap } from 'lucide-react'

interface Stock {
  symbol: string
  name: string
  currentPrice: number
  dailyVariation: number
  history: { date: string; value: number }[]
  fundamentals?: any
}

interface AIAnalysisResponse {
  symbol: string
  buyAndHoldScore: number
  buyAndHoldSummary: string
  swingTradeScore: number
  swingTradeSummary: string
  dayTradeScore: number
  dayTradeSummary: string
  recommendation: string
  generatedAt: string
}

interface AIInsightsProps {
  stock: Stock
}

export default function AIInsights({ stock }: AIInsightsProps) {
  const [analysis, setAnalysis] = useState<AIAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [cached, setCached] = useState(false)

  // Buscar análise em cache ao carregar
  useEffect(() => {
    if (stock) {
      checkCachedAnalysis()
    }
  }, [stock.symbol])

  const checkCachedAnalysis = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/ai/analysis/${stock.symbol}`)
      const data = await response.json()
      
      if (data.cached && data.analysis) {
        setAnalysis(data.analysis)
        setCached(true)
      } else {
        setAnalysis(null)
        setCached(false)
      }
    } catch (error) {
      console.error('Erro ao buscar análise em cache:', error)
      setAnalysis(null)
      setCached(false)
    }
  }

  const generateAnalysis = async () => {
    setLoading(true)
    setCached(false)
    
    try {
      const response = await fetch('http://localhost:8000/api/ai/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: stock.symbol,
          currentPrice: stock.currentPrice,
          dailyVariation: stock.dailyVariation,
          history: stock.history,
          fundamentals: stock.fundamentals || {}
        }),
      })

      const data = await response.json()
      setAnalysis(data)
      setCached(true)
    } catch (error) {
      console.error('Erro ao gerar análise:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRecommendationColor = (rec: string) => {
    if (rec === 'COMPRA FORTE') return 'bg-emerald-500 text-white'
    if (rec === 'COMPRA') return 'bg-emerald-600 text-white'
    if (rec === 'MANTER') return 'bg-blue-500 text-white'
    if (rec === 'VENDA') return 'bg-orange-600 text-white'
    if (rec === 'VENDA FORTE') return 'bg-red-500 text-white'
    return 'bg-zinc-700 text-white'
  }

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-emerald-400 border-emerald-500'
    if (score >= 6) return 'text-blue-400 border-blue-500'
    if (score >= 4) return 'text-orange-400 border-orange-500'
    return 'text-red-400 border-red-500'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 8) return 'Excelente'
    if (score >= 6) return 'Bom'
    if (score >= 4) return 'Razoável'
    return 'Fraco'
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-purple-500" />
          <h2 className="text-xl font-bold text-white">Análise de IA</h2>
        </div>
        <span className="text-xs text-zinc-500">Powered by GPT-4o</span>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center p-8">
          <Bot size={48} className="text-purple-400 animate-pulse mb-4" />
          <p className="text-lg font-semibold text-zinc-300 mb-2">
            Analisando {stock.symbol} com IA...
          </p>
          <p className="text-sm text-zinc-500 mb-4">
            Processando dados técnicos e fundamentalistas...
          </p>
          <div className="w-full max-w-md space-y-2">
            <div className="h-3 bg-zinc-800 rounded animate-pulse" />
            <div className="h-3 bg-zinc-800 rounded animate-pulse w-5/6" />
            <div className="h-3 bg-zinc-800 rounded animate-pulse w-4/5" />
          </div>
        </div>
      )}

      {/* No Analysis State */}
      {!loading && !analysis && (
        <div className="flex flex-col items-center justify-center p-8 text-center">
          <Sparkles size={48} className="text-zinc-700 mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">Gerar Análise Profissional</h3>
          <p className="text-zinc-500 mb-6 text-sm max-w-md">
            Análise com IA utilizando dados técnicos e fundamentalistas.
            Receba scores para Buy & Hold e Swing Trade.
          </p>
          <button
            onClick={generateAnalysis}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:scale-105 transition-transform duration-200 flex items-center gap-2 shadow-lg shadow-purple-500/20"
          >
            <Sparkles size={18} />
            Gerar Análise
          </button>
          <p className="text-xs text-zinc-600 mt-4">
            💡 Cache de 24h para economizar tokens
          </p>
        </div>
      )}

      {/* Analysis Display */}
      {!loading && analysis && (
        <>
          {/* Cache Indicator */}
          {cached && (
            <div className="flex items-center gap-2 mb-4 text-xs text-emerald-500">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
              Análise do dia em cache (economizando tokens)
            </div>
          )}

          {/* Recommendation Badge */}
          <div className="flex justify-center mb-6">
            <div className={`px-6 py-3 rounded-xl font-bold text-lg shadow-lg ${getRecommendationColor(analysis.recommendation)}`}>
              {analysis.recommendation}
            </div>
          </div>

          {/* Score Cards - 3 Tipos de Análise */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {/* Buy & Hold Score */}
            <div className="bg-zinc-800/50 border border-zinc-700 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Landmark className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-bold text-white">Buy & Hold</h3>
              </div>
              
              <div className="flex items-end gap-2 mb-3">
                <div className={`text-4xl font-bold ${getScoreColor(analysis.buyAndHoldScore)}`}>
                  {analysis.buyAndHoldScore.toFixed(1)}
                </div>
                <div className="text-xs text-zinc-500 mb-1">/ 10</div>
              </div>

              <div className={`inline-block px-2 py-1 rounded-full text-xs font-semibold mb-3 ${getScoreColor(analysis.buyAndHoldScore)} bg-opacity-10`}>
                {getScoreLabel(analysis.buyAndHoldScore)}
              </div>

              <p className="text-xs text-zinc-400 leading-relaxed">
                {analysis.buyAndHoldSummary}
              </p>
            </div>

            {/* Swing Trade Score */}
            <div className="bg-zinc-800/50 border border-zinc-700 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp className="w-5 h-5 text-blue-400" />
                <h3 className="text-base font-bold text-white">Swing Trade</h3>
              </div>
              
              <div className="flex items-end gap-2 mb-3">
                <div className={`text-4xl font-bold ${getScoreColor(analysis.swingTradeScore)}`}>
                  {analysis.swingTradeScore.toFixed(1)}
                </div>
                <div className="text-xs text-zinc-500 mb-1">/ 10</div>
              </div>

              <div className={`inline-block px-2 py-1 rounded-full text-xs font-semibold mb-3 ${getScoreColor(analysis.swingTradeScore)} bg-opacity-10`}>
                {getScoreLabel(analysis.swingTradeScore)}
              </div>

              <p className="text-xs text-zinc-400 leading-relaxed">
                {analysis.swingTradeSummary}
              </p>
            </div>

            {/* Day Trade Score */}
            <div className="bg-zinc-800/50 border border-zinc-700 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-bold text-white">Day Trade</h3>
              </div>
              
              <div className="flex items-end gap-2 mb-3">
                <div className={`text-4xl font-bold ${getScoreColor(analysis.dayTradeScore)}`}>
                  {analysis.dayTradeScore.toFixed(1)}
                </div>
                <div className="text-xs text-zinc-500 mb-1">/ 10</div>
              </div>

              <div className={`inline-block px-2 py-1 rounded-full text-xs font-semibold mb-3 ${getScoreColor(analysis.dayTradeScore)} bg-opacity-10`}>
                {getScoreLabel(analysis.dayTradeScore)}
              </div>

              <p className="text-xs text-zinc-400 leading-relaxed">
                {analysis.dayTradeSummary}
              </p>
            </div>
          </div>

          {/* Score Legend */}
          <div className="bg-zinc-800/30 border border-zinc-700 rounded-lg p-4 mb-4">
            <p className="text-xs font-semibold text-zinc-400 mb-2">Legenda de Scores:</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
                <span className="text-zinc-500">8-10: Excelente</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-400"></div>
                <span className="text-zinc-500">6-7: Bom</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-orange-400"></div>
                <span className="text-zinc-500">4-5: Razoável</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <span className="text-zinc-500">0-3: Fraco</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={generateAnalysis}
              disabled={loading}
              className="flex-1 px-4 py-2.5 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700 transition-colors flex items-center justify-center gap-2 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed border border-zinc-700"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              Atualizar Análise
            </button>
          </div>

          {/* Disclaimer */}
          <div className="mt-4 p-3 bg-orange-500/10 border border-orange-500/20 rounded-lg">
            <p className="text-xs text-orange-400">
              ⚠️ Análise automatizada para fins educacionais. Não é recomendação de investimento.
            </p>
          </div>

          {/* Generated At */}
          <p className="text-xs text-zinc-600 mt-3 text-center">
            Gerada em: {new Date(analysis.generatedAt).toLocaleString('pt-BR')}
          </p>
        </>
      )}
    </div>
  )
}
