'use client'

import { useState, useMemo } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Calendar } from 'lucide-react'

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

type Period = 7 | 15 | 30 | 90 | 'custom'

export default function StockChart({ data, stockName, stockSymbol, currentPrice, monthVariation }: StockChartProps) {
  // Calcular datas padrão baseadas nos dados disponíveis
  const getDefaultDates = () => {
    if (!data || data.length === 0) return { start: '', end: '' }
    
    const lastDate = data[data.length - 1].date // Última data com dados (ex: 13/11)
    const firstDate = data[0].date // Primeira data disponível
    
    // Data fim = última data com dados
    const endDate = lastDate
    
    // Data início = 30 dias antes da última data
    const startDateObj = new Date(lastDate)
    startDateObj.setDate(startDateObj.getDate() - 30)
    const startDate = startDateObj.toISOString().split('T')[0]
    
    return { start: startDate, end: endDate }
  }

  const defaultDates = getDefaultDates()

  // Estado para controlar o período selecionado (padrão: 30 dias)
  const [selectedPeriod, setSelectedPeriod] = useState<Period>(30)
  const [customStartDate, setCustomStartDate] = useState(defaultDates.start)
  const [customEndDate, setCustomEndDate] = useState(defaultDates.end)
  const [showCustomPicker, setShowCustomPicker] = useState(false)

  // Filtrar dados baseado no período selecionado (usando DATAS reais, não quantidade de registros)
  const filteredData = useMemo(() => {
    if (!data || data.length === 0) return []

    // Pegar a data mais recente (última do array)
    const lastDate = new Date(data[data.length - 1].date)
    
    let startDate: Date

    if (selectedPeriod === 'custom') {
      // Usar datas customizadas se selecionado
      if (!customStartDate || !customEndDate) return data
      startDate = new Date(customStartDate)
      const endDate = new Date(customEndDate)
      
      return data.filter(item => {
        const itemDate = new Date(item.date)
        return itemDate >= startDate && itemDate <= endDate
      })
    } else {
      // Calcular data de início baseado no período (dias de CALENDÁRIO)
      startDate = new Date(lastDate)
      startDate.setDate(startDate.getDate() - selectedPeriod)
    }

    // Filtrar todos os registros a partir da data calculada
    return data.filter(item => {
      const itemDate = new Date(item.date)
      return itemDate >= startDate
    })
  }, [data, selectedPeriod, customStartDate, customEndDate])

  // Formatar data para exibição (mostrar apenas dia/mês)
  const formattedData = useMemo(() => {
    return filteredData.map(item => ({
      ...item,
      displayDate: new Date(item.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
    }))
  }, [filteredData])

  // Calcular variação baseada nos dados filtrados
  const variation = useMemo(() => {
    if (filteredData.length < 2) return 0
    
    const firstValue = filteredData[0].value
    const lastValue = filteredData[filteredData.length - 1].value
    return ((lastValue - firstValue) / firstValue) * 100
  }, [filteredData])

  // Usar currentPrice do backend ou último valor do histórico
  const lastValue = currentPrice || data[data.length - 1]?.value || 0
  const isPositive = variation >= 0

  // Opções de período
  const periods: Period[] = [7, 15, 30, 90]

  // Handler para aplicar datas customizadas
  const handleCustomDateApply = () => {
    if (customStartDate && customEndDate) {
      setSelectedPeriod('custom')
      setShowCustomPicker(false)
    }
  }

  // Formatar label do período
  const getPeriodLabel = () => {
    if (selectedPeriod === 'custom') {
      const start = new Date(customStartDate).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
      const end = new Date(customEndDate).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
      return `${start} - ${end}`
    }
    return `${selectedPeriod}d`
  }

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
              {isPositive ? '+' : ''}{variation.toFixed(2)}% ({getPeriodLabel()})
            </p>
          </div>
        </div>

        {/* Filtros de Período */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm text-zinc-500 mr-2">Período:</span>
          {periods.map((period) => (
            <button
              key={period}
              onClick={() => {
                setSelectedPeriod(period)
                setShowCustomPicker(false)
              }}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                selectedPeriod === period
                  ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                  : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-white'
              }`}
            >
              {period}d
            </button>
          ))}
          
          {/* Botão Personalizado */}
          <button
            onClick={() => setShowCustomPicker(!showCustomPicker)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
              selectedPeriod === 'custom'
                ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-white'
            }`}
          >
            <Calendar size={16} />
            Personalizado
          </button>
        </div>

        {/* Seletor de Datas Customizado */}
        {showCustomPicker && (
          <div className="mt-4 p-4 bg-zinc-800/50 border border-zinc-700 rounded-lg backdrop-blur-sm">
            <div className="grid grid-cols-2 gap-4 mb-3">
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">Data Início</label>
                <div className="relative">
                  <input
                    type="date"
                    value={customStartDate}
                    onChange={(e) => setCustomStartDate(e.target.value)}
                    max={customEndDate || defaultDates.end}
                    style={{
                      colorScheme: 'dark'
                    }}
                    className="w-full px-3 py-2.5 bg-zinc-900/90 border border-zinc-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all [&::-webkit-calendar-picker-indicator]:filter [&::-webkit-calendar-picker-indicator]:invert [&::-webkit-calendar-picker-indicator]:opacity-70 [&::-webkit-calendar-picker-indicator]:hover:opacity-100 [&::-webkit-calendar-picker-indicator]:cursor-pointer"
                  />
                </div>
                <p className="text-xs text-zinc-500 mt-1">
                  Formato: DD/MM/AAAA
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">
                  Data Fim 
                  <span className="text-xs text-zinc-500 ml-1">(última: {new Date(defaultDates.end).toLocaleDateString('pt-BR')})</span>
                </label>
                <div className="relative">
                  <input
                    type="date"
                    value={customEndDate}
                    onChange={(e) => setCustomEndDate(e.target.value)}
                    min={customStartDate || undefined}
                    max={defaultDates.end}
                    style={{
                      colorScheme: 'dark'
                    }}
                    className="w-full px-3 py-2.5 bg-zinc-900/90 border border-zinc-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all [&::-webkit-calendar-picker-indicator]:filter [&::-webkit-calendar-picker-indicator]:invert [&::-webkit-calendar-picker-indicator]:opacity-70 [&::-webkit-calendar-picker-indicator]:hover:opacity-100 [&::-webkit-calendar-picker-indicator]:cursor-pointer"
                  />
                </div>
                <p className="text-xs text-zinc-500 mt-1">
                  Última data com dados disponíveis
                </p>
              </div>
            </div>
            
            <div className="flex items-center justify-between pt-3 border-t border-zinc-700">
              <button
                onClick={() => {
                  setCustomStartDate(defaultDates.start)
                  setCustomEndDate(defaultDates.end)
                }}
                className="text-xs text-zinc-400 hover:text-emerald-400 transition-colors"
              >
                Restaurar padrão (últimos 30 dias)
              </button>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowCustomPicker(false)}
                  className="px-4 py-2 bg-zinc-700 text-zinc-300 rounded-lg text-sm font-medium hover:bg-zinc-600 transition-all"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCustomDateApply}
                  disabled={!customStartDate || !customEndDate}
                  className="px-4 py-2 bg-emerald-500 text-white rounded-lg text-sm font-medium hover:bg-emerald-600 disabled:bg-zinc-700 disabled:text-zinc-500 disabled:cursor-not-allowed transition-all shadow-lg shadow-emerald-500/20 disabled:shadow-none"
                >
                  Aplicar Período
                </button>
              </div>
            </div>
          </div>
        )}
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

