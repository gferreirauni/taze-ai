'use client'

import { LucideIcon } from 'lucide-react'

interface SummaryCardProps {
  title: string
  value: string
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  icon: LucideIcon
}

export default function SummaryCard({ 
  title, 
  value, 
  change, 
  changeType = 'neutral',
  icon: Icon 
}: SummaryCardProps) {
  const changeColor = {
    positive: 'text-emerald-500',
    negative: 'text-red-500',
    neutral: 'text-zinc-400'
  }[changeType]

  const bgColor = {
    positive: 'bg-emerald-500/10',
    negative: 'bg-red-500/10',
    neutral: 'bg-zinc-800/50'
  }[changeType]

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:border-zinc-700 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-zinc-500 font-medium mb-2">{title}</p>
          <p className="text-3xl font-bold text-white mb-1">{value}</p>
          {change && (
            <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-md ${bgColor}`}>
              <span className={`text-sm font-semibold ${changeColor}`}>
                {change}
              </span>
            </div>
          )}
        </div>
        <div className="w-12 h-12 rounded-lg bg-emerald-500/10 flex items-center justify-center">
          <Icon className="w-6 h-6 text-emerald-500" />
        </div>
      </div>
    </div>
  )
}

