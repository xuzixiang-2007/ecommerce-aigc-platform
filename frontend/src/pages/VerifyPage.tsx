import { useState } from 'react'
import { certificateApi, type VerifyResult } from '../api/client'
import { ShieldCheck, Upload, Loader2, CheckCircle2, XCircle } from 'lucide-react'

export default function VerifyPage() {
  const [hashInput, setHashInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<VerifyResult | null>(null)

  const handleVerify = async () => {
    if (!hashInput.trim()) {
      alert('请输入图片哈希值')
      return
    }
    setLoading(true)
    setResult(null)
    try {
      const res = await certificateApi.verify(hashInput.trim())
      setResult(res.data)
    } catch (e: any) {
      alert('验证失败: ' + (e.response?.data?.detail || e.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* 说明 */}
      <div className="text-center">
        <ShieldCheck className="mx-auto text-primary-600 mb-2" size={48} />
        <h2 className="text-xl font-bold text-gray-800">区块链存证验证</h2>
        <p className="text-sm text-gray-500 mt-1">
          输入图片的 SHA-256 哈希值，验证其链上存证记录
        </p>
      </div>

      {/* 输入区 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <label className="block text-sm text-gray-500 mb-2">图片哈希值 (SHA-256)</label>
        <textarea
          value={hashInput}
          onChange={(e) => setHashInput(e.target.value)}
          placeholder="粘贴图片的 SHA-256 哈希值..."
          rows={3}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono"
        />
        <button
          onClick={handleVerify}
          disabled={loading}
          className="mt-3 bg-primary-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <Loader2 className="animate-spin" size={16} /> 验证中...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Upload size={16} /> 开始验证
            </span>
          )}
        </button>
      </div>

      {/* 验证结果 */}
      {result && (
        <div className={`rounded-xl border p-6 ${result.verified ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
          <div className="flex items-center gap-3 mb-4">
            {result.verified ? (
              <CheckCircle2 className="text-green-600" size={32} />
            ) : (
              <XCircle className="text-red-600" size={32} />
            )}
            <div>
              <p className="text-lg font-bold">
                {result.verified ? '验证通过' : '验证未通过'}
              </p>
              <p className="text-sm text-gray-600">{result.message}</p>
            </div>
          </div>

          {result.certificate && (
            <div className="space-y-2 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <InfoRow label="证书编号" value={result.certificate.certificate_no || '-'} />
                <InfoRow label="区块高度" value={`#${result.certificate.block_number}`} />
                <InfoRow label="感知哈希" value={result.certificate.phash || '-'} />
                <InfoRow
                  label="存证时间"
                  value={result.certificate.timestamp ? new Date(result.certificate.timestamp).toLocaleString('zh-CN') : '-'}
                />
              </div>
              <div className="pt-2 border-t border-gray-200">
                <p className="text-xs text-gray-500 mb-1">交易哈希</p>
                <p className="text-xs font-mono break-all">{result.certificate.tx_hash}</p>
              </div>
              <div className="pt-2 border-t border-gray-200">
                <p className="text-xs text-gray-500 mb-1">图片哈希</p>
                <p className="text-xs font-mono break-all">{result.certificate.image_hash}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-800">{value}</p>
    </div>
  )
}
