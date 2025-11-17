'use client'

import { TrendingUp, TrendingDown, ArrowRight, Target, Activity } from 'lucide-react'
import Link from 'next/link'

interface Stock {
  symbol: string
  name: string
  sector: string
  currentPrice: number
  dailyVariation: number
  monthVariation: number
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

interface AIScoreCardProps {
  stock: Stock
}

export default function AIScoreCard({ stock }: AIScoreCardProps) {
  const isPositive = stock.dailyVariation >= 0

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-emerald-400'
    if (score >= 6) return 'text-blue-400'
    if (score >= 4) return 'text-orange-400'
    return 'text-red-400'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 8) return 'Excelente'
    if (score >= 6) return 'Bom'
    if (score >= 4) return 'Razoável'
    return 'Fraco'
  }

  const getRecommendationColor = (rec: string) => {
    if (rec === 'COMPRA FORTE') return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
    if (rec === 'COMPRA') return 'bg-emerald-600/20 text-emerald-400 border-emerald-600/30'
    if (rec === 'MANTER') return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    if (rec === 'VENDA') return 'bg-orange-600/20 text-orange-400 border-orange-600/30'
    if (rec === 'VENDA FORTE') return 'bg-red-500/20 text-red-400 border-red-500/30'
    return 'bg-zinc-700/20 text-zinc-400 border-zinc-700/30'
  }

  // Se não há análise, mostrar card de "Gerar Análise"
  if (!stock.ai_analysis) {
    return (
      <Link href={`/analises?ticker=${stock.symbol}`}>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:border-purple-500/50 transition-all cursor-pointer group">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-white group-hover:text-purple-400 transition-colors">
                {stock.symbol}
              </h3>
              <p className="text-xs text-zinc-500 truncate">{stock.name}</p>
            </div>
            <div className="text-right">
              <p className="text-xl font-bold text-white">
                R$ {stock.currentPrice.toFixed(2)}
              </p>
              <p className={`text-sm font-semibold ${isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
                {isPositive ? '+' : ''}{stock.dailyVariation.toFixed(2)}%
              </p>
            </div>
          </div>

          {/* Call to Action */}
          <div className="flex flex-col items-center justify-center py-8 border border-dashed border-zinc-700 rounded-lg group-hover:border-purple-500/50 transition-all">
            <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center mb-3 group-hover:bg-purple-500/20 transition-all">
              <Activity className="w-6 h-6 text-purple-400" />
            </div>
            <p className="text-sm text-zinc-400 group-hover:text-purple-400 transition-colors">
              Clique para gerar análise de IA
            </p>
          </div>
        </div>
      </Link>
    )
  }

  // Card com análise
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:border-zinc-700 transition-all">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-white">{stock.symbol}</h3>
          <p className="text-xs text-zinc-500 truncate max-w-[200px]">{stock.name}</p>
          <p className="text-xs text-zinc-600 mt-0.5">{stock.sector}</p>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold text-white">
            R$ {stock.currentPrice.toFixed(2)}
          </p>
          <p className={`text-sm font-semibold ${isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
            {isPositive ? '+' : ''}{stock.dailyVariation.toFixed(2)}%
          </p>
        </div>
      </div>

      {/* Recommendation Badge */}
      <div className="mb-4">
        <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold ${getRecommendationColor(stock.ai_analysis.recommendation)}`}>
          {stock.ai_analysis.recommendation.includes('COMPRA') && <TrendingUp size={14} />}
          {stock.ai_analysis.recommendation.includes('VENDA') && <TrendingDown size={14} />}
          {stock.ai_analysis.recommendation}
        </div>
      </div>

      {/* Scores Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Buy & Hold Score */}
        <div className="bg-zinc-800/50 border border-zinc-700 rounded-lg p-4">
          <div className="flex items-center gap-1.5 mb-2">
            <Target className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-semibold text-zinc-400">Buy & Hold</span>
          </div>
          <div className="flex items-baseline gap-1 mb-1">
            <span className={`text-3xl font-bold ${getScoreColor(stock.ai_analysis.buyAndHoldScore)}`}>
              {stock.ai_analysis.buyAndHoldScore.toFixed(1)}
            </span>
            <span className="text-sm text-zinc-500">/ 10</span>
          </div>
          <span className={`text-xs font-medium ${getScoreColor(stock.ai_analysis.buyAndHoldScore)}`}>
            {getScoreLabel(stock.ai_analysis.buyAndHoldScore)}
          </span>
        </div>

        {/* Swing Trade Score */}
        <div className="bg-zinc-800/50 border border-zinc-700 rounded-lg p-4">
          <div className="flex items-center gap-1.5 mb-2">
            <Activity className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-semibold text-zinc-400">Swing Trade</span>
          </div>
          <div className="flex items-baseline gap-1 mb-1">
            <span className={`text-3xl font-bold ${getScoreColor(stock.ai_analysis.swingTradeScore)}`}>
              {stock.ai_analysis.swingTradeScore.toFixed(1)}
            </span>
            <span className="text-sm text-zinc-500">/ 10</span>
          </div>
          <span className={`text-xs font-medium ${getScoreColor(stock.ai_analysis.swingTradeScore)}`}>
            {getScoreLabel(stock.ai_analysis.swingTradeScore)}
          </span>
        </div>
      </div>

      {/* Summaries (Truncated) */}
      <div className="space-y-2 mb-4">
        <div className="bg-zinc-800/30 rounded-lg p-3">
          <p className="text-xs text-zinc-400 line-clamp-2">
            <span className="font-semibold text-emerald-400">Fundamentalista:</span>{' '}
            {stock.ai_analysis.buyAndHoldSummary}
          </p>
        </div>
        <div className="bg-zinc-800/30 rounded-lg p-3">
          <p className="text-xs text-zinc-400 line-clamp-2">
            <span className="font-semibold text-blue-400">Técnico:</span>{' '}
            {stock.ai_analysis.swingTradeSummary}
          </p>
        </div>
      </div>

      {/* Action Button */}
      <Link href={`/analises?ticker=${stock.symbol}`}>
        <button className="w-full px-4 py-2.5 bg-zinc-800 border border-zinc-700 text-white rounded-lg hover:bg-zinc-700 hover:border-purple-500/50 transition-all flex items-center justify-center gap-2 text-sm font-medium group">
          Ver Análise Completa
          <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
        </button>
      </Link>

      {/* Generated At */}
      <p className="text-xs text-zinc-600 mt-3 text-center">
        Gerada em: {new Date(stock.ai_analysis.generatedAt).toLocaleTimeString('pt-BR', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })}
      </p>
    </div>
  )
}

