'use client'

import { useState, useEffect } from 'react'
import { Bot, TrendingUp, TrendingDown, Minus, FileText, Sparkles } from 'lucide-react'

interface Stock {
  symbol: string
  name: string
  currentPrice: number
  dailyVariation: number
  history: { date: string; value: number }[]
}

interface AIAnalysis {
  symbol: string
  recommendation: string
  sentiment: 'bullish' | 'bearish' | 'neutral'
  confidence: number
  analysis: string
  sectorInsight: string
  generatedAt: string
  disclaimer: string
}

interface AIInsightsProps {
  stock: Stock
}

export default function AIInsights({ stock }: AIInsightsProps) {
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (stock) {
      analyzeStock()
    }
  }, [stock.symbol])

  const analyzeStock = async () => {
    setLoading(true)
    
    // Simular delay de 1.5s para parecer que está processando
    await new Promise(resolve => setTimeout(resolve, 1500))
    
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
          history: stock.history
        })
      })
      
      const data = await response.json()
      setAnalysis(data)
    } catch (error) {
      console.error('Erro ao analisar ação:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRecommendationColor = (recommendation: string) => {
    if (recommendation.includes('COMPRA')) return 'text-emerald-500 bg-emerald-500/10'
    if (recommendation.includes('VENDA')) return 'text-red-500 bg-red-500/10'
    if (recommendation.includes('ATENÇÃO')) return 'text-orange-500 bg-orange-500/10'
    return 'text-blue-500 bg-blue-500/10'
  }

  const getSentimentIcon = (sentiment: string) => {
    if (sentiment === 'bullish') return <TrendingUp className="w-5 h-5 text-emerald-500" />
    if (sentiment === 'bearish') return <TrendingDown className="w-5 h-5 text-red-500" />
    return <Minus className="w-5 h-5 text-zinc-400" />
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Análise de IA</h2>
            <p className="text-sm text-zinc-500">Powered by Taze AI Engine</p>
          </div>
        </div>
        {analysis && (
          <div className="flex items-center gap-2">
            {getSentimentIcon(analysis.sentiment)}
            <span className="text-sm text-zinc-400">
              Confiança: {analysis.confidence}%
            </span>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="space-y-4">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-5 h-5 text-purple-500 animate-pulse" />
            <span className="text-sm text-purple-400 font-medium">
              Analisando {stock.symbol} com IA...
            </span>
          </div>
          
          {/* Skeleton Loader */}
          <div className="space-y-3">
            <div className="h-4 bg-zinc-800 rounded animate-pulse"></div>
            <div className="h-4 bg-zinc-800 rounded w-5/6 animate-pulse"></div>
            <div className="h-4 bg-zinc-800 rounded w-4/6 animate-pulse"></div>
            <div className="h-32 bg-zinc-800 rounded animate-pulse mt-4"></div>
            <div className="h-4 bg-zinc-800 rounded w-3/6 animate-pulse"></div>
          </div>
        </div>
      )}

      {/* Analysis Content */}
      {!loading && analysis && (
        <div className="space-y-4">
          {/* Recommendation Badge */}
          <div className="flex items-center gap-3">
            <span className={`px-4 py-2 rounded-lg font-bold text-sm ${getRecommendationColor(analysis.recommendation)}`}>
              {analysis.recommendation}
            </span>
            <span className="text-xs text-zinc-500">
              Gerado em {new Date(analysis.generatedAt).toLocaleTimeString('pt-BR')}
            </span>
          </div>

          {/* Analysis Text */}
          <div className="prose prose-invert prose-sm max-w-none">
            <div className="text-zinc-300 leading-relaxed whitespace-pre-line text-sm">
              {analysis.analysis}
            </div>
          </div>

          {/* Sector Insight */}
          <div className="mt-4 p-4 bg-zinc-800/50 rounded-lg border border-zinc-700">
            <p className="text-sm text-zinc-400">
              <span className="font-semibold text-emerald-400">Contexto do Setor:</span> {analysis.sectorInsight}
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 mt-6">
            <button
              onClick={analyzeStock}
              className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              Atualizar Análise
            </button>
            <button
              className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
              title="Em breve"
            >
              <FileText className="w-4 h-4" />
              Relatório Completo
            </button>
          </div>

          {/* Disclaimer */}
          <div className="mt-4 p-3 bg-zinc-950 rounded-lg border border-zinc-800">
            <p className="text-xs text-zinc-500 leading-relaxed">
              ⚠️ {analysis.disclaimer}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

