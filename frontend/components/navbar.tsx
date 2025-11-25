'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'
import { ThemeToggle } from './theme-toggle'
import dynamic from 'next/dynamic'

const NotificationBell = dynamic(() => import('./NotificationBell'), { ssr: false })

interface NavbarProps {
  language?: 'ko' | 'en'
}

export function Navbar({ language: initialLanguage = 'ko' }: NavbarProps) {
  const pathname = usePathname()
  const [language, setLanguage] = useState<'ko' | 'en'>(initialLanguage)
  const [mounted, setMounted] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    // Close mobile menu on route change
    setMobileMenuOpen(false)
  }, [pathname])

  const t = {
    ko: {
      home: '홈',
      stocksList: '인기 종목',
      compare: '비교',
      predictionMap: '예측 맵',
      discovery: '신규 발굴',
      portfolio: '포트폴리오',
      education: '교육',
      accuracy: '예측 정확도',
      backtest: '백테스팅',
      models: 'AI 모델',
      scheduler: '스케줄러',
      guide: '사용 가이드',
      apiDocs: 'API 문서',
    },
    en: {
      home: 'Home',
      stocksList: 'Stocks',
      compare: 'Compare',
      predictionMap: 'Map',
      discovery: 'Discovery',
      portfolio: 'Portfolio',
      education: 'Education',
      accuracy: 'Accuracy',
      backtest: 'Backtest',
      models: 'AI Models',
      scheduler: 'Scheduler',
      guide: 'Guide',
      apiDocs: 'API Docs',
    },
  }

  const text = t[language]

  const navItems = [
    { href: '/', label: text.home },
    { href: '/stocks-list', label: text.stocksList },
    { href: '/prediction-map', label: text.predictionMap },
    { href: '/discovery', label: text.discovery },
    { href: '/portfolio', label: text.portfolio },
    { href: '/education', label: text.education },
    { href: '/accuracy', label: text.accuracy },
    { href: '/settings', label: '설정' },
    { href: '/guide', label: text.guide },
  ]

  // Prevent hydration mismatch by not rendering dynamic content until mounted
  if (!mounted) {
    return (
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-2">
              <span className="text-xl md:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Finance-Hub
              </span>
            </Link>
            <div className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                >
                  {item.label}
                </Link>
              ))}
            </div>
            <div className="w-[100px]" />
          </div>
        </div>
      </nav>
    )
  }

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-xl md:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Finance-Hub
            </span>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  pathname === item.href
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }`}
              >
                {item.label}
              </Link>
            ))}
            <a
              href="http://localhost:8001/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              {text.apiDocs}
            </a>
          </div>

          {/* Desktop Theme & Language Toggle */}
          <div className="hidden md:flex items-center gap-2">
            <NotificationBell />
            <ThemeToggle />
            <div className="flex gap-1 border rounded-md p-1">
              <button
                onClick={() => setLanguage('ko')}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  language === 'ko'
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                한국어
              </button>
              <button
                onClick={() => setLanguage('en')}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  language === 'en'
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                English
              </button>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-md hover:bg-accent transition-colors"
            aria-label="메뉴 열기"
          >
            {mobileMenuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-2 border-t">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`block px-4 py-3 rounded-md text-sm font-medium transition-colors ${
                  pathname === item.href
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }`}
              >
                {item.label}
              </Link>
            ))}
            <a
              href="http://localhost:8001/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="block px-4 py-3 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              {text.apiDocs}
            </a>

            {/* Mobile Theme & Language Controls */}
            <div className="flex items-center justify-between px-4 py-3">
              <span className="text-sm text-muted-foreground">테마</span>
              <ThemeToggle />
            </div>
            <div className="px-4 py-3">
              <div className="flex gap-2 border rounded-md p-1">
                <button
                  onClick={() => setLanguage('ko')}
                  className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
                    language === 'ko'
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  한국어
                </button>
                <button
                  onClick={() => setLanguage('en')}
                  className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
                    language === 'en'
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  English
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
