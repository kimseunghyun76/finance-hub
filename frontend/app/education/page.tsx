'use client'

import { useEffect, useState } from 'react'
import { educationApi, type EducationArticle, type ChatMessage } from '@/lib/api'
import { BookOpen, Sparkles, Trash2, Filter } from 'lucide-react'

const LEVEL_LABELS = {
  beginner: { label: '초보', emoji: '🌱', color: 'bg-green-100 text-green-700' },
  elementary: { label: '초급', emoji: '📘', color: 'bg-blue-100 text-blue-700' },
  intermediate: { label: '중급', emoji: '📙', color: 'bg-orange-100 text-orange-700' },
  advanced: { label: '고급', emoji: '📕', color: 'bg-red-100 text-red-700' },
}

export default function EducationPage() {
  const [articles, setArticles] = useState<EducationArticle[]>([])
  const [selectedArticle, setSelectedArticle] = useState<EducationArticle | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [filterLevel, setFilterLevel] = useState<string>('')
  const [filterCategory, setFilterCategory] = useState<string>('')
  const [showGenerateForm, setShowGenerateForm] = useState(false)
  const [topic, setTopic] = useState('')
  const [level, setLevel] = useState('beginner')
  const [category, setCategory] = useState('용어')

  useEffect(() => {
    loadArticles()
  }, [filterLevel, filterCategory])

  const loadArticles = async () => {
    setLoading(true)
    try {
      const params: any = {}
      if (filterLevel) params.level = filterLevel
      if (filterCategory) params.category = filterCategory
      const res = await educationApi.getArticles(params)
      setArticles(res.data)
      if (!selectedArticle && res.data.length > 0) {
        selectArticle(res.data[0])
      }
    } catch (error) {
      console.error('Failed to load articles:', error)
    } finally {
      setLoading(false)
    }
  }

  const selectArticle = (article: EducationArticle) => {
    setSelectedArticle(article)
    try {
      const parsed = JSON.parse(article.content)
      setMessages(parsed)
    } catch (error) {
      console.error('Failed to parse article content:', error)
      setMessages([])
    }
  }

  const handleGenerate = async () => {
    if (!topic.trim()) {
      alert('주제를 입력해주세요')
      return
    }
    setGenerating(true)
    try {
      const res = await educationApi.generateArticle({ topic, level, category })
      if (res.data.success) {
        setArticles([res.data.article, ...articles])
        selectArticle(res.data.article)
        setShowGenerateForm(false)
        setTopic('')
      }
    } catch (error) {
      console.error('Failed to generate article:', error)
      alert('강의 생성에 실패했습니다')
    } finally {
      setGenerating(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('정말 이 강의를 삭제하시겠습니까?')) return
    try {
      await educationApi.deleteArticle(id)
      setArticles(articles.filter(a => a.id !== id))
      if (selectedArticle?.id === id) {
        setSelectedArticle(null)
        setMessages([])
      }
    } catch (error) {
      console.error('Failed to delete article:', error)
      alert('삭제에 실패했습니다')
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-gradient-to-r from-purple-600 to-pink-600 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-1 flex items-center gap-2">
                <BookOpen className="w-8 h-8" />
                투자 교육 센터
              </h1>
              <p className="text-purple-100">AI가 생성하는 맞춤형 투자 강의</p>
            </div>
            <button
              onClick={() => setShowGenerateForm(!showGenerateForm)}
              className="flex items-center gap-2 px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition-colors"
            >
              <Sparkles className="w-5 h-5" />
              강의 생성하기
            </button>
          </div>
        </div>
      </header>

      {showGenerateForm && (
        <div className="border-b bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20">
          <div className="container mx-auto px-4 py-6">
            <div className="max-w-2xl">
              <h3 className="text-lg font-bold mb-4">AI 강의 생성</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">주제</label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="예: 배당금이란 무엇인가요?"
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    disabled={generating}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">레벨</label>
                    <select
                      value={level}
                      onChange={(e) => setLevel(e.target.value)}
                      className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                      disabled={generating}
                    >
                      <option value="beginner">초보 🌱</option>
                      <option value="elementary">초급 📘</option>
                      <option value="intermediate">중급 📙</option>
                      <option value="advanced">고급 📕</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">카테고리</label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                      disabled={generating}
                    >
                      <option value="용어">용어</option>
                      <option value="팁">팁</option>
                      <option value="분석기법">분석기법</option>
                    </select>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {generating ? '생성 중...' : '생성하기'}
                  </button>
                  <button
                    onClick={() => setShowGenerateForm(false)}
                    disabled={generating}
                    className="px-6 py-3 border rounded-lg font-semibold hover:bg-gray-50 disabled:opacity-50 transition-colors"
                  >
                    취소
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-4 space-y-4">
            <div className="p-4 border rounded-lg bg-card">
              <div className="flex items-center gap-2 mb-3">
                <Filter className="w-4 h-4" />
                <h3 className="font-semibold">필터</h3>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium mb-1">레벨</label>
                  <select
                    value={filterLevel}
                    onChange={(e) => setFilterLevel(e.target.value)}
                    className="w-full text-sm px-3 py-1.5 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">전체</option>
                    <option value="beginner">초보 🌱</option>
                    <option value="elementary">초급 📘</option>
                    <option value="intermediate">중급 📙</option>
                    <option value="advanced">고급 📕</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium mb-1">카테고리</label>
                  <select
                    value={filterCategory}
                    onChange={(e) => setFilterCategory(e.target.value)}
                    className="w-full text-sm px-3 py-1.5 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">전체</option>
                    <option value="용어">용어</option>
                    <option value="팁">팁</option>
                    <option value="분석기법">분석기법</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-sm text-muted-foreground px-2">
                전체 {articles.length}개의 강의
              </div>
              {loading ? (
                <div className="p-8 text-center text-muted-foreground">로딩 중...</div>
              ) : articles.length === 0 ? (
                <div className="p-8 text-center text-muted-foreground">
                  강의가 없습니다. 새 강의를 생성해보세요!
                </div>
              ) : (
                articles.map((article) => {
                  const levelInfo = LEVEL_LABELS[article.level as keyof typeof LEVEL_LABELS]
                  const isSelected = selectedArticle?.id === article.id
                  return (
                    <div
                      key={article.id}
                      className={'group p-4 border rounded-lg cursor-pointer transition-all ' + (isSelected ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/20' : 'hover:border-purple-300 hover:bg-gray-50 dark:hover:bg-gray-800')}
                      onClick={() => selectArticle(article)}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={'text-xs px-2 py-0.5 rounded-full font-medium ' + levelInfo.color}>
                              {levelInfo.emoji} {levelInfo.label}
                            </span>
                            <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-700">
                              {article.category}
                            </span>
                          </div>
                          <h3 className="font-semibold text-sm leading-tight mb-1 line-clamp-2">{article.title}</h3>
                          <p className="text-xs text-muted-foreground">조회 {article.views}회</p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDelete(article.id)
                          }}
                          className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-100 dark:hover:bg-red-900/20 rounded transition-all"
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </button>
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          </div>

          <div className="lg:col-span-8">
            {selectedArticle ? (
              <div className="border rounded-lg bg-card p-6">
                <div className="mb-6 pb-6 border-b">
                  <div className="flex items-center gap-2 mb-3">
                    {(() => {
                      const levelInfo = LEVEL_LABELS[selectedArticle.level as keyof typeof LEVEL_LABELS]
                      return (
                        <>
                          <span className={'text-sm px-3 py-1 rounded-full font-medium ' + levelInfo.color}>
                            {levelInfo.emoji} {levelInfo.label}
                          </span>
                          <span className="text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-700">
                            {selectedArticle.category}
                          </span>
                        </>
                      )
                    })()}
                  </div>
                  <h1 className="text-2xl font-bold mb-2">{selectedArticle.title}</h1>
                  <p className="text-sm text-muted-foreground">
                    조회 {selectedArticle.views}회 · {new Date(selectedArticle.created_at).toLocaleDateString('ko-KR')}
                  </p>
                </div>
                <div className="space-y-4">
                  {messages.map((msg, index) => {
                    const isQuestion = ['student', 'beginner', 'investor', 'user'].includes(msg.role)
                    return (
                      <div key={index} className={'flex gap-3 ' + (isQuestion ? 'justify-start' : 'justify-end')}>
                        {isQuestion && (
                          <div className="flex-shrink-0">
                            <div className="w-10 h-10 rounded-full flex items-center justify-center text-xl bg-purple-100 dark:bg-purple-900">
                              {msg.emoji}
                            </div>
                          </div>
                        )}
                        <div className="flex-1 max-w-[80%]">
                          <div className={'inline-block px-4 py-3 rounded-2xl ' + (isQuestion ? 'bg-purple-50 dark:bg-purple-950/30 rounded-tl-sm' : 'bg-blue-50 dark:bg-blue-950/30 rounded-tr-sm')}>
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                          </div>
                        </div>
                        {!isQuestion && (
                          <div className="flex-shrink-0">
                            <div className="w-10 h-10 rounded-full flex items-center justify-center text-xl bg-blue-100 dark:bg-blue-900">
                              {msg.emoji}
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            ) : (
              <div className="border rounded-lg bg-card p-12 text-center text-muted-foreground">
                좌측에서 강의를 선택해주세요
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
