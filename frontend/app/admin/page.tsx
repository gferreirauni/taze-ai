import type { Prisma } from '@prisma/client'
import prisma from '@/lib/prisma'

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  minimumFractionDigits: 2,
})

const percentFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'percent',
  minimumFractionDigits: 2,
})

type SignalWithStock = Prisma.SignalGetPayload<{ include: { stock: true } }>

const SPARKLINE_WIDTH = 110
const SPARKLINE_HEIGHT = 32

function parseNumber(value: unknown): number | null {
  if (typeof value === 'number') return value
  if (typeof value === 'string') {
    const normalized = value.replace(/[R$\s,%]/g, '').replace(',', '.')
    const parsed = Number(normalized)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}

function buildSparkline(prices: number[]) {
  if (prices.length < 2) return null
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1
  const step = SPARKLINE_WIDTH / (prices.length - 1)

  let path = `M0 ${SPARKLINE_HEIGHT - ((prices[0] - min) / range) * SPARKLINE_HEIGHT}`
  prices.forEach((price, index) => {
    if (index === 0) return
    const x = step * index
    const y = SPARKLINE_HEIGHT - ((price - min) / range) * SPARKLINE_HEIGHT
    path += ` L${x.toFixed(2)} ${y.toFixed(2)}`
  })

  return {
    d: path,
    width: SPARKLINE_WIDTH,
    height: SPARKLINE_HEIGHT,
  }
}

function extractFundamentalSummary(fundamentals: Prisma.JsonValue | null | undefined) {
  if (!fundamentals || typeof fundamentals !== 'object' || Array.isArray(fundamentals)) {
    return { text: '—', marketCap: null }
  }

  const record = fundamentals as Record<string, unknown>
  const pl = parseNumber(record['indicators_pl'])
  const dy = parseNumber(record['indicators_div_yield'])
  const marketCap = parseNumber(record['market_value'])

  const parts: string[] = []
  if (pl !== null) parts.push(`P/L ${pl.toFixed(1)}`)
  if (dy !== null) parts.push(`DY ${dy.toFixed(1)}%`)
  return { text: parts.length ? parts.join(' • ') : '—', marketCap }
}

function formatMarketCap(value: number | null) {
  if (value === null) return '—'
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(1)} bi`
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)} mi`
  }
  return currencyFormatter.format(value)
}

function parseSeries(jsonValue: Prisma.JsonValue | null | undefined): number[] {
  if (!jsonValue || !Array.isArray(jsonValue)) return []
  return jsonValue
    .map((entry) => {
      if (typeof entry === 'object' && entry && !Array.isArray(entry) && 'price' in entry) {
        return parseNumber((entry as Record<string, unknown>).price) ?? null
      }
      return null
    })
    .filter((value): value is number => value !== null)
}

function statusAccent(status: string) {
  switch (status) {
    case 'COMPRA':
      return 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
    case 'RADAR':
      return 'bg-amber-500/10 text-amber-200 border border-amber-500/30'
    default:
      return 'bg-rose-500/10 text-rose-200 border border-rose-500/30'
  }
}

