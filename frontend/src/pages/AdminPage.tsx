import { useState, useEffect } from 'react'
import {
  PieChart, Pie, Cell, Legend, Tooltip,
  LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
  BarChart, Bar,
  AreaChart, Area,
  RadialBarChart, RadialBar,
} from 'recharts'
import { statsApi, type StatsData } from '../api/client'
import { TrendingUp, ShieldCheck, Image, Users, FileCheck, XCircle, Clock, type LucideIcon } from 'lucide-react'

const STATUS_COLORS = ['#3b82f6', '#22c55e', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4']
const TREND_COLOR = '#3b82f6'
const CERT_COLOR = '#22c55e'

export default function AdminPage() {
  const [stats, setStats] = useState<StatsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
    const timer = setInterval(loadStats, 30000)
    return () => clearInterval(timer)
  }, [])

  const loadStats = async () => {
    try {
      const res = await statsApi.get()
      setStats(res.data)
    } catch (e) {
      console.error('加载统计数据失败', e)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-gray-500">加载中...</span>
      </div>
    )
  }

  const { overview, compliance, status_dist, category_dist, daily_trend, daily_cert_trend } = stats

  const passRateData = [{ name: '通过率', value: compliance.pass_rate, fill: '#22c55e' }]

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">数据可视化大屏</h2>
        <span className="text-sm text-gray-400">每30秒自动刷新</span>
      </div>

      {/* 总览统计卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        <MetricCard label="总任务" value={overview.total_tasks} icon={TrendingUp} color="text-blue-600" bg="bg-blue-50" />
        <MetricCard label="已存证" value={overview.total_certified} icon={FileCheck} color="text-green-600" bg="bg-green-50" />
        <MetricCard label="未通过" value={overview.total_failed} icon={XCircle} color="text-red-600" bg="bg-red-50" />
        <MetricCard label="处理中" value={overview.total_pending} icon={Clock} color="text-yellow-600" bg="bg-yellow-50" />
        <MetricCard label="商家数" value={overview.total_merchants} icon={Users} color="text-purple-600" bg="bg-purple-50" />
        <MetricCard label="生成图片" value={overview.total_images} icon={Image} color="text-cyan-600" bg="bg-cyan-50" />
        <MetricCard label="存证证书" value={overview.total_certificates} icon={ShieldCheck} color="text-indigo-600" bg="bg-indigo-50" />
      </div>

      {/* 图表区域第一行：饼图 + 合规通过率 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 任务状态分布饼图 */}
        <ChartCard title="任务状态分布">
          {status_dist.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={status_dist}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {status_dist.map((_, i) => (
                    <Cell key={i} fill={STATUS_COLORS[i % STATUS_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </ChartCard>

        {/* 合规检测通过率 */}
        <ChartCard title="合规检测通过率">
          <ResponsiveContainer width="100%" height={280}>
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="60%"
              outerRadius="100%"
              data={passRateData}
              startAngle={90}
              endAngle={-270}
            >
              <RadialBar background dataKey="value" cornerRadius={10} />
              <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" className="text-4xl font-bold fill-gray-700">
                {compliance.pass_rate}%
              </text>
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="flex justify-around mt-2 text-sm">
            <div className="text-center">
              <p className="text-green-600 font-bold text-lg">{compliance.passed}</p>
              <p className="text-gray-500">检测通过</p>
            </div>
            <div className="text-center">
              <p className="text-red-600 font-bold text-lg">{compliance.failed}</p>
              <p className="text-gray-500">检测未通过</p>
            </div>
            <div className="text-center">
              <p className="text-blue-600 font-bold text-lg">{compliance.avg_score}</p>
              <p className="text-gray-500">平均得分</p>
            </div>
          </div>
        </ChartCard>
      </div>

      {/* 图表区域第二行：任务趋势 + 存证趋势 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 最近7天任务趋势 */}
        <ChartCard title="最近7天任务趋势">
          {daily_trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={daily_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12, fontFamily: 'Noto Sans CJK SC, sans-serif' }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="count"
                  name="任务数"
                  stroke={TREND_COLOR}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </ChartCard>

        {/* 最近7天存证趋势 */}
        <ChartCard title="最近7天存证趋势">
          {daily_cert_trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={daily_cert_trend}>
                <defs>
                  <linearGradient id="certGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={CERT_COLOR} stopOpacity={0.8} />
                    <stop offset="95%" stopColor={CERT_COLOR} stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12, fontFamily: 'Noto Sans CJK SC, sans-serif' }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="count"
                  name="存证数"
                  stroke={CERT_COLOR}
                  fill="url(#certGrad)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </ChartCard>
      </div>

      {/* 图表区域第三行：类目分布柱状图 */}
      <ChartCard title="商品类目分布">
        {category_dist.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={category_dist}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 12, fontFamily: 'Noto Sans CJK SC, sans-serif' }}
                interval={0}
              />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" name="任务数" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <EmptyChart />
        )}
      </ChartCard>
    </div>
  )
}

// ===== 子组件 =====

function MetricCard({
  label, value, icon: Icon, color, bg,
}: {
  label: string
  value: number
  icon: LucideIcon
  color: string
  bg: string
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 flex flex-col items-center">
      <div className={`w-10 h-10 rounded-full ${bg} flex items-center justify-center mb-2`}>
        <Icon size={20} className={color} />
      </div>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  )
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-base font-semibold text-gray-700 mb-4">{title}</h3>
      {children}
    </div>
  )
}

function EmptyChart() {
  return (
    <div className="flex items-center justify-center h-[260px] text-gray-300 text-sm">
      暂无数据
    </div>
  )
}
