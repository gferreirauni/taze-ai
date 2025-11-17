'use client'

import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface HistoryData {
  date: string
  value: number
}

interface StockChartProps {
  data: HistoryData[]
  stockName: string
  stockSymbol: string
  currentPrice?: number
  monthVariation?: number
}

type Period = 7 | 15 | 30 | 90

export default function StockChart({ data, stockName, stockSymbol, currentPrice, monthVariation }: StockChartProps) {
  // Estado para controlar o período selecionado (padrão: 30 dias)
  const [selectedPeriod, setSelectedPeriod] = useState<Period>(30)

  // Filtrar dados baseado no período selecionado
  const filteredData = data.slice(-selectedPeriod)

  // Formatar data para exibição (mostrar apenas dia/mês)
  const formattedData = filteredData.map(item => ({
    ...item,
    displayDate: new Date(item.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  }))

  // Calcular variação baseada no período selecionado
  const calculateVariation = (period: Period) => {
    const periodData = data.slice(-period)
    if (periodData.length < 2) return 0
    
    const firstValue = periodData[0].value
    const lastValue = periodData[periodData.length - 1].value
    return ((lastValue - firstValue) / firstValue) * 100
  }

  // Usar currentPrice do backend ou último valor do histórico
  const lastValue = currentPrice || data[data.length - 1]?.value || 0
  
  // Variação baseada no período selecionado
  const variation = calculateVariation(selectedPeriod)
  const isPositive = variation >= 0

  // Opções de período
  const periods: Period[] = [7, 15, 30, 90]

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white">{stockSymbol}</h2>
            <p className="text-sm text-zinc-500">{stockName}</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-white">
              R$ {lastValue.toFixed(2)}
            </p>
            <p className={`text-sm font-semibold ${isPositive ? 'text-emerald-500' : 'text-red-500'}`}>
              {isPositive ? '+' : ''}{variation.toFixed(2)}% ({selectedPeriod}d)
            </p>
          </div>
        </div>

        {/* Filtros de Período */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-zinc-500 mr-2">Período:</span>
          {periods.map((period) => (
            <button
              key={period}
              onClick={() => setSelectedPeriod(period)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                selectedPeriod === period
                  ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                  : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-white'
              }`}
            >
              {period}d
            </button>
          ))}
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={formattedData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
            <XAxis 
              dataKey="displayDate" 
              stroke="#71717a"
              tick={{ fill: '#71717a', fontSize: 12 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              stroke="#71717a"
              tick={{ fill: '#71717a', fontSize: 12 }}
              tickLine={false}
              axisLine={false}
              domain={['dataMin - 1', 'dataMax + 1']}
              tickFormatter={(value) => `R$ ${value.toFixed(0)}`}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#18181b',
                border: '1px solid #27272a',
                borderRadius: '8px',
                color: '#fff'
              }}
              labelStyle={{ color: '#a1a1aa' }}
              formatter={(value: number) => [`R$ ${value.toFixed(2)}`, 'Preço']}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke={isPositive ? '#10b981' : '#ef4444'} 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: isPositive ? '#10b981' : '#ef4444' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
          <span className="text-zinc-400">Valorização</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <span className="text-zinc-400">Desvalorização</span>
        </div>
      </div>
    </div>
  )
}

