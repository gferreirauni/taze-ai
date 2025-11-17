'use client'

import { LayoutDashboard, Briefcase, TrendingUp, Settings, LogOut, ChevronLeft, ChevronRight } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/' },
  { icon: Briefcase, label: 'Carteira', href: '/carteira' },
  { icon: TrendingUp, label: 'Análises', href: '/analises' },
  { icon: Settings, label: 'Configurações', href: '/config' },
]

interface SidebarProps {
  collapsed?: boolean
  onToggle?: () => void
}

export default function Sidebar({ collapsed = false, onToggle }: SidebarProps) {
  const pathname = usePathname()

  return (
    <div className={`fixed left-0 top-0 h-screen bg-zinc-950 border-r border-zinc-800 flex flex-col transition-all duration-300 z-40 ${
      collapsed ? 'w-20' : 'w-64'
    } md:translate-x-0 ${collapsed ? '-translate-x-full md:translate-x-0' : ''}`}>
      {/* Logo e Toggle */}
      <div className="p-6 border-b border-zinc-800 relative">
        {!collapsed ? (
          <>
            <h1 className="text-2xl font-bold text-white">
              Taze<span className="text-emerald-500">AI</span>
            </h1>
            <p className="text-xs text-zinc-500 mt-1">Investimentos Inteligentes</p>
          </>
        ) : (
          <h1 className="text-xl font-bold text-emerald-500 text-center">
            TA
          </h1>
        )}
        
        {/* Toggle Button */}
        <button
          onClick={onToggle}
          className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 bg-zinc-800 border border-zinc-700 rounded-full flex items-center justify-center hover:bg-emerald-500 hover:border-emerald-500 transition-all z-10"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4 text-white" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-white" />
          )}
        </button>
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
                flex items-center gap-3 px-4 py-3 rounded-lg transition-all group relative
                ${isActive 
                  ? 'bg-emerald-500/10 text-emerald-500 font-medium' 
                  : 'text-zinc-400 hover:bg-zinc-900 hover:text-white'
                }
                ${collapsed ? 'justify-center' : ''}
              `}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span>{item.label}</span>}
              
              {/* Tooltip quando collapsed */}
              {collapsed && (
                <div className="absolute left-full ml-2 px-3 py-2 bg-zinc-900 border border-zinc-700 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
                  {item.label}
                </div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-zinc-800">
        <div className={`flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-zinc-900 transition-colors cursor-pointer group relative ${
          collapsed ? 'justify-center' : ''
        }`}>
          <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-500 font-semibold flex-shrink-0">
            G
          </div>
          {!collapsed && (
            <>
              <div className="flex-1">
                <p className="text-sm font-medium text-white">Gustavo F.</p>
                <p className="text-xs text-zinc-500">Investidor</p>
              </div>
              <LogOut className="w-4 h-4 text-zinc-500" />
            </>
          )}
          
          {/* Tooltip quando collapsed */}
          {collapsed && (
            <div className="absolute left-full ml-2 px-3 py-2 bg-zinc-900 border border-zinc-700 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
              Gustavo F.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