export default async function AdminPage() {
  const today = new Date().toISOString().slice(0, 10)

  const rawSignals = await prisma.signal.findMany({
    orderBy: { analysisDate: 'desc' },
    include: { stock: true },
    take: 300,
  })

  const latestSignals: SignalWithStock[] = []
  const seen = new Set<string>()
  for (const signal of rawSignals) {
    if (seen.has(signal.stockSymbol)) continue
    seen.add(signal.stockSymbol)
    latestSignals.push(signal)
  }

  return (
    <div className="min-h-screen bg-zinc-950 px-6 py-10 text-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <div>
          <p className="text-xs uppercase tracking-widest text-emerald-400/70">VeroAI • Controle</p>
          <h1 className="mt-2 text-3xl font-semibold text-white">Painel Administrativo</h1>
          <p className="text-sm text-zinc-400">
            Monitoramento completo dos sinais matemáticos + contexto fundamentalista em tempo real.
          </p>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-zinc-800 bg-zinc-900/30 shadow-xl">
          <table className="min-w-full divide-y divide-zinc-800 text-sm">
            <thead className="bg-zinc-900/60 text-xs uppercase tracking-wide text-zinc-400">
              <tr>
                <th className="px-4 py-3 text-left">Ativo</th>
                <th className="px-4 py-3 text-left">Score & Status</th>
                <th className="px-4 py-3 text-left">Intraday</th>
                <th className="px-4 py-3 text-left">Indicadores Técnicos</th>
                <th className="px-4 py-3 text-left">Fundamentos</th>
                <th className="px-4 py-3 text-left">Mensagem</th>
                <th className="px-4 py-3 text-left">Dados</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {latestSignals.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-zinc-500">
                    Sem dados disponíveis. Rode o pipeline de inferência.
                  </td>
                </tr>
              )}

              {latestSignals.map((signal) => {
                const lastUpdate = signal.analysisDate.toISOString().slice(0, 10)
                const isStale = lastUpdate !== today
                const series = parseSeries(signal.intradaySeries)
                const sparkline = buildSparkline(series)
                const intradayPercent =
                  typeof signal.intradayPercent === 'number' ? percentFormatter.format(signal.intradayPercent / 100) : '—'
                const intradayChange =
                  typeof signal.intradayChange === 'number' ? signal.intradayChange.toFixed(2) : null
                const fundamentalsSummary = extractFundamentalSummary(signal.fundamentals)

                return (
                  <tr key={signal.id} className="hover:bg-zinc-900/40">
                    <td className="px-4 py-4">
                      <div className="flex flex-col">
                        <span className="text-base font-semibold tracking-wide">{signal.stockSymbol}</span>
                        <span className="text-sm text-zinc-300">{signal.stock?.name ?? '—'}</span>
                        <span className="text-xs text-zinc-500">
                          {signal.stock?.sector ?? '—'} {signal.stock?.segment ? `• ${signal.stock.segment}` : ''}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-3xl font-semibold text-white">{signal.score.toFixed(1)}</span>
                          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusAccent(signal.status)}`}>
                            {signal.status_emoji} {signal.status}
                          </span>
                        </div>
                        <p className="text-xs text-zinc-400">{signal.aiAnalysis ?? signal.msg ?? '—'}</p>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-3">
                          <span className="text-lg font-medium text-white">{currencyFormatter.format(signal.price)}</span>
                          <div
                            className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                              signal.intradayChange && signal.intradayChange > 0
                                ? 'bg-emerald-500/15 text-emerald-300'
                                : signal.intradayChange && signal.intradayChange < 0
                                  ? 'bg-rose-500/15 text-rose-300'
                                  : 'bg-zinc-700/40 text-zinc-200'
                            }`}
                          >
                            {intradayChange ? `${intradayChange > 0 ? '+' : ''}${intradayChange}` : '0.00'} |{' '}
                            {intradayPercent}
                          </div>
                        </div>
                        {sparkline ? (
                          <svg
                            width={sparkline.width}
                            height={sparkline.height}
                            viewBox={`0 0 ${sparkline.width} ${sparkline.height}`}
                            className="text-emerald-400"
                          >
                            <path d={sparkline.d} fill="none" stroke="currentColor" strokeWidth={2} />
                          </svg>
                        ) : (
                          <span className="text-xs text-zinc-500">Sem histórico intraday</span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="space-y-1 text-sm text-zinc-300">
                        <p>RSI 14: {signal.rsi ? signal.rsi.toFixed(1) : '—'}</p>
                        <p>Vol. 21d: {signal.volatility ? `${(signal.volatility * 100).toFixed(2)}%` : '—'}</p>
                        <p>
                          Volume: {signal.intradayVolume ? signal.intradayVolume.toLocaleString('pt-BR') : '—'}
                        </p>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="space-y-1 text-sm text-zinc-200">
                        <p>{fundamentalsSummary.text}</p>
                        <p className="text-xs text-zinc-500">
                          Market Cap: {formatMarketCap(fundamentalsSummary.marketCap)}
                        </p>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-sm text-zinc-200">{signal.msg}</td>
                    <td className="px-4 py-4">
                      <div className="flex flex-col gap-2 text-sm">
                        <span className="text-zinc-200">Atualizado: {lastUpdate}</span>
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-semibold ${
                            isStale
                              ? 'bg-rose-500/15 text-rose-200 border border-rose-500/30'
                              : 'bg-emerald-500/10 text-emerald-200 border border-emerald-500/30'
                          }`}
                        >
                          {isStale ? 'Dados Atrasados' : 'Atualizado hoje'}
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
    </div>
  )
}
