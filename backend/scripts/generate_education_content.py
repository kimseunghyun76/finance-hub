"""Generate improved education content with diverse scenarios"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.education import EducationArticle
from app.models.portfolio_snapshot import PortfolioSnapshot  # Import to avoid SQLAlchemy registry error
import json

def create_article(db, title, level, category, messages):
    """Create an education article"""
    article = EducationArticle(
        title=title,
        level=level,
        category=category,
        content=json.dumps(messages, ensure_ascii=False),
        views=0
    )
    db.add(article)
    db.commit()
    print(f"✅ Created: {title} ({level} - {category}) - {len(messages)} messages")

def main():
    db = SessionLocal()

    # Beginner level articles (5 messages each)
    beginner_articles = [
        {
            "title": "주식이란 무엇인가요?",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "student", "content": "주식이 뭔가요?", "emoji": "🤔"},
                {"role": "teacher", "content": "주식은 회사의 일부를 소유하는 권리예요. 회사가 발행한 '소유권 증서'라고 생각하면 됩니다.", "emoji": "👨‍🏫"},
                {"role": "student", "content": "그럼 저도 회사 주인이 되는 건가요?", "emoji": "😮"},
                {"role": "teacher", "content": "네, 맞아요! 삼성전자 주식을 사면 삼성전자의 부분 소유자가 되는 거예요. 회사가 잘되면 주가도 오르고, 배당금도 받을 수 있습니다.", "emoji": "👨‍🏫"},
                {"role": "student", "content": "와! 그럼 회사 결정에도 참여할 수 있나요?", "emoji": "✨"},
                {"role": "teacher", "content": "원칙적으로 가능합니다. 주주총회에서 의결권을 행사할 수 있어요. 하지만 개인 투자자가 가진 주식은 전체의 극히 일부라서 영향력은 제한적입니다.", "emoji": "👨‍🏫"}
            ]
        },
        {
            "title": "배당금은 어떻게 받나요?",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "investor", "content": "친구가 배당금 받았다는데 저도 받을 수 있나요?", "emoji": "💭"},
                {"role": "expert", "content": "배당주에 투자하면 가능합니다. 배당금은 회사가 번 이익을 주주들에게 나눠주는 돈이에요.", "emoji": "💼"},
                {"role": "investor", "content": "모든 주식이 배당금을 주나요?", "emoji": "🤔"},
                {"role": "expert", "content": "아니요. 회사마다 다릅니다. 안정적인 대기업은 꾸준히 배당을 주지만, 성장하는 기업은 돈을 재투자해서 배당을 안 주기도 해요.", "emoji": "💼"},
                {"role": "investor", "content": "배당금은 언제 받나요?", "emoji": "📅"},
                {"role": "expert", "content": "보통 연 1-4회 지급됩니다. 배당기준일에 주식을 보유하고 있어야 받을 수 있어요. 증권사 계좌로 자동 입금됩니다.", "emoji": "💼"}
            ]
        }
    ]

    # Elementary level articles (10 messages each)
    elementary_articles = [
        {
            "title": "시가총액으로 회사 규모 파악하기",
            "level": "elementary",
            "category": "용어",
            "messages": [
                {"role": "beginner", "content": "뉴스에서 '시가총액 1위'라는 말을 들었는데 뭔가요?", "emoji": "📺"},
                {"role": "analyst", "content": "시가총액은 회사의 전체 가치를 나타내요. 주가 × 발행 주식 수로 계산합니다.", "emoji": "📊"},
                {"role": "beginner", "content": "예를 들어 설명해주시겠어요?", "emoji": "🤔"},
                {"role": "analyst", "content": "삼성전자 주가가 7만원이고 발행 주식이 60억주라면, 시가총액은 420조원입니다. 이게 회사의 시장 가치예요.", "emoji": "📊"},
                {"role": "beginner", "content": "시가총액이 크면 무조건 좋은 건가요?", "emoji": "💭"},
                {"role": "analyst", "content": "꼭 그렇지는 않아요. 시가총액이 크면 안정적이지만 성장률은 낮을 수 있습니다. 작은 회사는 리스크가 크지만 성장 가능성이 높죠.", "emoji": "📊"},
                {"role": "investor", "content": "그럼 어떤 걸 선택해야 하나요?", "emoji": "🎯"},
                {"role": "analyst", "content": "투자 성향에 따라 다릅니다. 안정성을 원하면 대형주(시가총액 10조 이상), 성장성을 원하면 중소형주를 고려하세요.", "emoji": "📊"},
                {"role": "investor", "content": "대형주와 중소형주를 섞어서 투자하면 어떨까요?", "emoji": "💡"},
                {"role": "analyst", "content": "좋은 전략입니다! 대형주로 안정성을 확보하고, 중소형주로 수익률을 높이는 '코어-위성 전략'이라고 합니다.", "emoji": "📊"}
            ]
        },
        {
            "title": "PER과 PBR로 저평가 주식 찾기",
            "level": "elementary",
            "category": "분석기법",
            "messages": [
                {"role": "trader", "content": "주식이 비싼지 싼지 어떻게 알 수 있나요?", "emoji": "💰"},
                {"role": "expert", "content": "PER과 PBR이라는 지표로 판단할 수 있습니다. 이 두 가지만 알아도 저평가 주식을 찾을 수 있어요.", "emoji": "🎓"},
                {"role": "trader", "content": "PER이 뭔가요?", "emoji": "🤔"},
                {"role": "expert", "content": "PER은 주가수익비율입니다. 회사가 1년에 버는 돈에 비해 주가가 얼마나 높은지를 보여줘요. PER 10이면 10년 치 이익과 주가가 같다는 뜻입니다.", "emoji": "🎓"},
                {"role": "trader", "content": "PER이 낮으면 저평가인가요?", "emoji": "📉"},
                {"role": "expert", "content": "일반적으로는 그렇습니다. 하지만 업종별로 평균 PER이 다르니 비교가 필요해요. IT는 20-30, 금융은 5-10 정도가 평균입니다.", "emoji": "🎓"},
                {"role": "trader", "content": "그럼 PBR은요?", "emoji": "📊"},
                {"role": "expert", "content": "PBR은 주가순자산비율입니다. 회사가 가진 자산에 비해 주가가 얼마나 높은지 보여줘요. PBR 1 미만이면 청산가치보다 싸다는 뜻입니다.", "emoji": "🎓"},
                {"role": "investor", "content": "그럼 PER과 PBR 둘 다 낮은 주식을 사면 되나요?", "emoji": "🎯"},
                {"role": "expert", "content": "좋은 출발점이지만, 왜 낮은지도 확인해야 합니다. 실적이 나빠서 낮은 건지, 시장이 저평가한 건지 분석이 필요해요.", "emoji": "🎓"},
                {"role": "investor", "content": "구체적으로 어떻게 확인하나요?", "emoji": "🔍"},
                {"role": "expert", "content": "최근 3년 매출과 영업이익 추이를 보세요. 꾸준히 증가하는데 PER/PBR이 낮다면 저평가된 가치주일 가능성이 높습니다.", "emoji": "🎓"}
            ]
        }
    ]

    # Intermediate level articles (20 messages each)
    intermediate_articles = [
        {
            "title": "재무제표로 기업의 진짜 실력 파악하기",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "investor", "content": "요즘 재무제표 공부를 시작했는데, 어디서부터 봐야 할지 모르겠어요.", "emoji": "📚"},
                {"role": "analyst", "content": "재무제표는 크게 3가지예요. 재무상태표(자산), 손익계산서(수익), 현금흐름표(현금)입니다. 각각의 역할이 달라요.", "emoji": "📊"},
                {"role": "investor", "content": "가장 중요한 게 뭔가요?", "emoji": "🎯"},
                {"role": "analyst", "content": "손익계산서부터 보세요. 매출액과 영업이익이 회사의 수익 창출 능력을 보여줍니다.", "emoji": "📊"},
                {"role": "trader", "content": "매출액이 높으면 좋은 회사인가요?", "emoji": "💭"},
                {"role": "analyst", "content": "매출도 중요하지만 '영업이익률'이 더 중요합니다. 매출 100억에 이익 1억인 회사보다, 매출 50억에 이익 10억인 회사가 더 효율적이에요.", "emoji": "📊"},
                {"role": "investor", "content": "영업이익률은 어떻게 계산하나요?", "emoji": "🧮"},
                {"role": "analyst", "content": "(영업이익 ÷ 매출액) × 100 입니다. 10% 이상이면 우량, 20% 이상이면 매우 우수한 편입니다.", "emoji": "📊"},
                {"role": "trader", "content": "재무상태표에서는 뭘 봐야 하나요?", "emoji": "📋"},
                {"role": "analyst", "content": "부채비율을 확인하세요. (부채 ÷ 자본) × 100으로 계산합니다. 100% 이하가 안정적, 200% 이상이면 재무 리스크가 큽니다.", "emoji": "📊"},
                {"role": "investor", "content": "부채가 무조건 나쁜 건가요?", "emoji": "🤔"},
                {"role": "analyst", "content": "아닙니다. 저금리 시기에 부채로 사업을 확장하면 오히려 수익이 커질 수 있어요. 중요한 건 '이자보상배율'입니다.", "emoji": "📊"},
                {"role": "trader", "content": "이자보상배율이 뭔가요?", "emoji": "❓"},
                {"role": "analyst", "content": "(영업이익 ÷ 이자비용)입니다. 3배 이상이면 안전하고, 1배 미만이면 위험합니다. 이익으로 이자를 감당 못하는 거죠.", "emoji": "📊"},
                {"role": "investor", "content": "현금흐름표는 왜 중요한가요?", "emoji": "💰"},
                {"role": "analyst", "content": "회계상 이익과 실제 현금은 다릅니다. 매출이 있어도 돈을 못 받으면 흑자도산할 수 있어요. '영업활동 현금흐름'이 (+)인지 확인하세요.", "emoji": "📊"},
                {"role": "trader", "content": "구체적인 사례를 들어주실 수 있나요?", "emoji": "📖"},
                {"role": "analyst", "content": "A사는 매출 1000억, 순이익 100억이지만 현금흐름이 -50억이라면 위험합니다. 외상 매출이 많거나 재고가 쌓인 거예요.", "emoji": "📊"},
                {"role": "investor", "content": "그럼 어떤 회사가 좋은 건가요?", "emoji": "⭐"},
                {"role": "analyst", "content": "1) 매출과 영업이익 꾸준히 증가 2) 영업이익률 10% 이상 3) 부채비율 100% 이하 4) 영업 현금흐름 (+) 이 4가지를 충족하는 회사가 우량 기업입니다.", "emoji": "📊"},
                {"role": "trader", "content": "이런 정보는 어디서 볼 수 있나요?", "emoji": "🔍"},
                {"role": "analyst", "content": "전자공시시스템(DART)에서 무료로 확인할 수 있어요. 분기보고서, 사업보고서를 검색하면 됩니다.", "emoji": "📊"},
                {"role": "investor", "content": "감사합니다! 실전에 바로 적용해보겠습니다.", "emoji": "💪"}
            ]
        },
        {
            "title": "기술적 분석: 차트로 매매 타이밍 잡기",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "trader", "content": "언제 사고 팔아야 할지 모르겠어요. 차트를 봐도 잘 모르겠고요.", "emoji": "😵"},
                {"role": "expert", "content": "기술적 분석을 배우면 도움이 됩니다. 주가 차트와 거래량 패턴으로 매매 시점을 찾는 방법이에요.", "emoji": "📈"},
                {"role": "trader", "content": "가장 기본적인 지표가 뭔가요?", "emoji": "🎯"},
                {"role": "expert", "content": "이동평균선입니다. 5일, 20일, 60일, 120일선을 많이 봅니다. 주가가 20일선 위에 있으면 단기 상승 추세예요.", "emoji": "📈"},
                {"role": "beginner", "content": "골든크로스가 뭔가요?", "emoji": "✨"},
                {"role": "expert", "content": "단기선(20일)이 장기선(60일)을 아래에서 위로 뚫고 올라가는 거예요. 상승 신호로 봅니다. 반대는 데드크로스라고 합니다.", "emoji": "📈"},
                {"role": "trader", "content": "이동평균선만 보면 되나요?", "emoji": "🤔"},
                {"role": "expert", "content": "거래량도 함께 봐야 합니다. 주가가 오르는데 거래량도 증가하면 진짜 상승이에요. 거래량 없이 오르면 곧 떨어질 수 있습니다.", "emoji": "📈"},
                {"role": "investor", "content": "RSI라는 것도 들었는데 뭔가요?", "emoji": "📊"},
                {"role": "expert", "content": "RSI는 과매수/과매도를 판단하는 지표예요. 0-100 사이 값인데, 70 이상이면 과열(매도 고려), 30 이하면 과매도(매수 고려)입니다.", "emoji": "📈"},
                {"role": "trader", "content": "그럼 RSI 30 이하에서 무조건 사면 되나요?", "emoji": "💭"},
                {"role": "expert", "content": "아니요. RSI는 보조지표일 뿐입니다. 하락 추세에서 RSI 30은 '더 떨어질 수 있다'는 신호일 수도 있어요. 추세와 함께 봐야 합니다.", "emoji": "📈"},
                {"role": "investor", "content": "그럼 어떻게 조합해서 보나요?", "emoji": "🔍"},
                {"role": "expert", "content": "예를 들어 1) 20일선 상향돌파 2) 거래량 급증 3) RSI 50 돌파 이 3가지가 동시에 나타나면 강한 매수 신호입니다.", "emoji": "📈"},
                {"role": "trader", "content": "지지선과 저항선은 뭔가요?", "emoji": "📉"},
                {"role": "expert", "content": "과거 여러 번 반등한 가격대가 '지지선', 여러 번 막힌 가격대가 '저항선'입니다. 지지선에서 매수, 저항선 돌파 시 추가 매수를 고려합니다.", "emoji": "📈"},
                {"role": "investor", "content": "저항선을 못 뚫으면 어떻게 하나요?", "emoji": "😰"},
                {"role": "expert", "content": "저항선에서 3번 이상 막히면 하락할 확률이 높습니다. 손절하거나 비중을 줄이는 게 좋아요.", "emoji": "📈"},
                {"role": "trader", "content": "캔들 패턴도 중요한가요?", "emoji": "🕯️"},
                {"role": "expert", "content": "네, 중요합니다. '망치형(하락 후 긴 아래꼬리)', '십자형(매물대기)', '장대양봉(강한 매수)' 같은 패턴으로 시장 심리를 읽을 수 있어요.", "emoji": "📈"},
                {"role": "investor", "content": "기술적 분석만으로 수익을 낼 수 있나요?", "emoji": "💰"},
                {"role": "expert", "content": "기술적 분석은 '언제' 사고팔지 알려주지만, '무엇을' 살지는 기본적 분석이 필요합니다. 둘을 조합하는 게 가장 좋아요.", "emoji": "📈"},
                {"role": "trader", "content": "감사합니다! 실전에서 연습해보겠습니다.", "emoji": "🙏"}
            ]
        }
    ]

    # Advanced level articles (35+ messages each)
    advanced_articles = [
        {
            "title": "포트폴리오 리밸런싱 완벽 가이드",
            "level": "advanced",
            "category": "팁",
            "messages": [
                {"role": "professional", "content": "5년째 투자 중인데, 포트폴리오가 처음 계획과 많이 달라졌어요. 리밸런싱을 해야 할까요?", "emoji": "💼"},
                {"role": "strategist", "content": "네, 정기적인 리밸런싱이 필요합니다. 주가 변동으로 자산 배분 비율이 틀어지면 위험도가 높아질 수 있어요.", "emoji": "🎯"},
                {"role": "professional", "content": "리밸런싱이 정확히 뭔가요?", "emoji": "🤔"},
                {"role": "strategist", "content": "처음 세운 자산 배분 비율로 되돌리는 거예요. 예를 들어 주식 60%, 채권 40%로 시작했는데, 주가 상승으로 70:30이 됐다면 주식 일부를 팔아 채권을 사는 겁니다.", "emoji": "🎯"},
                {"role": "investor", "content": "왜 굳이 오른 주식을 팔아야 하나요?", "emoji": "😕"},
                {"role": "strategist", "content": "고평가된 자산을 팔고 저평가된 자산을 사는 '역발상 투자'의 원리입니다. 장기적으로 수익률을 높이고 위험을 관리할 수 있어요.", "emoji": "🎯"},
                {"role": "professional", "content": "언제 리밸런싱을 해야 하나요?", "emoji": "📅"},
                {"role": "strategist", "content": "크게 2가지 방법이 있습니다. 1) 시간 기준: 분기별, 반기별 2) 비율 기준: 목표에서 5-10% 벗어났을 때. 저는 반기별 + 10% 벗어나면 즉시 방식을 추천합니다.", "emoji": "🎯"},
                {"role": "investor", "content": "구체적인 예시를 들어주실 수 있나요?", "emoji": "📊"},
                {"role": "strategist", "content": "1억 포트폴리오를 삼성전자 40%, NAVER 30%, 채권 30%로 구성했다고 합시다. 1년 후 삼성전자가 50% 올라 7000만원, NAVER는 그대로 3000만원이 됐어요.", "emoji": "🎯"},
                {"role": "professional", "content": "그럼 어떻게 하나요?", "emoji": "🔄"},
                {"role": "strategist", "content": "총 자산이 1.3억이 됐으니, 목표 비율로 다시 계산하면 삼성 5200만원, NAVER 3900만원, 채권 3900만원이 돼야 합니다. 삼성 1800만원어치를 팔아 NAVER와 채권을 사는 거죠.", "emoji": "🎯"},
                {"role": "investor", "content": "세금이나 수수료가 아깝지 않나요?", "emoji": "💸"},
                {"role": "strategist", "content": "맞아요. 그래서 ISA 계좌나 연금저축 같은 비과세 계좌를 활용하면 좋습니다. 또는 신규 매수 자금으로 비중을 조절하는 방법도 있어요.", "emoji": "🎯"},
                {"role": "professional", "content": "신규 자금으로 조절한다는 게 뭔가요?", "emoji": "🤔"},
                {"role": "strategist", "content": "매달 100만원씩 투자한다면, 비중이 낮은 종목만 집중 매수하는 겁니다. 위 예시에서는 NAVER와 채권만 사서 비율을 맞추는 거죠. 수수료를 아낄 수 있어요.", "emoji": "🎯"},
                {"role": "trader", "content": "리밸런싱의 실제 효과가 궁금해요.", "emoji": "📈"},
                {"role": "strategist", "content": "역사적 데이터를 보면, S&P500 60% + 채권 40% 포트폴리오를 매년 리밸런싱하면 안 한 것보다 연 0.5-1%p 더 높은 수익률을 보였어요. 20년이면 큰 차이입니다.", "emoji": "🎯"},
                {"role": "investor", "content": "리밸런싱 할 때 주의할 점이 있나요?", "emoji": "⚠️"},
                {"role": "strategist", "content": "3가지 주의사항이 있습니다. 1) 단기 변동에 너무 자주 반응 금지 2) 시장 타이밍을 노리지 말 것 3) 감정에 휘둘리지 말 것. 기계적으로 실행하는 게 중요해요.", "emoji": "🎯"},
                {"role": "professional", "content": "종목별로도 리밸런싱이 필요한가요?", "emoji": "📊"},
                {"role": "strategist", "content": "네, 매우 중요합니다. 특정 종목이 너무 커지면 포트폴리오 위험이 집중돼요. 한 종목이 20%를 넘지 않도록 관리하세요.", "emoji": "🎯"},
                {"role": "investor", "content": "코스피, 나스닥 같은 지역별로는요?", "emoji": "🌍"},
                {"role": "strategist", "content": "지역 분산도 중요합니다. 한국 50%, 미국 30%, 신흥국 20% 같은 비율을 정하고 유지하세요. 한 지역에 집중되면 특정 국가 리스크에 노출됩니다.", "emoji": "🎯"},
                {"role": "professional", "content": "업종별로도 나눠야 하나요?", "emoji": "🏭"},
                {"role": "strategist", "content": "당연합니다. IT 70%는 위험합니다. IT 30%, 금융 20%, 소비재 20%, 헬스케어 15%, 에너지 15% 처럼 분산하세요. 한 업종이 무너져도 전체에 미치는 영향을 줄일 수 있어요.", "emoji": "🎯"},
                {"role": "trader", "content": "리밸런싱 주기는 짧을수록 좋나요?", "emoji": "⏰"},
                {"role": "strategist", "content": "아니요. 너무 자주 하면 수수료만 많이 나갑니다. 연구 결과 1년에 1-2회가 최적입니다. 단, 급격한 시장 변동(±30% 이상) 시에는 추가로 하는 게 좋아요.", "emoji": "🎯"},
                {"role": "investor", "content": "약세장에서는 어떻게 하나요?", "emoji": "📉"},
                {"role": "strategist", "content": "오히려 기회입니다. 주식 비중이 줄어들었을 때 '싸게 더 사는' 효과가 있어요. 2008년, 2020년처럼 대폭락 후 리밸런싱한 사람들이 큰 수익을 냈습니다.", "emoji": "🎯"},
                {"role": "professional", "content": "구체적인 리밸런싱 계산 방법을 알려주세요.", "emoji": "🧮"},
                {"role": "strategist", "content": "1) 현재 자산 평가 2) 목표 비율 재설정 3) 차이 계산 4) 매도/매수 주문 실행. 엑셀로 정리하면 쉬워요. '현재 비중'과 '목표 비중'을 비교하는 표를 만드세요.", "emoji": "🎯"},
                {"role": "trader", "content": "초보자도 할 수 있나요?", "emoji": "🌱"},
                {"role": "strategist", "content": "물론입니다! ETF 3-4개로 시작하면 쉬워요. SPY(미국 대형주) + QQQ(나스닥) + AGG(채권) 조합이면 충분합니다. 반기마다 비율만 맞춰주세요.", "emoji": "🎯"},
                {"role": "investor", "content": "리밸런싱 자동화 도구가 있나요?", "emoji": "🤖"},
                {"role": "strategist", "content": "로보어드바이저가 자동으로 해줍니다. 하지만 수수료가 있어요. 직접 엑셀로 관리하면 무료이고, 투자 원리도 배울 수 있어서 추천합니다.", "emoji": "🎯"},
                {"role": "professional", "content": "리밸런싱 후 기록을 남겨야 하나요?", "emoji": "📝"},
                {"role": "strategist", "content": "꼭 필요합니다. 리밸런싱 날짜, 자산 비율, 수익률을 기록하세요. 1년 후 비교하면 전략의 효과를 검증할 수 있고, 세금 신고 시에도 유용합니다.", "emoji": "🎯"},
                {"role": "investor", "content": "마지막으로 가장 중요한 팁 하나만 주세요!", "emoji": "💡"},
                {"role": "strategist", "content": "감정을 배제하세요. '이 주식은 더 오를 것 같아'라는 생각을 버리고, 정한 비율대로 기계적으로 실행하는 게 장기 성공의 비결입니다. 규칙을 지키는 사람이 이깁니다.", "emoji": "🎯"},
                {"role": "professional", "content": "완벽하게 이해했습니다. 바로 실천하겠습니다!", "emoji": "💪"},
                {"role": "strategist", "content": "화이팅! 1년 후 리밸런싱 결과를 공유해주세요. 분명 포트폴리오가 더 안정적이고 수익도 좋아질 겁니다.", "emoji": "🎯"}
            ]
        }
    ]

    all_articles = beginner_articles + elementary_articles + intermediate_articles + advanced_articles

    print(f"\n📚 Creating {len(all_articles)} enhanced education articles...\n")

    for article in all_articles:
        create_article(
            db,
            article["title"],
            article["level"],
            article["category"],
            article["messages"]
        )

    db.close()
    print(f"\n✨ Successfully created {len(all_articles)} articles!")
    print("\n레벨별 분포:")
    print(f"  🌱 Beginner: {len(beginner_articles)}개 (평균 {sum(len(a['messages']) for a in beginner_articles)//len(beginner_articles)}개 메시지)")
    print(f"  📘 Elementary: {len(elementary_articles)}개 (평균 {sum(len(a['messages']) for a in elementary_articles)//len(elementary_articles)}개 메시지)")
    print(f"  📙 Intermediate: {len(intermediate_articles)}개 (평균 {sum(len(a['messages']) for a in intermediate_articles)//len(intermediate_articles)}개 메시지)")
    print(f"  📕 Advanced: {len(advanced_articles)}개 (평균 {sum(len(a['messages']) for a in advanced_articles)//len(advanced_articles)}개 메시지)")

if __name__ == "__main__":
    main()
