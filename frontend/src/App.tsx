import { useState, useEffect } from 'react'
import PortalPage from './pages/PortalPage'
import AdminPage from './pages/AdminPage'
import VerifyPage from './pages/VerifyPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DetectPage from './pages/DetectPage'
import { ShoppingCart, LayoutDashboard, ShieldCheck, Scan, LogOut, User } from 'lucide-react'

// ===== 简单路由（不依赖 react-router-dom）=====

export function navigate(path: string) {
  window.history.pushState({}, '', path)
  window.dispatchEvent(new Event('popstate'))
}

export function Link({ to, children, className }: { to: string; children: React.ReactNode; className?: string }) {
  return (
    <a
      href={to}
      onClick={(e) => {
        e.preventDefault()
        navigate(to)
      }}
      className={className}
    >
      {children}
    </a>
  )
}

// ===== 认证 Hook =====

interface MerchantInfo {
  id: number
  name: string
  phone: string
}

function useAuth() {
  const [merchant, setMerchant] = useState<MerchantInfo | null>(null)

  useEffect(() => {
    const check = () => {
      const saved = localStorage.getItem('merchant')
      if (saved) {
        try {
          setMerchant(JSON.parse(saved))
        } catch {
          setMerchant(null)
        }
      } else {
        setMerchant(null)
      }
    }
    check()
    window.addEventListener('authChange', check)
    return () => window.removeEventListener('authChange', check)
  }, [])

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('merchant')
    window.dispatchEvent(new Event('authChange'))
  }

  return { merchant, logout }
}

// ===== 头部导航 =====

function Header() {
  const { merchant, logout } = useAuth()

  const navItems = [
    { path: '/', label: '商家门户', icon: ShoppingCart },
    { path: '/admin', label: '管理后台', icon: LayoutDashboard },
    { path: '/detect', label: 'AIGC识别', icon: Scan },
    { path: '/verify', label: '存证验证', icon: ShieldCheck },
  ]

  return (
    <header className="bg-primary-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-lg font-bold">AIGC 存证平台</span>
        </div>
        <div className="flex items-center gap-2">
          <nav className="flex gap-1 flex-wrap">
            {navItems.map(({ path, label, icon: Icon }) => {
              const isActive = window.location.pathname === path
              return (
                <a
                  key={path}
                  href={path}
                  onClick={(e) => {
                    e.preventDefault()
                    navigate(path)
                  }}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium ${
                    isActive
                      ? 'bg-blue-500 text-gray-900 shadow-md'
                      : 'bg-blue-400 text-gray-800'
                  }`}
                >
                  <Icon size={16} />
                  {label}
                </a>
              )
            })}
          </nav>
          {merchant ? (
            <div className="flex items-center gap-2 flex-shrink-0">
              <div className="flex items-center gap-1.5 text-sm">
                <User size={16} />
                <span>{merchant.name}</span>
              </div>
              <button
                onClick={() => {
                  logout()
                  navigate('/login')
                }}
                className="flex items-center gap-1 text-primary-200 hover:text-white text-sm"
              >
                <LogOut size={14} />
                退出
              </button>
            </div>
          ) : (
            <a
              href="/login"
              onClick={(e) => {
                e.preventDefault()
                navigate('/login')
              }}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm bg-white text-primary-900 hover:bg-primary-50 font-medium shadow-md flex-shrink-0"
            >
              <User size={16} />
              登录
            </a>
          )}
        </div>
      </div>
    </header>
  )
}

// ===== 主应用 =====

export default function App() {
  const [route, setRoute] = useState(window.location.pathname)

  useEffect(() => {
    const onPop = () => setRoute(window.location.pathname)
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])

  const renderPage = () => {
    switch (route) {
      case '/':
        return <PortalPage />
      case '/admin':
        return <AdminPage />
      case '/detect':
        return <DetectPage />
      case '/verify':
        return <VerifyPage />
      case '/login':
        return <LoginPage />
      case '/register':
        return <RegisterPage />
      default:
        return <PortalPage />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-8">
        {renderPage()}
      </main>
      <footer className="text-center text-gray-400 text-sm py-6">
        电商AIGC商品图合规溯源存证平台 v1.0 | 人工智能精英算法大赛参赛项目
      </footer>
    </div>
  )
}
