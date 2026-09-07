import { useState, useEffect } from 'react'
import { taskApi, merchantApi, type Task, type GenerateResult } from '../api/client'
import { Sparkles, CheckCircle2, XCircle, Loader2, FileText } from 'lucide-react'

const STATUS_MAP: Record<string, { label: string; color: string }> = {
  pending: { label: '待处理', color: 'bg-gray-100 text-gray-600' },
  generating: { label: '生成中', color: 'bg-blue-100 text-blue-600' },
  checking: { label: '检测中', color: 'bg-yellow-100 text-yellow-600' },
  passed: { label: '已通过', color: 'bg-green-100 text-green-600' },
  failed: { label: '未通过', color: 'bg-red-100 text-red-600' },
  certified: { label: '已存证', color: 'bg-primary-100 text-primary-600' },
}

export default function PortalPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [merchants, setMerchants] = useState<any[]>([])
  const [merchantId, setMerchantId] = useState(1)
  const [productName, setProductName] = useState('')
  const [category, setCategory] = useState('数码')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<GenerateResult | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [taskRes, merchantRes] = await Promise.all([
        taskApi.list(),
        merchantApi.list(),
      ])
      setTasks(taskRes.data)
      setMerchants(merchantRes.data)
    } catch (e) {
      console.error('加载数据失败', e)
    }
  }

  const handleCreateAndGenerate = async () => {
    if (!productName.trim()) {
      alert('请输入商品名称')
      return
    }
    setLoading(true)
    setResult(null)
    try {
      const createRes = await taskApi.create({
        merchant_id: merchantId,
        product_name: productName,
        product_category: category,
      })
      const taskId = createRes.data.id
      const genRes = await taskApi.generate(taskId)
      setResult(genRes.data)
      await loadData()
    } catch (e: any) {
      alert('操作失败: ' + (e.response?.data?.detail || e.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* 生成区域 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="text-primary-600" size={20} />
          AIGC 商品图生成
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm text-gray-500 mb-1">商家</label>
            <select
              value={merchantId}
              onChange={(e) => setMerchantId(Number(e.target.value))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            >
              {merchants.map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-500 mb-1">商品名称</label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="例: 无线蓝牙耳机"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-500 mb-1">商品类目</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            >
              <option>数码</option>
              <option>服饰</option>
              <option>食品</option>
              <option>美妆</option>
              <option>家居</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleCreateAndGenerate}
          disabled={loading}
          className="bg-primary-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <Loader2 className="animate-spin" size={16} /> 生成中...
            </span>
          ) : (
            '一键生成 + 合规检测 + 存证'
          )}
        </button>
      </div>

      {/* 生成结果 */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">生成结果</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 图片 */}
            <div>
              {result.image?.image_url ? (
                <img
                  src={result.image.image_url}
                  alt="生成结果"
                  className="w-full rounded-lg border border-gray-200"
                />
              ) : (
                <div className="w-full aspect-square bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">
                  图片加载失败
                </div>
              )}
              <div className="mt-2 text-xs text-gray-500 space-y-1">
                <p>图片哈希: {result.image?.image_hash?.substring(0, 32)}...</p>
                <p>感知哈希: {result.image?.phash}</p>
              </div>
            </div>

            {/* 详情 */}
            <div className="space-y-3">
              {/* 状态 */}
              <div className={`p-3 rounded-lg ${result.status === 'certified' ? 'bg-green-50' : 'bg-red-50'}`}>
                <div className="flex items-center gap-2">
                  {result.status === 'certified' ? (
                    <CheckCircle2 className="text-green-600" size={20} />
                  ) : (
                    <XCircle className="text-red-600" size={20} />
                  )}
                  <span className="font-medium">
                    {result.status === 'certified' ? '全流程完成' : '合规检测未通过'}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{result.message}</p>
              </div>

              {/* 合规报告 */}
              {result.compliance && (
                <div className="border border-gray-200 rounded-lg p-3 space-y-1.5">
                  <p className="text-sm font-medium">合规检测报告</p>
                  <p className="text-xs">内容安全: {result.compliance.content_safety === 'pass' ? '通过' : '不通过'}</p>
                  <p className="text-xs">版权检测: {result.compliance.copyright_check === 'pass' ? '通过' : '不通过'}</p>
                  <p className="text-xs">规范检查: {result.compliance.spec_check === 'pass' ? '通过' : '不通过'}</p>
                  <p className="text-xs">综合得分: {result.compliance.score}分</p>
                </div>
              )}

              {/* 证书 */}
              {result.certificate && (
                <div className="border border-primary-200 bg-primary-50 rounded-lg p-3 space-y-1.5">
                  <p className="text-sm font-medium flex items-center gap-1">
                    <FileText size={16} className="text-primary-600" />
                    区块链存证证书
                  </p>
                  <p className="text-xs">证书编号: {result.certificate.certificate_no}</p>
                  <p className="text-xs">交易哈希: {result.certificate.tx_hash?.substring(0, 24)}...</p>
                  <p className="text-xs">区块高度: #{result.certificate.block_number}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 任务列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">任务列表</h3>
        {tasks.length === 0 ? (
          <p className="text-gray-400 text-sm">暂无任务，试试生成一张商品图吧</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-gray-500">
                  <th className="py-2 text-left">ID</th>
                  <th className="py-2 text-left">商品名称</th>
                  <th className="py-2 text-left">类目</th>
                  <th className="py-2 text-left">状态</th>
                  <th className="py-2 text-left">创建时间</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <tr key={task.id} className="border-b border-gray-100">
                    <td className="py-2">#{task.id}</td>
                    <td className="py-2">{task.product_name}</td>
                    <td className="py-2">{task.product_category}</td>
                    <td className="py-2">
                      <span className={`px-2 py-0.5 rounded-full text-xs ${STATUS_MAP[task.status]?.color || ''}`}>
                        {STATUS_MAP[task.status]?.label || task.status}
                      </span>
                    </td>
                    <td className="py-2 text-gray-500">
                      {task.created_at ? new Date(task.created_at).toLocaleString('zh-CN') : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
