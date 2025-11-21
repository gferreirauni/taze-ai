import fs from 'node:fs/promises'
import path from 'node:path'

interface MarketSignal {
  symbol: string
  current_price?: number
  score?: number
  status?: string
  status_emoji?: string
  msg?: string
  last_update?: string
}

async function loadSignals(): Promise<MarketSignal[]> {
  const dataPath = path.join(process.cwd(), 'public', 'data', 'market_signals.json')

  try {
    const raw = await fs.readFile(dataPath, 'utf-8')
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) {
      return parsed
    }
    return []
  } catch (error) {
    console.error('[ADMIN] Falha ao ler market_signals.json', error)
    return []
  }
}

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  minimumFractionDigits: 2,
})

export default async function AdminPage() {
  const signals = await loadSignals()
  const today = new Date().toISOString().slice(0, 10)

  return (
    <div className="min-h-screen bg-zinc-950 text-white px-6 py-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <div>
          <p className="text-sm uppercase tracking-widest text-emerald-400/70">VeroAI • Controle</p>
          <h1 className="mt-2 text-3xl font-semibold text-white">Painel Administrativo</h1>
          <p className="text-sm text-zinc-400">
            Monitore os sinais publicados pela IA e valide se todos os ativos foram atualizados no dia.
          </p>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-zinc-800 bg-zinc-900/40 shadow-xl">
          <table className="min-w-full divide-y divide-zinc-800 text-sm">
            <thead className="bg-zinc-900/60 text-xs uppercase tracking-wide text-zinc-400">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">Ticker</th>
                <th className="px-4 py-3 text-left font-semibold">Preço Atual</th>
                <th className="px-4 py-3 text-left font-semibold">Score IA</th>
                <th className="px-4 py-3 text-left font-semibold">Status</th>
                <th className="px-4 py-3 text-left font-semibold">Última Atualização</th>
                <th className="px-4 py-3 text-left font-semibold">Status do Dado</th>
                <th className="px-4 py-3 text-left font-semibold">Mensagem</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {signals.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-zinc-500">
                    Nenhum dado disponível. Verifique se o pipeline de inferência já foi executado.
                  </td>
                </tr>
              )}

              {signals.map((signal) => {
                const lastUpdate = signal.last_update ? signal.last_update.slice(0, 10) : 'N/A'
                const isStale = !lastUpdate || lastUpdate !== today
                const badgeStyles = isStale
                  ? 'bg-rose-500/15 text-rose-300 border border-rose-500/30'
                  : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'

                return (
                  <tr key={signal.symbol} className="hover:bg-zinc-900/40">
                    <td className="px-4 py-3 font-semibold tracking-wide text-white">{signal.symbol}</td>
                    <td className="px-4 py-3 text-zinc-100">
                      {typeof signal.current_price === 'number'
                        ? currencyFormatter.format(signal.current_price)
                        : '—'}
                    </td>
                    <td className="px-4 py-3 text-lg font-semibold text-emerald-400">
                      {typeof signal.score === 'number' ? signal.score.toFixed(1) : '—'}
                    </td>
                    <td className="px-4 py-3 text-base">
                      <span className="font-medium text-white">
                        {signal.status_emoji ? `${signal.status_emoji} ` : ''}
                        {signal.status || '—'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-zinc-300">{lastUpdate}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${badgeStyles}`}>
                        {isStale ? 'Dados Atrasados' : 'Atualizado'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-zinc-300">{signal.msg || '—'}</td>
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
