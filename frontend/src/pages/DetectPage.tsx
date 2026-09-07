import { useState, useRef } from 'react'
import { detectionApi, DetectionResult } from '../api/client'
import { Scan, Upload, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'

export default function DetectPage() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DetectionResult | null>(null)
  const [error, setError] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (f: File) => {
    if (!f.type.startsWith('image/')) {
      setError('请上传图片文件')
      return
    }
    setFile(f)
    setError('')
    setResult(null)
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target?.result as string)
    reader.readAsDataURL(f)
  }

  const handleUpload = () => inputRef.current?.click()

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const handleDetect = async () => {
    if (!file) {
      setError('请先选择图片')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await detectionApi.detect(file)
      setResult(res.data)
    } catch (e: any) {
      setError(e.response?.data?.detail || '识别失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 65) return 'bg-red-500'
    if (score >= 35) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getScoreBg = (score: number) => {
    if (score >= 65) return 'bg-red-50 border-red-200 text-red-700'
    if (score >= 35) return 'bg-yellow-50 border-yellow-200 text-yellow-700'
    return 'bg-green-50 border-green-200 text-green-700'
  }

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div className="flex items-center gap-3">
        <Scan className="text-primary-600" size={28} />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AIGC 商品图识别</h1>
          <p className="text-sm text-gray-500 mt-1">上传图片，智能检测是否为 AI 生成内容</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 左侧：上传区 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">上传图片</h2>

          {/* 上传区域 */}
          <div
            onClick={handleUpload}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50/30 transition-colors"
          >
            {preview ? (
              <div className="space-y-3">
                <img src={preview} alt="预览" className="max-h-64 mx-auto rounded-lg" />
                <p className="text-sm text-gray-500">{file?.name}</p>
                <button
                  onClick={(e) => { e.stopPropagation(); handleUpload() }}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  重新选择
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <Upload className="mx-auto text-gray-400" size={48} />
                <p className="text-gray-500">点击或拖拽图片到此处</p>
                <p className="text-xs text-gray-400">支持 PNG、JPG、WebP，最大 10MB</p>
              </div>
            )}
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />
          </div>

          {/* 识别按钮 */}
          <button
            onClick={handleDetect}
            disabled={!file || loading}
            className="w-full mt-4 flex items-center justify-center gap-2 bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={18} />
                正在分析...
              </>
            ) : (
              <>
                <Scan size={18} />
                开始识别
              </>
            )}
          </button>

          {error && (
            <div className="mt-3 flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-3">
              <AlertCircle size={16} />
              {error}
            </div>
          )}
        </div>

        {/* 右侧：识别结果 */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">识别结果</h2>

          {result ? (
            <div className="space-y-4">
              {/* 总体判定 */}
              <div className={`rounded-xl border-2 p-4 ${result.is_aigc ? 'bg-red-50 border-red-300' : 'bg-green-50 border-green-300'}`}>
                <div className="flex items-center gap-3">
                  {result.is_aigc ? (
                    <AlertCircle className="text-red-600" size={32} />
                  ) : (
                    <CheckCircle className="text-green-600" size={32} />
                  )}
                  <div>
                    <div className="text-xl font-bold" style={{ color: result.is_aigc ? '#dc2626' : '#16a34a' }}>
                      {result.label}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      置信度: <span className="font-bold">{result.confidence}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* 置信度大数字 */}
              <div className="text-center py-4">
                <div className={`inline-flex items-baseline gap-1 ${result.is_aigc ? 'text-red-600' : 'text-green-600'}`}>
                  <span className="text-5xl font-bold">{result.confidence}</span>
                  <span className="text-2xl">%</span>
                </div>
                <p className="text-sm text-gray-500 mt-2">AI 生成置信度</p>
              </div>

              {/* 6项指标 */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">分析指标</h3>
                <div className="space-y-3">
                  {result.indicators.map((ind, i) => (
                    <div key={i} className={`rounded-lg border p-3 ${getScoreBg(ind.score)}`}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">{ind.name}</span>
                        <span className="text-sm font-bold">{ind.score}分</span>
                      </div>
                      {/* 进度条 */}
                      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${getScoreColor(ind.score)}`}
                          style={{ width: `${ind.score}%` }}
                        />
                      </div>
                      <p className="text-xs mt-1 opacity-80">{ind.desc}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 图片信息 */}
              <div className="text-xs text-gray-500 space-y-1 pt-2 border-t border-gray-100">
                <div>图片尺寸: {result.image_size}</div>
                <div className="truncate">图片哈希: {result.image_hash}</div>
                <div>检测时间: {new Date(result.detected_at).toLocaleString('zh-CN')}</div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-gray-400">
              <Scan size={48} className="mb-3 opacity-50" />
              <p>上传图片后点击「开始识别」</p>
              <p className="text-xs mt-1">结果将显示在此处</p>
            </div>
          )}
        </div>
      </div>

      {/* 详细分析 */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-3">详细分析报告</h2>
          <pre className="text-sm text-gray-600 whitespace-pre-wrap bg-gray-50 rounded-lg p-4">
            {result.details}
          </pre>
        </div>
      )}

      {/* 技术原理说明 */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">检测技术原理</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs text-blue-800">
          <div><b>频域能量分析</b> - FFT变换检测高频能量分布异常</div>
          <div><b>噪声模式分析</b> - 拉普拉斯方差检测噪声均匀性</div>
          <div><b>色彩分布分析</b> - 色彩饱和度与丰富度统计</div>
          <div><b>边缘锐度分析</b> - Sobel算子检测边缘特征</div>
          <div><b>纹理复杂度</b> - 局部方差分析纹理规律性</div>
          <div><b>伪影检测</b> - 块状伪影与重复模式检测</div>
        </div>
      </div>
    </div>
  )
}
