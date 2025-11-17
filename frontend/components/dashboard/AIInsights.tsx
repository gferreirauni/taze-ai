'use client'

import { useState, useEffect } from 'react'
import { Bot, TrendingUp, TrendingDown, Minus, FileText, Sparkles, RefreshCw } from 'lucide-react'

interface Stock {
  symbol: string
  name: string
  currentPrice: number
  dailyVariation: number
  history: { date: string; value: number }[]
  fundamentals?: any  // Dados fundamentalistas da API Tradebox
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
    
    // Simular delay para UX
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
          history: stock.history,
          fundamentals: stock.fundamentals  // Incluir dados fundamentalistas
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
    if (rec.includes('COMPRA')) return 'text-emerald-500 bg-emerald-500/10'
    if (rec.includes('VENDA')) return 'text-red-500 bg-red-500/10'
    if (rec.includes('ATENÇÃO')) return 'text-orange-500 bg-orange-500/10'
    return 'text-blue-500 bg-blue-500/10'
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-purple-500" />
          <h2 className="text-xl font-bold text-white">Análise de IA</h2>
        </div>
        <span className="text-xs text-zinc-500">Powered by Taze AI Engine</span>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center h-full p-6">
          <Bot size={48} className="text-purple-400 animate-pulse" />
          <p className="mt-4 text-lg font-semibold text-zinc-300">
            Analisando {stock.symbol} com IA...
          </p>
          <div className="mt-4 w-full space-y-2">
            <div className="h-4 bg-zinc-800 rounded animate-pulse" />
            <div className="h-4 bg-zinc-800 rounded animate-pulse w-5/6" />
            <div className="h-4 bg-zinc-800 rounded animate-pulse w-4/5" />
            <div className="h-4 bg-zinc-800 rounded animate-pulse w-11/12" />
            <div className="h-4 bg-zinc-800 rounded animate-pulse w-3/4" />
          </div>
        </div>
      )}

      {/* No Analysis State */}
      {!loading && !analysis && (
        <div className="flex flex-col items-center justify-center h-full p-8 text-center">
          <Sparkles size={48} className="text-zinc-700 mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">Gerar Análise de IA</h3>
          <p className="text-zinc-500 mb-6 text-sm">
            Clique no botão abaixo para gerar uma análise detalhada de {stock.symbol} com IA.
          </p>
          <button
            onClick={generateAnalysis}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:scale-105 transition-transform duration-200 flex items-center gap-2"
          >
            <Sparkles size={18} />
            Gerar Análise
          </button>
          <p className="text-xs text-zinc-600 mt-4">
            💡 A análise é salva por 24h para economizar tokens
          </p>
        </div>
      )}

      {/* Analysis Display */}
      {!loading && analysis && (
        <>
          {/* Recommendation Badge */}
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg mb-4 ${getRecommendationColor(analysis.recommendation)}`}>
            {analysis.recommendation.includes('COMPRA') && <TrendingUp size={18} />}
            {analysis.recommendation.includes('VENDA') && <TrendingDown size={18} />}
            {analysis.recommendation.includes('MANTER') && <Minus size={18} />}
            <span className="font-bold text-sm">{analysis.recommendation}</span>
            <span className="text-xs opacity-70">• {analysis.confidence}% confiança</span>
          </div>

          {cached && (
            <div className="flex items-center gap-2 mb-4 text-xs text-emerald-500">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
              Análise do dia em cache (economizando tokens)
            </div>
          )}

          {/* Analysis Text */}
          <div className="prose prose-invert max-w-none mb-4">
            <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
              {analysis.analysis}
            </div>
          </div>

          {/* Sector Context */}
          <div className="bg-zinc-800/50 rounded-lg p-4 mb-4 border border-zinc-700">
            <p className="text-xs font-semibold text-emerald-500 mb-1">Contexto do Setor:</p>
            <p className="text-sm text-zinc-400">{analysis.sectorInsight}</p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={generateAnalysis}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700 transition-colors flex items-center justify-center gap-2 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              Atualizar Análise
            </button>
            <button
              className="flex-1 px-4 py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700 transition-colors flex items-center justify-center gap-2 text-sm font-medium"
            >
              <FileText size={16} />
              Relatório Completo
            </button>
          </div>

          {/* Disclaimer */}
          <div className="mt-4 p-3 bg-orange-500/10 border border-orange-500/20 rounded-lg">
            <p className="text-xs text-orange-400">
              ⚠️ {analysis.disclaimer}
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
