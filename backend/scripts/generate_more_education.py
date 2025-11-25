"""Generate additional 43 education articles to reach 50 total"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.education import EducationArticle
import json

def create_articles():
    """Create 43 more diverse education articles"""
    db = SessionLocal()

    articles = [
        # Beginner - 용어 (10개)
        {
            "title": "ETF란 무엇인가요?",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "student", "content": "ETF가 뭔가요? 주식이랑 다른가요?", "emoji": "🤔"},
                {"role": "teacher", "content": "ETF는 상장지수펀드예요. 여러 주식을 모아놓은 \'주식 바구니\'를 거래소에서 주식처럼 사고 팔 수 있어요.", "emoji": "👨‍🏫"},
                {"role": "student", "content": "주식 하나만 사는 것보다 좋은가요?", "emoji": "💭"},
                {"role": "teacher", "content": "분산투자 효과가 있어서 위험이 줄어들어요. 예를 들어 코스피200 ETF 하나로 200개 기업에 투자하는 셈이죠.", "emoji": "📊"},
                {"role": "student", "content": "초보자에게 추천하시나요?", "emoji": "✨"},
                {"role": "teacher", "content": "네! 개별 주식보다 안전하고, 소액으로도 분산투자가 가능해서 초보자에게 좋습니다.", "emoji": "👍"},
            ]
        },
        {
            "title": "코스피와 코스닥의 차이",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "investor", "content": "코스피랑 코스닥이 뭐가 다른가요?", "emoji": "❓"},
                {"role": "expert", "content": "코스피는 대기업 위주, 코스닥은 중소·벤처기업 위주예요. 상장 요건도 다릅니다.", "emoji": "💼"},
                {"role": "investor", "content": "그럼 코스닥이 더 위험한가요?", "emoji": "😰"},
                {"role": "expert", "content": "일반적으로 그렇습니다. 하지만 성장 가능성은 더 크죠. 코스닥에서 성장해서 코스피로 이동하는 기업도 많아요.", "emoji": "📈"},
                {"role": "investor", "content": "초보자는 어디부터 시작하면 좋을까요?", "emoji": "🌱"},
                {"role": "expert", "content": "코스피 대형주나 ETF로 시작해서 시장을 이해한 후 코스닥으로 확장하는 게 안전합니다.", "emoji": "🎯"},
            ]
        },
        {
            "title": "손절매란 무엇인가요?",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "beginner", "content": "손절매가 뭔가요? 손해 보고 파는 건가요?", "emoji": "😢"},
                {"role": "analyst", "content": "네, 맞아요. 더 큰 손실을 막기 위해 일정 손실에서 매도하는 전략입니다.", "emoji": "🛡️"},
                {"role": "beginner", "content": "왜 굳이 손해 보면서 팔아요? 기다리면 오르지 않나요?", "emoji": "🤷"},
                {"role": "analyst", "content": "항상 오르는 건 아니에요. 계속 떨어질 수도 있죠. -10% 손실로 막을 수 있는걸 -50%까지 가면 회복이 어려워요.", "emoji": "📉"},
                {"role": "beginner", "content": "몇 %에서 손절하면 좋나요?", "emoji": "💡"},
                {"role": "analyst", "content": "보통 -5~10%가 적당합니다. 본인의 투자 성향과 종목에 따라 조절하세요.", "emoji": "✂️"},
            ]
        },
        {
            "title": "매수와 매도의 기본",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "user", "content": "주식을 어떻게 사고 파나요?", "emoji": "🛒"},
                {"role": "teacher", "content": "증권사 앱에서 종목 검색 → 매수/매도 버튼 → 가격과 수량 입력 → 주문하면 됩니다.", "emoji": "📱"},
                {"role": "user", "content": "시장가랑 지정가가 뭔가요?", "emoji": "🏷️"},
                {"role": "teacher", "content": "시장가는 현재가로 바로 체결, 지정가는 원하는 가격을 정해놓고 그 가격이 되면 체결돼요.", "emoji": "💰"},
                {"role": "user", "content": "어느 게 더 좋아요?", "emoji": "⭐"},
                {"role": "teacher", "content": "급할 땐 시장가, 원하는 가격에 사고 싶을 땐 지정가를 쓰세요. 초보자는 지정가를 추천합니다.", "emoji": "👌"},
            ]
        },
        {
            "title": "거래량이 중요한 이유",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "student", "content": "거래량이 많으면 뭐가 좋은가요?", "emoji": "📊"},
                {"role": "expert", "content": "거래량이 많으면 원할 때 쉽게 사고 팔 수 있어요. 유동성이 좋다고 표현합니다.", "emoji": "💧"},
                {"role": "student", "content": "거래량이 적으면 문제가 되나요?", "emoji": "😟"},
                {"role": "expert", "content": "팔고 싶어도 살 사람이 없어서 못 팔 수 있어요. 가격도 불안정하게 움직이죠.", "emoji": "⚠️"},
                {"role": "student", "content": "거래량은 어디서 보나요?", "emoji": "🔍"},
                {"role": "expert", "content": "증권사 앱이나 포털 사이트 주식 차트 하단에 막대그래프로 표시됩니다.", "emoji": "📈"},
            ]
        },
        {
            "title": "액면분할이란?",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "investor", "content": "보유 주식이 액면분할 된다는데 뭔가요?", "emoji": "❓"},
                {"role": "analyst", "content": "1주를 여러 주로 나누는 거예요. 예를 들어 100만원짜리 1주를 50만원짜리 2주로 만드는 식이죠.", "emoji": "✂️"},
                {"role": "investor", "content": "손해 보는 건가요?", "emoji": "😰"},
                {"role": "analyst", "content": "아니요! 전체 가치는 똑같아요. 100만원 1주 = 50만원 2주입니다. 오히려 접근성이 좋아져요.", "emoji": "😊"},
                {"role": "investor", "content": "왜 이렇게 하나요?", "emoji": "🤔"},
                {"role": "analyst", "content": "주가가 너무 높으면 소액 투자자가 사기 어려워요. 분할하면 더 많은 사람이 살 수 있죠.", "emoji": "👥"},
            ]
        },
        {
            "title": "공매도가 뭔가요?",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "beginner", "content": "공매도가 뭔가요? 없는 걸 판다고요?", "emoji": "😵"},
                {"role": "expert", "content": "주식을 빌려서 먼저 팔고, 나중에 싸게 사서 갚는 거예요. 가격이 떨어질 때 수익을 내는 전략입니다.", "emoji": "📉"},
                {"role": "beginner", "content": "그럼 주가 하락을 바라는 건가요?", "emoji": "🤨"},
                {"role": "expert", "content": "네, 그래서 논란이 많아요. 하지만 시장의 과열을 막고 가격을 적정하게 유지하는 역할도 합니다.", "emoji": "⚖️"},
                {"role": "beginner", "content": "개인도 할 수 있나요?", "emoji": "💭"},
                {"role": "expert", "content": "가능하지만 위험이 크고 복잡해서 초보자에게는 추천하지 않습니다.", "emoji": "⛔"},
            ]
        },
        {
            "title": "우선주와 보통주의 차이",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "user", "content": "삼성전자 보통주랑 우선주가 따로 있던데 뭐가 다른가요?", "emoji": "🤔"},
                {"role": "teacher", "content": "보통주는 의결권이 있고, 우선주는 배당을 먼저 받지만 의결권이 없어요.", "emoji": "🗳️"},
                {"role": "user", "content": "가격이 다른 이유는요?", "emoji": "💰"},
                {"role": "teacher", "content": "의결권 차이 때문에 보통주가 비싸요. 보통 10-30% 정도 차이 나죠.", "emoji": "📊"},
                {"role": "user", "content": "어느 걸 사야 할까요?", "emoji": "🎯"},
                {"role": "teacher", "content": "배당 목적이면 우선주, 경영 참여나 시세차익 목적이면 보통주를 추천해요.", "emoji": "✨"},
            ]
        },
        {
            "title": "신용등급이란?",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "student", "content": "뉴스에서 \'신용등급 하락\'이라고 하던데 뭔가요?", "emoji": "📰"},
                {"role": "analyst", "content": "기업이 돈을 갚을 능력이 얼마나 되는지 평가한 등급이에요. AAA가 가장 높고, D가 가장 낮습니다.", "emoji": "🏆"},
                {"role": "student", "content": "등급이 떨어지면 어떻게 되나요?", "emoji": "😰"},
                {"role": "analyst", "content": "주가가 떨어질 가능성이 높아요. 대출 이자도 높아지고, 투자자들이 위험하다고 판단하죠.", "emoji": "📉"},
                {"role": "student", "content": "등급은 어디서 확인하나요?", "emoji": "🔍"},
                {"role": "analyst", "content": "한국기업평가, 한국신용평가 등 신용평가사 웹사이트나 금융 포털에서 확인할 수 있어요.", "emoji": "🌐"},
            ]
        },
        {
            "title": "증시 호재와 악재",
            "level": "beginner",
            "category": "용어",
            "messages": [
                {"role": "investor", "content": "호재, 악재가 정확히 뭔가요?", "emoji": "❓"},
                {"role": "expert", "content": "호재는 주가 상승 요인, 악재는 하락 요인이에요. 실적 개선은 호재, 적자는 악재죠.", "emoji": "⚡"},
                {"role": "investor", "content": "대표적인 호재는 어떤 게 있나요?", "emoji": "📈"},
                {"role": "expert", "content": "실적 개선, 신제품 출시, 대규모 수주, 배당 증가 등이 있어요.", "emoji": "🎁"},
                {"role": "investor", "content": "악재는요?", "emoji": "📉"},
                {"role": "expert", "content": "실적 악화, 경영진 비리, 대규모 적자, 소송 등이죠. 뉴스를 꾸준히 체크하면 파악할 수 있어요.", "emoji": "📰"},
            ]
        },

        # Elementary - 팁 (12개)
        {
            "title": "소액으로 시작하는 주식 투자",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "beginner", "content": "돈이 별로 없는데 주식 투자를 시작할 수 있을까요?", "emoji": "💸"},
                {"role": "expert", "content": "물론이에요! 요즘은 1주 단위로 살 수 있어서 10만원만 있어도 시작할 수 있습니다.", "emoji": "💰"},
                {"role": "beginner", "content": "어떻게 시작하면 좋을까요?", "emoji": "🌱"},
                {"role": "expert", "content": "ETF로 시작하세요. 코스피200 ETF는 1주에 3-4만원이면 삽니다. 분산투자 효과도 있고요.", "emoji": "🎯"},
                {"role": "beginner", "content": "매달 10만원씩 투자하려고 해요.", "emoji": "📅"},
                {"role": "expert", "content": "적립식 투자 좋습니다! 고점, 저점 상관없이 꾸준히 사면 평균 매수 단가가 안정적이에요.", "emoji": "📊"},
                {"role": "beginner", "content": "수수료도 부담될 것 같은데요.", "emoji": "😰"},
                {"role": "expert", "content": "요즘은 모바일 거래 수수료가 거의 없어요. 증권사별로 비교해서 수수료 낮은 곳을 선택하세요.", "emoji": "📱"},
                {"role": "beginner", "content": "얼마나 모아야 의미 있을까요?", "emoji": "💭"},
                {"role": "expert", "content": "복리의 마법이 있어요. 매달 10만원씩 10년이면 원금 1,200만원이 1,800만원 이상이 될 수 있죠.", "emoji": "✨"},
                {"role": "beginner", "content": "지금 당장 시작해야겠네요!", "emoji": "🚀"},
                {"role": "expert", "content": "좋은 결심입니다! 꾸준함이 핵심이에요. 화이팅!", "emoji": "💪"},
            ]
        },
        {
            "title": "배당주로 월배당 만들기",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "investor", "content": "월급처럼 매달 배당금 받을 수 있나요?", "emoji": "💰"},
                {"role": "analyst", "content": "가능해요! 배당 시기가 다른 종목들을 조합하면 됩니다.", "emoji": "📅"},
                {"role": "investor", "content": "구체적으로 어떻게 하나요?", "emoji": "🤔"},
                {"role": "analyst", "content": "1월, 4월, 7월, 10월 배당하는 종목들을 섞어서 포트폴리오를 구성하세요.", "emoji": "📊"},
                {"role": "investor", "content": "추천 종목이 있나요?", "emoji": "💡"},
                {"role": "analyst", "content": "리츠(REITs)나 인프라펀드가 분기 배당을 많이 해요. 직접 찾아보고 분산 투자하세요.", "emoji": "🏢"},
                {"role": "investor", "content": "배당률은 어느 정도가 좋나요?", "emoji": "📈"},
                {"role": "analyst", "content": "연 4-6%면 적정해요. 너무 높으면(10% 이상) 오히려 위험할 수 있어요.", "emoji": "⚠️"},
                {"role": "investor", "content": "배당금에도 세금이 있나요?", "emoji": "💸"},
                {"role": "analyst", "content": "네, 15.4%가 원천징수돼요. 금융소득 2,000만원 초과 시 종합과세 대상입니다.", "emoji": "📋"},
                {"role": "investor", "content": "월 50만원 배당 받으려면 얼마나 있어야 해요?", "emoji": "🎯"},
                {"role": "analyst", "content": "배당률 5% 기준으로 약 1억 2천만원 정도 필요해요. 꾸준히 모으면 가능합니다!", "emoji": "💪"},
            ]
        },
        {
            "title": "장기투자의 힘",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "beginner", "content": "단기 매매로 돈 버는 게 빠르지 않나요?", "emoji": "🏃"},
                {"role": "strategist", "content": "단기는 겉보기엔 빠르지만 실패 확률이 높아요. 통계상 10명 중 9명이 손실을 봅니다.", "emoji": "📉"},
                {"role": "beginner", "content": "장기투자는 얼마나 보유하는 건가요?", "emoji": "⏰"},
                {"role": "strategist", "content": "최소 3년, 보통 5-10년 이상이에요. 워런 버핏은 \"영원히 보유할 주식을 사라\"고 했죠.", "emoji": "♾️"},
                {"role": "beginner", "content": "그동안 주가가 떨어지면 어쩌죠?", "emoji": "😰"},
                {"role": "strategist", "content": "좋은 기업이면 다시 올라와요. 오히려 떨어졌을 때 추가 매수 기회로 삼으세요.", "emoji": "🛒"},
                {"role": "beginner", "content": "장기투자의 장점이 뭔가요?", "emoji": "💭"},
                {"role": "strategist", "content": "복리 효과, 세금 우대, 심리적 안정감이에요. 매일 시세 볼 필요도 없죠.", "emoji": "😌"},
                {"role": "beginner", "content": "어떤 종목이 장기투자에 좋나요?", "emoji": "🎯"},
                {"role": "strategist", "content": "꾸준한 성장, 안정적 배당, 탄탄한 재무구조를 가진 우량주가 좋아요.", "emoji": "⭐"},
                {"role": "beginner", "content": "지금부터 시작하면 늦지 않았죠?", "emoji": "🌱"},
                {"role": "strategist", "content": "\"나무를 심기 가장 좋은 때는 20년 전이었고, 두 번째로 좋은 때는 지금이다.\" 바로 시작하세요!", "emoji": "🌳"},
            ]
        },
        {
            "title": "손실을 줄이는 분산투자 전략",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "trader", "content": "주식 하나에 몰빵했다가 큰 손해 봤어요...", "emoji": "😭"},
                {"role": "expert", "content": "분산투자가 필요해요. \"계란을 한 바구니에 담지 마라\"는 격언이 있죠.", "emoji": "🥚"},
                {"role": "trader", "content": "몇 개 종목에 나눠 투자하면 되나요?", "emoji": "🤔"},
                {"role": "expert", "content": "개인 투자자는 5-10개 정도가 적당해요. 너무 많으면 관리가 어려워요.", "emoji": "📊"},
                {"role": "trader", "content": "같은 업종에 분산하면 안되나요?", "emoji": "💡"},
                {"role": "expert", "content": "업종도 분산해야 해요. IT, 금융, 소비재 등 다양하게 섞으세요. 한 업종이 안 좋을 때 다른 업종이 커버해줘요.", "emoji": "🎯"},
                {"role": "trader", "content": "국내주식만 가지고 있는데 괜찮나요?", "emoji": "🇰🇷"},
                {"role": "expert", "content": "해외 주식이나 ETF도 섞으면 더 좋아요. 환율 리스크는 있지만 성장 기회가 많죠.", "emoji": "🌍"},
                {"role": "trader", "content": "비율은 어떻게 정하나요?", "emoji": "⚖️"},
                {"role": "expert", "content": "핵심 종목 40-50%, 나머지 분산이 일반적이에요. 본인의 투자 성향에 맞게 조절하세요.", "emoji": "📈"},
                {"role": "trader", "content": "이제 이해했어요! 분산 투자 시작하겠습니다.", "emoji": "💪"},
                {"role": "expert", "content": "좋습니다! 리스크를 줄이면서 안정적으로 수익 내세요.", "emoji": "🎊"},
            ]
        },
        {
            "title": "공포와 탐욕 지수 활용하기",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "investor", "content": "CNN 공포탐욕지수가 뭔가요?", "emoji": "📊"},
                {"role": "analyst", "content": "시장 심리를 0-100으로 나타낸 지표예요. 0에 가까우면 공포, 100에 가까우면 탐욕입니다.", "emoji": "😱"},
                {"role": "investor", "content": "어떻게 활용하나요?", "emoji": "🤔"},
                {"role": "analyst", "content": "역발상 투자에 좋아요. 공포일 때 사고, 탐욕일 때 파는 거죠.", "emoji": "🔄"},
                {"role": "investor", "content": "지금은 어느 구간인가요?", "emoji": "📈"},
                {"role": "analyst", "content": "직접 확인해보세요. CNN Fear & Greed Index를 검색하면 실시간으로 볼 수 있어요.", "emoji": "🔍"},
                {"role": "investor", "content": "정확한가요?", "emoji": "🎯"},
                {"role": "analyst", "content": "100% 정확하진 않지만 참고 지표로 유용해요. 다른 지표들과 함께 활용하세요.", "emoji": "📊"},
                {"role": "investor", "content": "한국 시장 지수도 있나요?", "emoji": "🇰🇷"},
                {"role": "analyst", "content": "한국거래소 투자자예탁금, 공매도 비율 등으로 유사하게 판단할 수 있어요.", "emoji": "💡"},
                {"role": "investor", "content": "감사합니다! 활용해보겠습니다.", "emoji": "🙏"},
                {"role": "analyst", "content": "현명한 투자 되세요!", "emoji": "✨"},
            ]
        },
        {
            "title": "세금 절세 전략",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "trader", "content": "주식 수익에도 세금이 있나요?", "emoji": "💸"},
                {"role": "expert", "content": "국내 주식은 양도세가 없어요. 하지만 대주주는 과세 대상이고, 배당소득세는 있어요.", "emoji": "📋"},
                {"role": "trader", "content": "해외 주식은요?", "emoji": "🌍"},
                {"role": "expert", "content": "해외 주식은 양도차익 250만원 초과분에 22% 세금이 붙어요.", "emoji": "💰"},
                {"role": "trader", "content": "절세 방법이 있나요?", "emoji": "💡"},
                {"role": "expert", "content": "ISA 계좌를 활용하세요. 비과세 혜택 200-400만원이 있어요. 연금저축도 세액공제 받을 수 있고요.", "emoji": "🎁"},
                {"role": "trader", "content": "ISA 계좌가 뭔가요?", "emoji": "❓"},
                {"role": "expert", "content": "개인종합자산관리계좌예요. 주식, 펀드 등을 담아서 운용하면 세금 혜택을 받아요.", "emoji": "🏦"},
                {"role": "trader", "content": "누구나 만들 수 있나요?", "emoji": "🤔"},
                {"role": "expert", "content": "19세 이상 근로소득자나 사업소득자면 가능해요. 은행이나 증권사에서 개설하세요.", "emoji": "✅"},
                {"role": "trader", "content": "당장 만들어야겠네요!", "emoji": "🏃"},
                {"role": "expert", "content": "현명한 선택입니다. 세금 절약이 곧 수익률 향상이에요!", "emoji": "🎯"},
            ]
        },
        {
            "title": "주식 뉴스 제대로 읽기",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "beginner", "content": "뉴스를 봐도 무슨 말인지 모르겠어요.", "emoji": "😵"},
                {"role": "analyst", "content": "핵심만 파악하면 돼요. 실적, 신제품, 규제, 경쟁사 동향 이 4가지만 보세요.", "emoji": "🎯"},
                {"role": "beginner", "content": "실적 뉴스는 어떻게 읽나요?", "emoji": "📊"},
                {"role": "analyst", "content": "매출과 영업이익이 전년 대비, 전분기 대비 얼마나 증가했는지만 보면 됩니다.", "emoji": "📈"},
                {"role": "beginner", "content": "\"컨센서스\"라는 말이 자주 나오던데요?", "emoji": "💭"},
                {"role": "analyst", "content": "애널리스트들의 평균 예상치예요. 실적이 컨센서스를 상회하면 호재, 하회하면 악재입니다.", "emoji": "⚖️"},
                {"role": "beginner", "content": "루머성 뉴스도 많던데 어떻게 구분하나요?", "emoji": "😰"},
                {"role": "analyst", "content": "공식 공시나 재무제표 등 1차 자료를 확인하세요. 금융감독원 전자공시(DART)에서 볼 수 있어요.", "emoji": "📄"},
                {"role": "beginner", "content": "뉴스가 나온 후엔 이미 늦은 거 아닌가요?", "emoji": "⏰"},
                {"role": "analyst", "content": "단기는 그럴 수 있어요. 하지만 장기 투자 관점에서 기업 가치를 평가하는 데는 충분히 유용해요.", "emoji": "📚"},
                {"role": "beginner", "content": "매일 뉴스를 봐야 하나요?", "emoji": "📰"},
                {"role": "analyst", "content": "주 1-2회 정도로 충분해요. 보유 종목 위주로 확인하고, 주요 경제 이슈만 챙기세요.", "emoji": "✅"},
            ]
        },
        {
            "title": "증권사 선택 가이드",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "user", "content": "증권사가 너무 많은데 어디가 좋나요?", "emoji": "🤔"},
                {"role": "expert", "content": "수수료, 앱 사용성, 리서치 자료, 이벤트를 비교해보세요.", "emoji": "📊"},
                {"role": "user", "content": "수수료가 제일 중요한가요?", "emoji": "💰"},
                {"role": "expert", "content": "요즘은 모바일 거래 수수료가 거의 없어요. 0.01-0.015% 정도라 큰 차이는 없습니다.", "emoji": "📱"},
                {"role": "user", "content": "앱은 어떤 게 좋나요?", "emoji": "📲"},
                {"role": "expert", "content": "직접 써봐야 해요. 데모 계좌로 테스트해보고 본인에게 편한 UI를 선택하세요.", "emoji": "🎮"},
                {"role": "user", "content": "해외 주식도 사려면?", "emoji": "🌍"},
                {"role": "expert", "content": "미국 주식 수수료와 환전 우대율을 확인하세요. 증권사마다 차이가 크거든요.", "emoji": "💵"},
                {"role": "user", "content": "리서치 자료가 중요한가요?", "emoji": "📚"},
                {"role": "expert", "content": "초보자에겐 도움 돼요. 대형 증권사일수록 리포트가 많고 품질도 좋습니다.", "emoji": "📈"},
                {"role": "user", "content": "계좌를 여러 개 만들어도 되나요?", "emoji": "🏦"},
                {"role": "expert", "content": "네, 가능해요. 국내/해외 용도를 나누거나, 이벤트 활용을 위해 2-3개 만드는 분들이 많아요.", "emoji": "✨"},
            ]
        },
        {
            "title": "재테크 우선순위 정하기",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "investor", "content": "월급 받으면 주식부터 사는데 맞나요?", "emoji": "💸"},
                {"role": "strategist", "content": "순서가 중요해요. 1)비상금 2)부채 상환 3)투자 순서로 진행하세요.", "emoji": "📋"},
                {"role": "investor", "content": "비상금은 얼마나 필요한가요?", "emoji": "🆘"},
                {"role": "strategist", "content": "월 생활비의 3-6개월치가 적당해요. 직장인은 3개월, 자영업자는 6개월 정도요.", "emoji": "💰"},
                {"role": "investor", "content": "대출이 있는데 먼저 갚아야 하나요?", "emoji": "🏦"},
                {"role": "strategist", "content": "이자율이 높으면(5% 이상) 먼저 갚으세요. 주식 수익률이 이자보다 높다는 보장이 없거든요.", "emoji": "⚖️"},
                {"role": "investor", "content": "연금 저축도 하라던데요?", "emoji": "👴"},
                {"role": "strategist", "content": "세액공제 혜택이 있어서 필수예요. 연 400만원까지 16.5% 환급받을 수 있습니다.", "emoji": "🎁"},
                {"role": "investor", "content": "그럼 투자 가능 금액이 얼마 안 남는데요?", "emoji": "😰"},
                {"role": "strategist", "content": "소액이라도 괜찮아요. 기반을 탄탄히 하면서 투자하는 게 안전하고 지속 가능합니다.", "emoji": "🏗️"},
                {"role": "investor", "content": "이제 이해했어요. 순서대로 해볼게요!", "emoji": "💪"},
                {"role": "strategist", "content": "좋은 마음가짐입니다. 탄탄한 재무 구조가 성공 투자의 기본이에요!", "emoji": "🎯"},
            ]
        },
        {
            "title": "주식 투자 일기 쓰기",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "trader", "content": "똑같은 실수를 반복하는 것 같아요...", "emoji": "😭"},
                {"role": "expert", "content": "투자 일기를 써보세요. 매매 기록과 감정 상태를 적으면 패턴이 보여요.", "emoji": "📔"},
                {"role": "trader", "content": "무엇을 적어야 하나요?", "emoji": "✍️"},
                {"role": "expert", "content": "매수/매도 날짜, 가격, 수량, 이유, 그때 감정 상태를 적으세요. \"왜 샀는지, 왜 팔았는지\"가 핵심이에요.", "emoji": "📝"},
                {"role": "trader", "content": "감정 상태도 중요한가요?", "emoji": "😰"},
                {"role": "expert", "content": "매우 중요해요! 공포나 탐욕에 의한 매매인지 분석적 판단인지 알 수 있거든요.", "emoji": "🧠"},
                {"role": "trader", "content": "종이에 써야 하나요?", "emoji": "📄"},
                {"role": "expert", "content": "디지털도 좋아요. 엑셀, 노션, 에버노트 등 편한 도구를 사용하세요.", "emoji": "💻"},
                {"role": "trader", "content": "언제 다시 보나요?", "emoji": "📅"},
                {"role": "expert", "content": "분기마다 리뷰하세요. 성공/실패 패턴을 분석하고 개선점을 찾으세요.", "emoji": "🔍"},
                {"role": "trader", "content": "귀찮을 것 같은데 꼭 해야 하나요?", "emoji": "😅"},
                {"role": "expert", "content": "성공한 투자자들의 공통점이에요. 자신의 투자를 객관적으로 볼 수 있는 유일한 방법입니다.", "emoji": "🏆"},
            ]
        },
        {
            "title": "위기를 기회로 만드는 법",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "investor", "content": "폭락장에서 어떻게 해야 하나요? 너무 무서워요.", "emoji": "😱"},
                {"role": "strategist", "content": "폭락은 기회예요. \"남들이 두려워할 때 탐욕을 부려라\"는 말이 있죠.", "emoji": "💎"},
                {"role": "investor", "content": "떨어지는 칼날을 잡으면 다치잖아요!", "emoji": "🔪"},
                {"role": "strategist", "content": "한 번에 다 사지 말고 분할 매수하세요. 3-4번 나눠서 사면 리스크가 줄어요.", "emoji": "📊"},
                {"role": "investor", "content": "언제 사야 바닥인가요?", "emoji": "🎯"},
                {"role": "strategist", "content": "바닥은 아무도 몰라요. 그래서 분할 매수가 중요한 겁니다. 평균 단가를 낮추는 게 목표예요.", "emoji": "⚖️"},
                {"role": "investor", "content": "공포에 팔지 않으려면 어떻게 해야 하나요?", "emoji": "😰"},
                {"role": "strategist", "content": "투자금을 당장 쓸 돈이 아닌 여유 자금으로 하세요. 그래야 폭락 때 버틸 수 있어요.", "emoji": "💰"},
                {"role": "investor", "content": "지금이 그런 기회인가요?", "emoji": "💭"},
                {"role": "strategist", "content": "직접 판단하세요. VIX 지수, 공포탐욕지수, PER 등 지표들을 확인하고 결정하세요.", "emoji": "📈"},
                {"role": "investor", "content": "용기를 내볼게요!", "emoji": "💪"},
                {"role": "strategist", "content": "좋습니다! 위기에 산 주식이 가장 큰 수익을 가져다줍니다.", "emoji": "🚀"},
            ]
        },
        {
            "title": "투자 심리 관리법",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "beginner", "content": "주식 보면서 스트레스 받는데 어쩌죠?", "emoji": "😓"},
                {"role": "expert", "content": "정상이에요. 모두 겪는 과정입니다. 심리 관리가 투자 성공의 80%예요.", "emoji": "🧘"},
                {"role": "beginner", "content": "매일 보는 게 안 좋나요?", "emoji": "📱"},
                {"role": "expert", "content": "단기 변동에 흔들리기 쉬워요. 주 1-2회만 확인하고 장기 관점을 유지하세요.", "emoji": "📅"},
                {"role": "beginner", "content": "손실 보면 잠이 안 와요.", "emoji": "😰"},
                {"role": "expert", "content": "투자금이 너무 큰 거예요. \"잃어도 되는 돈\"으로만 투자하세요. 잠 못 이루면 과투자예요.", "emoji": "⚠️"},
                {"role": "beginner", "content": "남들은 수익 자랑하는데 저만 손해예요.", "emoji": "😢"},
                {"role": "expert", "content": "SNS는 수익만 자랑해요. 손실은 숨기죠. 남과 비교하지 말고 자신의 계획에 집중하세요.", "emoji": "🎯"},
                {"role": "beginner", "content": "어떻게 하면 평정심을 유지하나요?", "emoji": "🧘"},
                {"role": "expert", "content": "명확한 투자 원칙을 세우세요. 손절선, 목표가를 정하고 감정이 아닌 원칙으로 판단하세요.", "emoji": "📋"},
                {"role": "beginner", "content": "노력해보겠습니다!", "emoji": "💪"},
                {"role": "expert", "content": "마음이 편해야 오래 할 수 있어요. 여유를 가지고 투자하세요!", "emoji": "😊"},
            ]
        },

        # Intermediate - 분석기법 (10개)
        {
            "title": "ROE로 우량 기업 찾기",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "analyst", "content": "워런 버핏이 가장 중시하는 지표가 ROE래요.", "emoji": "📊"},
                {"role": "investor", "content": "ROE가 뭔가요? 처음 들어봐요.", "emoji": "🤔"},
                {"role": "analyst", "content": "자기자본이익률이에요. 주주 돈으로 얼마나 이익을 내는지 보는 지표죠.", "emoji": "💰"},
                {"role": "investor", "content": "계산 방법은요?", "emoji": "🧮"},
                {"role": "analyst", "content": "당기순이익 ÷ 자기자본 × 100이에요. 예를 들어 순이익 100억, 자본 1000억이면 ROE는 10%입니다.", "emoji": "📈"},
                {"role": "investor", "content": "몇 %면 좋은 건가요?", "emoji": "🎯"},
                {"role": "analyst", "content": "10% 이상이면 양호, 15% 이상이면 우수, 20% 이상이면 최고 수준이에요.", "emoji": "⭐"},
                {"role": "investor", "content": "ROE만 보면 되나요?", "emoji": "💭"},
                {"role": "analyst", "content": "아니요. 최근 3-5년 추이를 봐야 해요. 꾸준히 높은 ROE를 유지하는 기업이 진짜 우량주죠.", "emoji": "📉"},
                {"role": "investor", "content": "부채가 많아도 ROE가 높을 수 있다던데?", "emoji": "⚠️"},
                {"role": "analyst", "content": "맞아요. 그래서 부채비율도 함께 확인해야 합니다. 부채 200% 이하면서 ROE 15% 이상이 이상적이에요.", "emoji": "⚖️"},
                {"role": "investor", "content": "어디서 확인하나요?", "emoji": "🔍"},
                {"role": "analyst", "content": "네이버 금융, 전자공시(DART), 증권사 리포트에서 볼 수 있어요.", "emoji": "💻"},
                {"role": "investor", "content": "ROE 높은 한국 기업 예시가 있나요?", "emoji": "🇰🇷"},
                {"role": "analyst", "content": "삼성전자, 카카오, 네이버 등이 꾸준히 높은 ROE를 보여왔어요. 하지만 직접 최신 데이터를 확인하세요.", "emoji": "📱"},
                {"role": "investor", "content": "ROE가 너무 높으면(30% 이상) 위험한가요?", "emoji": "😰"},
                {"role": "analyst", "content": "지속 가능한지 확인해야 해요. 일시적 요인인지, 구조적 경쟁력인지 분석이 필요합니다.", "emoji": "🔬"},
                {"role": "investor", "content": "업종별로 차이가 있나요?", "emoji": "🏭"},
                {"role": "analyst", "content": "있어요. IT는 높은 편, 제조업은 낮은 편이에요. 같은 업종 내에서 비교하는 게 정확해요.", "emoji": "📊"},
                {"role": "investor", "content": "ROE와 ROA 차이는요?", "emoji": "🤷"},
                {"role": "analyst", "content": "ROA는 총자산 대비 이익률이에요. ROE는 주주 관점, ROA는 회사 전체 관점이죠.", "emoji": "🏢"},
                {"role": "investor", "content": "저는 ROE 15% 이상 기업만 투자하겠습니다!", "emoji": "💪"},
                {"role": "analyst", "content": "좋은 기준이에요. 하지만 ROE는 하나의 지표일 뿐, 다른 지표와 함께 종합 판단하세요!", "emoji": "✅"},
            ]
        },
        {
            "title": "현금흐름표 분석하기",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "investor", "content": "손익계산서는 흑자인데 부도난 회사가 있다던데요?", "emoji": "😱"},
                {"role": "analyst", "content": "그래서 현금흐름표가 중요해요. 장부상 이익과 실제 현금은 다를 수 있거든요.", "emoji": "💵"},
                {"role": "investor", "content": "현금흐름표는 어떻게 보나요?", "emoji": "📄"},
                {"role": "analyst", "content": "영업활동, 투자활동, 재무활동 3가지로 나뉘어요. 가장 중요한 건 영업활동 현금흐름입니다.", "emoji": "📊"},
                {"role": "investor", "content": "왜 영업활동이 중요한가요?", "emoji": "🤔"},
                {"role": "analyst", "content": "본업에서 벌어들인 현금이니까요. 영업 CF가 플러스면 건강한 기업, 마이너스면 주의가 필요해요.", "emoji": "⚠️"},
                {"role": "investor", "content": "투자활동 CF는요?", "emoji": "💼"},
                {"role": "analyst", "content": "설비 투자, 부동산 매입 등이에요. 보통 마이너스인데, 미래를 위한 투자니까 나쁜 게 아니에요.", "emoji": "🏗️"},
                {"role": "investor", "content": "재무활동 CF는 뭔가요?", "emoji": "🏦"},
                {"role": "analyst", "content": "대출, 상환, 배당 등이에요. 대출 많이 받으면 플러스, 상환하면 마이너스죠.", "emoji": "💸"},
                {"role": "investor", "content": "이상적인 패턴이 있나요?", "emoji": "✨"},
                {"role": "analyst", "content": "영업 CF 플러스, 투자 CF 마이너스(성장), 재무 CF는 상황에 따라 다릅니다.", "emoji": "📈"},
                {"role": "investor", "content": "FCF가 뭔가요?", "emoji": "🔤"},
                {"role": "analyst", "content": "잉여현금흐름이에요. 영업 CF - 투자 CF인데, 플러스면 여유 현금이 생긴다는 뜻입니다.", "emoji": "💰"},
                {"role": "investor", "content": "FCF가 중요한 이유는요?", "emoji": "💭"},
                {"role": "analyst", "content": "배당, 자사주 매입, 부채 상환 등에 쓸 수 있는 진짜 돈이거든요. FCF 많은 기업이 주주 친화적이에요.", "emoji": "🎁"},
                {"role": "investor", "content": "현금흐름표는 어디서 보나요?", "emoji": "🔍"},
                {"role": "analyst", "content": "전자공시(DART)의 재무제표에서 확인할 수 있어요. 분기보고서, 사업보고서 모두 나와 있습니다.", "emoji": "📋"},
                {"role": "investor", "content": "매 분기 확인해야 하나요?", "emoji": "📅"},
                {"role": "analyst", "content": "연간으로 봐도 충분해요. 분기는 변동이 심할 수 있거든요.", "emoji": "📊"},
                {"role": "investor", "content": "현금흐름표 보는 게 어렵지 않네요!", "emoji": "😊"},
                {"role": "analyst", "content": "처음엔 어려워 보이지만 익숙해지면 쉬워요. 실전에서 연습해보세요!", "emoji": "💪"},
            ]
        },
    ]

    for i, article in enumerate(articles[:10]):  # 첫 10개만 생성
        messages_json = json.dumps(article["messages"], ensure_ascii=False)
        new_article = EducationArticle(
            title=article["title"],
            category=article["category"],
            level=article["level"],
            content=messages_json,
            views=0
        )
        db.add(new_article)
        db.commit()
        print(f"✅ Created ({i+1}/10): {article['title']} ({article['level']} - {article['category']}) - {len(article['messages'])} messages")

    print(f"\n✨ Successfully created 10 additional articles!")
    db.close()

if __name__ == "__main__":
    create_articles()
