import { useState } from 'react'
import { authApi } from '../api/client'
import { navigate, Link } from '../App'
import { LogIn } from 'lucide-react'

export default function LoginPage() {
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!phone || !password) {
      setError('请填写手机号和密码')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await authApi.login({ phone, password })
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('merchant', JSON.stringify({
        id: res.data.merchant_id,
        name: res.data.name,
        phone: res.data.phone,
      }))
      window.dispatchEvent(new Event('authChange'))
      navigate('/')
    } catch (e: any) {
      setError(e.response?.data?.detail || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto mt-12">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-10 h-10 rounded-full bg-primary-50 flex items-center justify-center">
            <LogIn className="text-primary-600" size={20} />
          </div>
          <h2 className="text-xl font-bold text-gray-800">商家登录</h2>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 text-sm rounded-lg p-3 mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">手机号</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="请输入手机号"
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 text-white py-2.5 rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? '登录中...' : '登录'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          还没有账号？{' '}
          <Link to="/register" className="text-primary-600 font-medium">
            立即注册
          </Link>
        </p>
      </div>
    </div>
  )
}
