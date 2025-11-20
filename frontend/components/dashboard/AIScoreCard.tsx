'use client'

import { useState } from 'react'
import { TrendingUp, TrendingDown, ArrowRight, Landmark, Zap, Sparkles, Bot } from 'lucide-react'
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
  predictiveSignals?: {
    score?: number | null
    raw_prediction?: number
    horizon_days?: number
    source?: string
  }
  ai_analysis?: {
    buyAndHoldScore: number
    buyAndHoldSummary: string
    swingTradeScore: number
    swingTradeSummary: string
    dayTradeScore: number
    dayTradeSummary: string
    recommendation: string
    generatedAt: string
  }
}

interface AIScoreCardProps {
  stock: Stock
  onAnalysisGenerated?: () => void
}

export default function AIScoreCard({ stock, onAnalysisGenerated }: AIScoreCardProps) {
  const [generating, setGenerating] = useState(false)
  const isPositive = stock.dailyVariation >= 0
  const predictiveScore = typeof stock.predictiveSignals?.score === 'number' ? stock.predictiveSignals.score : null
  const predictiveHorizon = stock.predictiveSignals?.horizon_days ?? 90

  const generateAnalysis = async () => {
    setGenerating(true)
    
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
      
      if (data && data.symbol) {
        console.log(`[HOMEPAGE] Análise gerada para ${stock.symbol}`)
        // Aguardar 1 segundo antes de recarregar para garantir que cache foi salvo
        await new Promise(resolve => setTimeout(resolve, 1000))
        // Chamar callback para atualizar lista
        if (onAnalysisGenerated) {
          onAnalysisGenerated()
        }
      }
    } catch (error) {
      console.error('Erro ao gerar análise:', error)
    } finally {
      setGenerating(false)
    }
  }

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

  // Se não há análise, mostrar card de "Gerar Análise" - Glassmorphism
  if (!stock.ai_analysis) {
    return (
      <div className="bg-zinc-900/70 backdrop-blur-xl border border-zinc-800/50 rounded-2xl p-5 hover:border-emerald-500/30 transition-all duration-500 animate-in fade-in">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-white">{stock.symbol}</h3>
            <p className="text-xs text-zinc-500 truncate">{stock.name}</p>
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

        {/* Predictive Score */}
        <div className="mb-4">
          {predictiveScore !== null ? (
            <div className="flex items-center justify-between px-4 py-3 rounded-2xl border border-emerald-500/30 bg-emerald-500/5">
              <div>
                <p className="text-[11px] uppercase tracking-wider text-emerald-300 font-semibold">
                  ML Proprietário · Taze Model
                </p>
                <p className="text-[11px] text-zinc-500 mt-0.5">
                  Horizonte {predictiveHorizon} dias
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-emerald-300">
                  {predictiveScore.toFixed(1)} <span className="text-sm text-emerald-200">/ 10</span>
                </p>
                <p className="text-[11px] text-zinc-400">
                  {getScoreLabel(predictiveScore)}
                </p>
              </div>
            </div>
          ) : (
            <div className="px-4 py-3 rounded-2xl border border-dashed border-zinc-700 text-[11px] text-zinc-500">
              Nosso modelo proprietário está treinando novos dados. Assim que disponível, o score preditivo aparecerá aqui.
            </div>
          )}
        </div>

        {/* Call to Action */}
        {generating ? (
          <div className="flex flex-col items-center justify-center py-8 border border-zinc-700 rounded-lg">
            <Bot size={48} className="text-purple-400 animate-pulse mb-4" />
            <p className="text-sm font-semibold text-zinc-300 mb-2">
              Analisando {stock.symbol} com IA...
            </p>
            <p className="text-xs text-zinc-500 mb-4">
              Processando dados técnicos e fundamentalistas...
            </p>
            <div className="w-full max-w-[200px] space-y-2">
              <div className="h-2 bg-zinc-800 rounded animate-pulse" />
              <div className="h-2 bg-zinc-800 rounded animate-pulse w-5/6" />
              <div className="h-2 bg-zinc-800 rounded animate-pulse w-4/5" />
            </div>
          </div>
        ) : (
          <>
            <div className="flex flex-col items-center justify-center py-6 border border-dashed border-zinc-700 rounded-lg mb-4">
              <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center mb-3">
                <Sparkles className="w-6 h-6 text-purple-400" />
              </div>
              <p className="text-sm text-zinc-400">
                Nenhuma análise gerada ainda
              </p>
              <p className="text-xs text-zinc-600 mt-1">
                3 perfis: Buy & Hold • Swing Trade • Day Trade
              </p>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={generateAnalysis}
                disabled={generating}
                className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-emerald-500 text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-emerald-500/30 hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm"
              >
                <Sparkles size={16} />
                Gerar Análise
              </button>
              
              <Link href={`/analises?ticker=${stock.symbol}`}>
                <button className="w-full px-4 py-2.5 bg-zinc-800 border border-zinc-700 text-white rounded-lg hover:bg-zinc-700 hover:border-purple-500/50 transition-all flex items-center justify-center gap-2 text-sm font-medium">
                  Ver Detalhes
                  <ArrowRight size={16} />
                </button>
              </Link>
            </div>
          </>
        )}
      </div>
    )
  }

  // Card com análise - Glassmorphism e Animado
  return (
    <div className="bg-zinc-900/70 backdrop-blur-xl border border-zinc-800/50 rounded-2xl p-5 hover:border-emerald-500/30 hover:shadow-2xl hover:shadow-emerald-500/10 transition-all duration-500 animate-in fade-in slide-in-from-bottom-4">
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

      {/* Recommendation Badge - Moderno */}
      <div className="mb-4">
        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl border text-xs font-bold backdrop-blur-xl shadow-lg ${getRecommendationColor(stock.ai_analysis.recommendation)}`}>
          {stock.ai_analysis.recommendation.includes('COMPRA') && <TrendingUp size={14} />}
          {stock.ai_analysis.recommendation.includes('VENDA') && <TrendingDown size={14} />}
          {stock.ai_analysis.recommendation}
        </div>
      </div>

      {/* Scores Grid - 3 Colunas Modernas */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        {/* Buy & Hold Score + ML */}
        <div className="bg-zinc-800/30 backdrop-blur-sm border border-zinc-700/50 rounded-xl p-3 hover:bg-zinc-800/50 hover:border-emerald-500/30 transition-all duration-300">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1">
              <Landmark className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-xs font-semibold text-zinc-400">Warren</span>
            </div>
            {predictiveScore !== null && (
              <span className="text-[10px] font-semibold text-emerald-300 border border-emerald-500/40 rounded-full px-2 py-0.5">
                ML Proprietário
              </span>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className={`text-2xl font-bold ${getScoreColor(stock.ai_analysis.buyAndHoldScore)}`}>
                  {stock.ai_analysis.buyAndHoldScore.toFixed(1)}
                </span>
                <span className="text-xs text-zinc-500">/ 10</span>
              </div>
              <span className={`text-xs font-medium ${getScoreColor(stock.ai_analysis.buyAndHoldScore)}`}>
                {getScoreLabel(stock.ai_analysis.buyAndHoldScore)}
              </span>
              <p className="text-xs text-zinc-500 mt-1">Buy & Hold</p>
            </div>

            <div className="pl-4 border-l border-zinc-700/50 flex-1">
              {predictiveScore !== null ? (
                <div className="text-right">
                  <p className="text-[11px] text-zinc-500">Taze Model</p>
                  <div className="flex items-baseline justify-end gap-1 mb-1">
                    <span className="text-2xl font-bold text-emerald-300">
                      {predictiveScore.toFixed(1)}
                    </span>
                    <span className="text-xs text-zinc-500">/ 10</span>
                  </div>
                  <span className="text-[11px] text-zinc-400">
                    {getScoreLabel(predictiveScore)}
                  </span>
                  <p className="text-[10px] text-zinc-500 mt-1">Horizonte {predictiveHorizon}d</p>
                </div>
              ) : (
                <p className="text-[11px] text-zinc-500">
                  Modelo proprietário em treinamento
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Swing Trade Score */}
        <div className="bg-zinc-800/30 backdrop-blur-sm border border-zinc-700/50 rounded-xl p-3 hover:bg-zinc-800/50 hover:border-blue-500/30 transition-all duration-300">
          <div className="flex items-center gap-1 mb-2">
            <TrendingUp className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-xs font-semibold text-zinc-400">Trader</span>
          </div>
          <div className="flex items-baseline gap-1 mb-1">
            <span className={`text-2xl font-bold ${getScoreColor(stock.ai_analysis.swingTradeScore)}`}>
              {stock.ai_analysis.swingTradeScore.toFixed(1)}
            </span>
            <span className="text-xs text-zinc-500">/ 10</span>
          </div>
          <span className={`text-xs font-medium ${getScoreColor(stock.ai_analysis.swingTradeScore)}`}>
            {getScoreLabel(stock.ai_analysis.swingTradeScore)}
          </span>
          <p className="text-xs text-zinc-500 mt-1">Swing Trade</p>
        </div>

        {/* Day Trade Score */}
        <div className="bg-zinc-800/30 backdrop-blur-sm border border-zinc-700/50 rounded-xl p-3 hover:bg-zinc-800/50 hover:border-amber-500/30 transition-all duration-300">
          <div className="flex items-center gap-1 mb-2">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-xs font-semibold text-zinc-400">Viper</span>
          </div>
          <div className="flex items-baseline gap-1 mb-1">
            <span className={`text-2xl font-bold ${getScoreColor(stock.ai_analysis.dayTradeScore)}`}>
              {stock.ai_analysis.dayTradeScore.toFixed(1)}
            </span>
            <span className="text-xs text-zinc-500">/ 10</span>
          </div>
          <span className={`text-xs font-medium ${getScoreColor(stock.ai_analysis.dayTradeScore)}`}>
            {getScoreLabel(stock.ai_analysis.dayTradeScore)}
          </span>
          <p className="text-xs text-zinc-500 mt-1">Day Trade</p>
        </div>
      </div>

      {/* Summaries (Truncated) */}
      <div className="space-y-2 mb-4">
        <div className="bg-zinc-800/30 rounded-lg p-3">
          <p className="text-xs text-zinc-400 line-clamp-2">
            <span className="font-semibold text-emerald-400">🏛️ Fundamentalista:</span>{' '}
            {stock.ai_analysis.buyAndHoldSummary}
          </p>
        </div>
        <div className="bg-zinc-800/30 rounded-lg p-3">
          <p className="text-xs text-zinc-400 line-clamp-2">
            <span className="font-semibold text-blue-400">📈 Técnico:</span>{' '}
            {stock.ai_analysis.swingTradeSummary}
          </p>
        </div>
        <div className="bg-zinc-800/30 rounded-lg p-3">
          <p className="text-xs text-zinc-400 line-clamp-2">
            <span className="font-semibold text-amber-400">⚡ Volatilidade:</span>{' '}
            {stock.ai_analysis.dayTradeSummary}
          </p>
        </div>
      </div>

      {/* Action Button - Moderno */}
      <Link href={`/analises?ticker=${stock.symbol}`}>
        <button className="w-full px-4 py-3 bg-gradient-to-r from-emerald-600/20 to-emerald-500/20 backdrop-blur-xl border border-emerald-500/30 text-white rounded-xl hover:from-emerald-600 hover:to-emerald-500 hover:border-emerald-500 hover:shadow-lg hover:shadow-emerald-500/20 transition-all duration-300 flex items-center justify-center gap-2 text-sm font-medium group">
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
