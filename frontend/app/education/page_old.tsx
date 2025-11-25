'use client'

import { useEffect, useState } from 'react'
import { Search, BookOpen, TrendingUp, BarChart3, ChevronDown, ChevronUp, Award, Plus, Filter, Edit, Trash2, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface EducationArticle {
  id: number
  title: string
  category: string
  level: 'beginner' | 'elementary' | 'intermediate' | 'advanced'
  content: string
  views: number
  created_at: string
}

interface ChatMessage {
  role: 'teacher' | 'student'
  content: string
  emoji?: string
}

interface ConversationTopic {
  id: number
  title: string
  level: 'beginner' | 'elementary' | 'intermediate' | 'advanced'
  conversation: ChatMessage[]
}

type FilterType = 'all' | 'completed' | 'incomplete'

export default function EducationPage() {
  const [articles, setArticles] = useState<EducationArticle[]>([])
  const [filteredArticles, setFilteredArticles] = useState<EducationArticle[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string>('전체')
  const [selectedLevel, setSelectedLevel] = useState<string>('전체')
  const [filterType, setFilterType] = useState<FilterType>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedArticle, setExpandedArticle] = useState<number | null>(null)
  const [viewedArticles, setViewedArticles] = useState<number[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingArticle, setEditingArticle] = useState<EducationArticle | null>(null)

  const categories = [
    { id: '전체', label: '전체', icon: BookOpen, emoji: '📚' },
    { id: '용어', label: '주식 용어', icon: BookOpen, emoji: '📖' },
    { id: '팁', label: '투자 팁', icon: TrendingUp, emoji: '💡' },
    { id: '분석기법', label: '분석 기법', icon: BarChart3, emoji: '📊' },
  ]

  const levels = [
    { id: '전체', label: '전체 레벨', emoji: '🎯' },
    { id: 'beginner', label: '초보', emoji: '🌱' },
    { id: 'elementary', label: '초급', emoji: '📘' },
    { id: 'intermediate', label: '중급', emoji: '📙' },
    { id: 'advanced', label: '고급', emoji: '📕' },
  ]

  const filterTypes = [
    { id: 'all' as FilterType, label: '전체 강의', emoji: '📚' },
    { id: 'completed' as FilterType, label: '학습 완료', emoji: '✅' },
    { id: 'incomplete' as FilterType, label: '미학습', emoji: '📝' },
  ]

  // 기본 대화형 교육 콘텐츠
  const defaultConversationTopics: Record<string, ConversationTopic[]> = {
    '용어': [
      {
        id: 1,
        title: '주식이 뭐예요?',
        level: 'beginner' as const,
        conversation: [
          { role: 'student', content: '선생님~ 주식이 정확히 뭐예요? 다들 주식 주식 하는데 저는 잘 모르겠어요 😅', emoji: '🤔' },
          { role: 'teacher', content: '아~ 그거? 쉽게 말하면 회사의 작은 조각을 사는 거야! 삼성전자 주식 1주를 샀다? 그럼 넌 삼성전자의 작은 주인이 되는 거지~', emoji: '👨‍🏫' },
          { role: 'student', content: '오오! 그럼 제가 삼성전자 주인이라구요? 멋진데요! 😮', emoji: '✨' },
          { role: 'teacher', content: '그러니까 말이야~ 회사가 돈을 많이 벌면 너도 이익을 보고, 망하면 손해를 볼 수도 있어. 운명공동체인 셈이지!', emoji: '💡' },
          { role: 'student', content: '아하! 그래서 좋은 회사 주식을 사야 하는구나! 이제 좀 알겠어요~', emoji: '😊' },
          { role: 'teacher', content: '딩동댕! 바로 그거야. 좋은 회사를 싸게 사는 게 진짜 중요한 거지. 워렌 버핏 할아버지도 항상 그렇게 말씀하시잖아?', emoji: '🎯' }
        ]
      },
      {
        id: 2,
        title: 'PER이 뭐죠? 자꾸 나오는데...',
        level: 'elementary' as const,
        conversation: [
          { role: 'student', content: 'PER이라는 게 뭐예요? 뉴스 볼 때마다 나오는데 도통 모르겠어요 😵', emoji: '🤷' },
          { role: 'teacher', content: '있잖아, PER은 Price Earning Ratio야. 한국말로는 "주가수익비율"인데... 솔직히 이것만으론 감이 안 오지?', emoji: '👨‍🏫' },
          { role: 'student', content: '네... 무슨 말인지 1도 모르겠어요 ㅠㅠ', emoji: '😭' },
          { role: 'teacher', content: '하하! 그럼 쉽게 설명해줄게. 햄버거 가게를 생각해봐. 1년에 100만원 버는 가게를 1000만원에 산다? 그럼 PER이 10배야! 10년 장사하면 본전 찾는 거지~', emoji: '🍔' },
          { role: 'student', content: '아~ 그럼 PER이 낮을수록 싸게 사는 거네요?', emoji: '💡' },
          { role: 'teacher', content: '정답! 근데 너무 낮으면 망할 가능성이 있다는 얘기일 수도 있어. 보통 10~15 정도면 적당하다고 보지. 업종마다 다르긴 해!', emoji: '✅' },
          { role: 'student', content: '오호~ 그럼 PER 10인 회사랑 30인 회사 중에 뭐가 나아요?', emoji: '🤔' },
          { role: 'teacher', content: '그러니까 말이지~ 무조건 낮다고 좋은 건 아니야! 30이어도 빠르게 성장하는 회사면 괜찮고, 10이어도 망해가는 회사면 위험하지. 다른 지표들도 같이 봐야 해!', emoji: '📊' }
        ]
      }
    ],
    '팁': [
      {
        id: 3,
        title: '처음 투자할 땐 얼마부터?',
        level: 'beginner' as const,
        conversation: [
          { role: 'student', content: '선생님~ 주식 시작하려는데 얼마부터 시작하는 게 좋아요? 100만원? 1000만원? 😰', emoji: '💰' },
          { role: 'teacher', content: '아~ 그거? 솔직히 말하면 말이지~ 잃어도 안 아까운 돈으로 시작해! 처음엔 수업료 낸다 생각하고 소액으로!', emoji: '👨‍🏫' },
          { role: 'student', content: '그럼... 10만원도 괜찮아요? 너무 적은가요? 🤔', emoji: '💭' },
          { role: 'teacher', content: '전혀! 10만원이면 딱 좋지! 요즘은 소액으로도 다양한 주식 살 수 있거든. 경험이 진짜 중요해. 책으로만 배우는 거랑 직접 해보는 거랑은 천지차이야!', emoji: '💪' },
          { role: 'student', content: '오! 그럼 저도 당장 시작할 수 있겠네요! 어떤 주식 살까요? 😊', emoji: '🎯' },
          { role: 'teacher', content: '잠깐잠깐! 여기서 진짜 중요한 거! 네가 잘 아는 회사, 사용하는 제품 만드는 회사부터 시작해봐. 삼성? 애플? 카카오? 매일 쓰잖아!', emoji: '✋' },
          { role: 'student', content: '아하! 제가 이해할 수 있는 회사부터요! 버핏 할아버지도 그렇게 하셨다며요?', emoji: '😮' },
          { role: 'teacher', content: '딱 맞아! "이해하지 못하는 것엔 투자하지 마라" - 버핏의 명언이지. 그리고 또! 한 종목에 몰빵은 절대 금물! 3~5개 정도 분산해!', emoji: '🎓' }
        ]
      },
      {
        id: 4,
        title: '손절은 언제 하나요?',
        level: 'intermediate' as const,
        conversation: [
          { role: 'student', content: '주식이 10% 떨어졌어요 ㅠㅠ 팔아야 하나요? 아님 기다려야 하나요? 너무 고민돼요...', emoji: '😢' },
          { role: 'teacher', content: '이거 진짜 중요한 질문이야! 있잖아, 정답은... 경우에 따라 다르다! (어이없지? ㅋㅋ)', emoji: '👨‍🏫' },
          { role: 'student', content: '에이~ 그런 답변은 저도 알아요! 구체적으로 알려주세요! 😤', emoji: '😠' },
          { role: 'teacher', content: '하하 미안미안! 자, 이렇게 생각해봐. ① 회사 펀더멘털(기본 체력)이 나빠졌나? ② 내가 산 이유가 틀렸나? 이 두 가지가 YES면 손절이야!', emoji: '📋' },
          { role: 'student', content: '펀더멘털이요...? 그게 뭔데요? 🤔', emoji: '❓' },
          { role: 'teacher', content: '그러니까 말이야~ 회사가 돈을 잘 벌고 있나? 빚은 없나? 망할 징조는 없나? 이런 기본적인 거! 이게 멀쩡하면 단기 하락은 오히려 기회야!', emoji: '💡' },
          { role: 'student', content: '아~ 그럼 회사는 멀쩡한데 주가만 떨어진 거면 오히려 살 기회? 😮', emoji: '✨' },
          { role: 'teacher', content: '정답! 워렌 버핏이 말했잖아? "남들이 두려워할 때 탐욕스럽게, 남들이 탐욕스러울 때 두려워하라!" 근데 초보자는 -20% 정도를 손절선으로 잡는 것도 방법이야.', emoji: '🎯' }
        ]
      }
    ],
    '분석기법': [
      {
        id: 5,
        title: '재무제표 보는 법',
        level: 'advanced' as const,
        conversation: [
          { role: 'student', content: '선생님, 재무제표가 너무 복잡해요... 어디서부터 봐야 할지 모르겠어요 😭', emoji: '📊' },
          { role: 'teacher', content: '재무제표? 어려워 보이지만 사실 성적표랑 비슷해! 회사의 성적표라고 생각하면 돼~', emoji: '👨‍🏫' },
          { role: 'student', content: '성적표요? 어떻게요?', emoji: '🤔' },
          { role: 'teacher', content: '성적표에 국영수 점수가 있듯이, 재무제표엔 3가지가 있어. ① 재무상태표(재산), ② 손익계산서(성적), ③ 현금흐름표(용돈)!', emoji: '📝' },
          { role: 'student', content: '오~ 그럼 이 3개만 보면 되는 거예요?', emoji: '💡' },
          { role: 'teacher', content: '맞아! 재무상태표는 회사가 뭘 가지고 있고 빚은 얼마인지, 손익계산서는 얼마나 벌고 썼는지, 현금흐름표는 실제 돈이 어떻게 움직였는지 보여줘!', emoji: '✅' },
          { role: 'student', content: '헐... 그럼 이걸 다 봐야 해요? 😰', emoji: '😨' },
          { role: 'teacher', content: '아니아니! 처음엔 핵심만 봐. 매출액이 늘고 있나? 영업이익은? 부채비율은 괜찮나? 이 3가지만 체크해도 80%는 파악돼!', emoji: '🎯' },
          { role: 'student', content: '오! 그 정도면 저도 할 수 있을 것 같아요! 😊', emoji: '✨' },
          { role: 'teacher', content: '그래그래! 버핏 할아버지도 "복잡한 기업은 투자하지 않는다"고 했어. 이해 안 되면 안 사는 게 최고야!', emoji: '👍' }
        ]
      }
    ]
  }

  useEffect(() => {
    loadArticles()
    loadViewHistory()
  }, [])

  useEffect(() => {
    filterArticles()
  }, [articles, selectedCategory, selectedLevel, filterType, searchQuery])

  const loadArticles = () => {
    // Load from localStorage
    const savedArticles = localStorage.getItem('education_articles')

    if (savedArticles) {
      const parsed = JSON.parse(savedArticles)
      setArticles(parsed)
      setLoading(false)
    } else {
      // Initialize with default topics
      const convertedArticles: EducationArticle[] = []
      let idCounter = 1

      Object.entries(defaultConversationTopics).forEach(([category, topics]) => {
        topics.forEach(topic => {
          convertedArticles.push({
            id: idCounter++,
            title: topic.title,
            category: category,
            level: topic.level,
            content: JSON.stringify(topic.conversation),
            views: 0,
            created_at: new Date().toISOString()
          })
        })
      })

      setArticles(convertedArticles)
      localStorage.setItem('education_articles', JSON.stringify(convertedArticles))
      setLoading(false)
    }
  }

  const saveArticles = (newArticles: EducationArticle[]) => {
    setArticles(newArticles)
    localStorage.setItem('education_articles', JSON.stringify(newArticles))
  }

  const loadViewHistory = () => {
    const history = localStorage.getItem('education_viewed')
    if (history) {
      setViewedArticles(JSON.parse(history))
    }
  }

  const saveViewHistory = (articleId: number) => {
    const newHistory = [...new Set([...viewedArticles, articleId])]
    setViewedArticles(newHistory)
    localStorage.setItem('education_viewed', JSON.stringify(newHistory))
  }

  const filterArticles = () => {
    let filtered = articles

    if (selectedCategory !== '전체') {
      filtered = filtered.filter(article => article.category === selectedCategory)
    }

    if (selectedLevel !== '전체') {
      filtered = filtered.filter(article => article.level === selectedLevel)
    }

    if (filterType === 'completed') {
      filtered = filtered.filter(article => viewedArticles.includes(article.id))
    } else if (filterType === 'incomplete') {
      filtered = filtered.filter(article => !viewedArticles.includes(article.id))
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(article =>
        article.title.toLowerCase().includes(query)
      )
    }

    setFilteredArticles(filtered)
  }

  const handleArticleClick = async (articleId: number) => {
    if (expandedArticle === articleId) {
      setExpandedArticle(null)
      return
    }

    setExpandedArticle(articleId)
    saveViewHistory(articleId)
  }

  const handleDeleteArticle = (articleId: number) => {
    if (!confirm('정말 이 강의를 삭제하시겠습니까?')) {
      return
    }

    const newArticles = articles.filter(a => a.id !== articleId)
    saveArticles(newArticles)

    // Remove from viewed history
    const newViewed = viewedArticles.filter(id => id !== articleId)
    setViewedArticles(newViewed)
    localStorage.setItem('education_viewed', JSON.stringify(newViewed))
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case '용어':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case '팁':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case '분석기법':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'elementary':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'intermediate':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
      case 'advanced':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  const getLevelLabel = (level: string) => {
    const levelMap: Record<string, string> = {
      beginner: '🌱 초보',
      elementary: '📘 초급',
      intermediate: '📙 중급',
      advanced: '📕 고급'
    }
    return levelMap[level] || level
  }

  const renderContentAsChat = (content: string) => {
    let messages: ChatMessage[] = []
    try {
      messages = JSON.parse(content)
    } catch (e) {
      console.error('Failed to parse conversation:', e)
      return null
    }

    return (
      <div className="space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${
              message.role === 'student' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'teacher' && (
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-xl">
                {message.emoji || '👨‍🏫'}
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'teacher'
                  ? 'bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 border border-blue-200 dark:border-blue-800'
                  : 'bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 border border-green-200 dark:border-green-800'
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
            </div>
            {message.role === 'student' && (
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center text-white text-xl">
                {message.emoji || '🤔'}
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }

  const completedCount = viewedArticles.filter(id => articles.some(a => a.id === id)).length
  const totalCount = articles.length
  const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 dark:from-indigo-950 dark:via-purple-950 dark:to-pink-950">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <div className="text-6xl">📚</div>
              <div>
                <h1 className="text-4xl font-bold mb-2">투자 교육 센터</h1>
                <p className="text-lg text-muted-foreground">
                  대화형 학습으로 쉽고 재미있게 투자 공부하기!
                </p>
              </div>
            </div>

            <button
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
              onClick={() => setShowCreateModal(true)}
            >
              <Plus className="w-5 h-5" />
              강의 생성
            </button>
          </div>

          {/* Achievement badges */}
          <div className="flex gap-2 mt-4">
            {completedCount >= 3 && (
              <div className="flex items-center gap-2 px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 rounded-full text-sm font-semibold">
                <Award className="w-4 h-4 text-yellow-600" />
                <span>학습 초보 탈출! 🎉</span>
              </div>
            )}
            {completedCount >= totalCount && totalCount > 0 && (
              <div className="flex items-center gap-2 px-3 py-1 bg-purple-100 dark:bg-purple-900/30 rounded-full text-sm font-semibold">
                <Award className="w-4 h-4 text-purple-600" />
                <span>완벽 마스터! 🏆</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Search and Filter */}
        <div className="mb-8 space-y-4">
          {/* Search Bar */}
          <div className="relative max-w-2xl">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="🔍 어떤 걸 배우고 싶으세요?"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
            />
          </div>

          {/* Filter Type Buttons */}
          <div className="flex items-center gap-2 mb-2">
            <Filter className="w-5 h-5 text-muted-foreground" />
            <span className="text-sm font-semibold text-muted-foreground">필터:</span>
            {filterTypes.map((type) => (
              <button
                key={type.id}
                onClick={() => setFilterType(type.id)}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  filterType === type.id
                    ? 'bg-primary text-primary-foreground shadow'
                    : 'bg-muted hover:bg-muted/80'
                }`}
              >
                <span>{type.emoji}</span>
                <span>{type.label}</span>
              </button>
            ))}
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all transform hover:scale-105 ${
                  selectedCategory === category.id
                    ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                    : 'bg-muted hover:bg-muted/80'
                }`}
              >
                <span className="text-xl">{category.emoji}</span>
                <span>{category.label}</span>
              </button>
            ))}
          </div>

          {/* Level Filter */}
          <div className="flex flex-wrap gap-2">
            {levels.map((level) => (
              <button
                key={level.id}
                onClick={() => setSelectedLevel(level.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${
                  selectedLevel === level.id
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
                    : 'bg-muted hover:bg-muted/80'
                }`}
              >
                <span>{level.emoji}</span>
                <span>{level.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="p-6 border-2 border-blue-200 dark:border-blue-800 rounded-xl bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30 shadow-md">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="text-3xl">📚</div>
                <span className="text-sm font-semibold text-muted-foreground">전체 강의</span>
              </div>
            </div>
            <p className="text-3xl font-bold text-blue-600">{totalCount}개</p>
            <p className="text-xs text-muted-foreground mt-1">풍부한 학습 자료가 준비되어 있어요!</p>
          </div>

          <div className="p-6 border-2 border-green-200 dark:border-green-800 rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 shadow-md">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="text-3xl">✅</div>
                <span className="text-sm font-semibold text-muted-foreground">학습 완료</span>
              </div>
            </div>
            <p className="text-3xl font-bold text-green-600">{completedCount}개</p>
            <p className="text-xs text-muted-foreground mt-1">대단해요! 계속 배워나가세요!</p>
          </div>

          <div className="p-6 border-2 border-purple-200 dark:border-purple-800 rounded-xl bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30 shadow-md">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="text-3xl">📈</div>
                <span className="text-sm font-semibold text-muted-foreground">학습 진도</span>
              </div>
            </div>
            <p className="text-3xl font-bold text-purple-600">{progressPercent}%</p>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
              <div
                className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                style={{ width: `${Math.min(progressPercent, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Articles List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-bounce text-6xl mb-4">📖</div>
            <p className="text-muted-foreground">재미있는 학습 자료를 불러오는 중...</p>
          </div>
        ) : filteredArticles.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed rounded-xl bg-muted/20">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-xl font-semibold mb-2">찾으시는 자료가 없어요</p>
            <p className="text-muted-foreground">다른 키워드나 카테고리를 시도해보세요!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredArticles.map((article) => {
              const isExpanded = expandedArticle === article.id
              const isViewed = viewedArticles.includes(article.id)

              return (
                <div
                  key={article.id}
                  className={`border-2 rounded-xl overflow-hidden transition-all ${
                    isExpanded
                      ? 'shadow-2xl border-primary lg:col-span-2'
                      : 'hover:shadow-lg border-gray-200 dark:border-gray-800'
                  }`}
                >
                  <button
                    onClick={() => handleArticleClick(article.id)}
                    className="w-full p-6 text-left bg-card hover:bg-accent/30 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`px-2 py-1 rounded-md text-xs font-semibold ${getCategoryColor(article.category)}`}>
                            {article.category}
                          </span>
                          <span className={`px-2 py-1 rounded-md text-xs font-semibold ${getLevelColor(article.level)}`}>
                            {getLevelLabel(article.level)}
                          </span>
                          {isViewed && (
                            <span className="px-2 py-1 rounded-md text-xs font-semibold bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                              ✅ 완료
                            </span>
                          )}
                        </div>
                        <h3 className="text-xl font-bold mb-2">{article.title}</h3>
                      </div>
                      <div className="ml-4 flex items-center gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setEditingArticle(article)
                          }}
                          className="p-2 hover:bg-blue-100 dark:hover:bg-blue-900 rounded-lg transition-colors"
                          title="편집"
                        >
                          <Edit className="w-4 h-4 text-blue-600" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteArticle(article.id)
                          }}
                          className="p-2 hover:bg-red-100 dark:hover:bg-red-900 rounded-lg transition-colors"
                          title="삭제"
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </button>
                        {isExpanded ? (
                          <ChevronUp className="w-6 h-6 text-muted-foreground" />
                        ) : (
                          <ChevronDown className="w-6 h-6 text-muted-foreground" />
                        )}
                      </div>
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="px-6 pb-6 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50">
                      <div className="border-t pt-6">
                        {renderContentAsChat(article.content)}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {(showCreateModal || editingArticle) && (
        <LectureModal
          article={editingArticle}
          onClose={() => {
            setShowCreateModal(false)
            setEditingArticle(null)
          }}
          onSave={(article) => {
            if (editingArticle) {
              // Edit existing
              const newArticles = articles.map(a => a.id === article.id ? article : a)
              saveArticles(newArticles)
            } else {
              // Create new
              const newArticles = [...articles, article]
              saveArticles(newArticles)
            }
            setShowCreateModal(false)
            setEditingArticle(null)
          }}
          existingIds={articles.map(a => a.id)}
        />
      )}
    </main>
  )
}

// Lecture Modal Component
function LectureModal({
  article,
  onClose,
  onSave,
  existingIds
}: {
  article: EducationArticle | null
  onClose: () => void
  onSave: (article: EducationArticle) => void
  existingIds: number[]
}) {
  const [title, setTitle] = useState(article?.title || '')
  const [category, setCategory] = useState(article?.category || '용어')
  const [level, setLevel] = useState<'beginner' | 'elementary' | 'intermediate' | 'advanced'>(
    article?.level || 'beginner'
  )
  const [messages, setMessages] = useState<ChatMessage[]>(
    article ? JSON.parse(article.content) : [
      { role: 'student', content: '', emoji: '🤔' },
      { role: 'teacher', content: '', emoji: '👨‍🏫' }
    ]
  )

  const addMessage = (role: 'teacher' | 'student') => {
    setMessages([...messages, { role, content: '', emoji: role === 'teacher' ? '👨‍🏫' : '🤔' }])
  }

  const updateMessage = (index: number, field: keyof ChatMessage, value: string) => {
    const newMessages = [...messages]
    newMessages[index] = { ...newMessages[index], [field]: value }
    setMessages(newMessages)
  }

  const removeMessage = (index: number) => {
    setMessages(messages.filter((_, i) => i !== index))
  }

  const handleSave = () => {
    if (!title.trim()) {
      alert('제목을 입력해주세요')
      return
    }

    const validMessages = messages.filter(m => m.content.trim())
    if (validMessages.length < 2) {
      alert('최소 2개 이상의 메시지를 입력해주세요')
      return
    }

    const newArticle: EducationArticle = {
      id: article?.id || Math.max(0, ...existingIds) + 1,
      title,
      category,
      level,
      content: JSON.stringify(validMessages),
      views: article?.views || 0,
      created_at: article?.created_at || new Date().toISOString()
    }

    onSave(newArticle)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white dark:bg-gray-900 border-b p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold">
            {article ? '강의 편집' : '새 강의 만들기'}
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Title */}
          <div>
            <label className="block text-sm font-semibold mb-2">강의 제목</label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="예: 주식이 뭐예요?"
              className="w-full"
            />
          </div>

          {/* Category and Level */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">카테고리</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg bg-background"
              >
                <option value="용어">주식 용어</option>
                <option value="팁">투자 팁</option>
                <option value="분석기법">분석 기법</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">레벨</label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value as any)}
                className="w-full px-3 py-2 border rounded-lg bg-background"
              >
                <option value="beginner">🌱 초보</option>
                <option value="elementary">📘 초급</option>
                <option value="intermediate">📙 중급</option>
                <option value="advanced">📕 고급</option>
              </select>
            </div>
          </div>

          {/* Messages */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <label className="block text-sm font-semibold">대화 내용</label>
              <div className="flex gap-2">
                <Button onClick={() => addMessage('student')} size="sm" variant="outline">
                  + 학생 메시지
                </Button>
                <Button onClick={() => addMessage('teacher')} size="sm" variant="outline">
                  + 선생님 메시지
                </Button>
              </div>
            </div>

            <div className="space-y-4">
              {messages.map((message, index) => (
                <div key={index} className="p-4 border rounded-lg bg-muted/30">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        message.role === 'teacher' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {message.role === 'teacher' ? '👨‍🏫 선생님' : '🤔 학생'}
                      </span>
                      <Input
                        value={message.emoji}
                        onChange={(e) => updateMessage(index, 'emoji', e.target.value)}
                        placeholder="이모지"
                        className="w-20"
                      />
                    </div>
                    <button
                      onClick={() => removeMessage(index)}
                      className="text-red-600 hover:bg-red-100 p-2 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <textarea
                    value={message.content}
                    onChange={(e) => updateMessage(index, 'content', e.target.value)}
                    placeholder="대화 내용을 입력하세요..."
                    className="w-full px-3 py-2 border rounded-lg bg-background min-h-[100px]"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button onClick={onClose} variant="outline">
              취소
            </Button>
            <Button onClick={handleSave}>
              {article ? '수정 완료' : '강의 생성'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
