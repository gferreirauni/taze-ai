'use client'

import { TrendingUp, TrendingDown } from 'lucide-react'

interface Stock {
  symbol: string
  name: string
  sector: string
  currentPrice: number
  dailyVariation: number
}

interface StockListProps {
  stocks: Stock[]
  onSelectStock: (stock: Stock) => void
  selectedStock?: Stock
}

export default function StockList({ stocks, onSelectStock, selectedStock }: StockListProps) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
      <div className="p-6 border-b border-zinc-800">
        <h2 className="text-xl font-bold text-white">Ações Monitoradas</h2>
        <p className="text-sm text-zinc-500 mt-1">Acompanhe suas ações favoritas</p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-zinc-950">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Ação
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Setor
              </th>
              <th className="px-6 py-4 text-right text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Preço
              </th>
              <th className="px-6 py-4 text-right text-xs font-semibold text-zinc-400 uppercase tracking-wider">
                Variação
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {stocks.map((stock) => {
              const isPositive = stock.dailyVariation >= 0
              const isSelected = selectedStock?.symbol === stock.symbol
              
              return (
                <tr 
                  key={stock.symbol}
                  onClick={() => onSelectStock(stock)}
                  className={`
                    cursor-pointer transition-colors
                    ${isSelected 
                      ? 'bg-emerald-500/5 border-l-2 border-l-emerald-500' 
                      : 'hover:bg-zinc-800/50'
                    }
                  `}
                >
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-semibold text-white">{stock.symbol}</p>
                      <p className="text-sm text-zinc-500">{stock.name}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-zinc-800 text-zinc-300">
                      {stock.sector}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <p className="font-semibold text-white">
                      R$ {stock.currentPrice.toFixed(2)}
                    </p>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-md ${
                      isPositive ? 'bg-emerald-500/10' : 'bg-red-500/10'
                    }`}>
                      {isPositive ? (
                        <TrendingUp className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      <span className={`font-semibold ${
                        isPositive ? 'text-emerald-500' : 'text-red-500'
                      }`}>
                        {isPositive ? '+' : ''}{stock.dailyVariation.toFixed(2)}%
                      </span>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

