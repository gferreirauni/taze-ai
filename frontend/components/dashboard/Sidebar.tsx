'use client'

import { LayoutDashboard, Briefcase, TrendingUp, Settings, LogOut } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/' },
  { icon: Briefcase, label: 'Carteira', href: '/carteira' },
  { icon: TrendingUp, label: 'Análises', href: '/analises' },
  { icon: Settings, label: 'Configurações', href: '/config' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="fixed left-0 top-0 h-screen w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-zinc-800">
        <h1 className="text-2xl font-bold text-white">
          Taze<span className="text-emerald-500">AI</span>
        </h1>
        <p className="text-xs text-zinc-500 mt-1">Investimentos Inteligentes</p>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg transition-all
                ${isActive 
                  ? 'bg-emerald-500/10 text-emerald-500 font-medium' 
                  : 'text-zinc-400 hover:bg-zinc-900 hover:text-white'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-zinc-800">
        <div className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-zinc-900 transition-colors cursor-pointer">
          <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-500 font-semibold">
            G
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-white">Gustavo F.</p>
            <p className="text-xs text-zinc-500">Investidor</p>
          </div>
          <LogOut className="w-4 h-4 text-zinc-500" />
        </div>
      </div>
    </div>
  )
}

