"""Generate final 33 education articles to reach 50 total"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.education import EducationArticle
import json

def create_articles():
    """Create 33 more education articles"""
    db = SessionLocal()

    articles = [
        # Elementary - 팁 (15개)
        {
            "title": "소액으로 시작하는 투자",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "beginner", "content": "돈이 많이 없는데도 투자할 수 있나요?", "emoji": "💰"},
                {"role": "mentor", "content": "물론이죠! 소액으로도 충분히 시작할 수 있어요. 중요한 건 금액이 아니라 습관입니다.", "emoji": "💡"},
                {"role": "beginner", "content": "얼마 정도면 시작할 수 있어요?", "emoji": "🤔"},
                {"role": "mentor", "content": "월 10만원부터 가능해요. 적립식으로 ETF나 우량주에 꾸준히 투자하는 게 좋습니다.", "emoji": "📈"},
                {"role": "beginner", "content": "소액이라 수익이 적지 않나요?", "emoji": "😅"},
                {"role": "mentor", "content": "처음엔 작지만, 복리 효과로 시간이 지나면 커집니다. 일찍 시작하는 게 가장 중요해요!", "emoji": "⏰"},
            ]
        },
        {
            "title": "배당주 투자 전략",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "investor", "content": "배당주가 뭐예요? 주식 사면 돈을 주나요?", "emoji": "💵"},
                {"role": "advisor", "content": "네! 기업이 번 이익을 주주들에게 나눠주는 걸 배당이라고 해요. 정기적으로 받을 수 있죠.", "emoji": "🎁"},
                {"role": "investor", "content": "모든 주식이 배당을 주나요?", "emoji": "❓"},
                {"role": "advisor", "content": "아니요. 성장 중인 기업은 배당 대신 재투자를 선호해요. 안정적인 대형주가 배당을 많이 줍니다.", "emoji": "🏢"},
                {"role": "investor", "content": "배당만으로도 수익이 될까요?", "emoji": "🤑"},
                {"role": "advisor", "content": "배당수익률 3-5%면 괜찮지만, 주가 상승도 함께 봐야 해요. 둘 다 고려하는 게 중요합니다!", "emoji": "⚖️"},
            ]
        },
        {
            "title": "장기 투자의 힘",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "student", "content": "단타 vs 장기투자 뭐가 나아요?", "emoji": "⚡"},
                {"role": "expert", "content": "대부분의 개인투자자에겐 장기투자가 유리합니다. 시간이 위험을 줄여주거든요.", "emoji": "🛡️"},
                {"role": "student", "content": "얼마나 보유해야 장기투자인가요?", "emoji": "⏳"},
                {"role": "expert", "content": "최소 3년, 이상적으로는 5-10년입니다. 복리 효과가 본격적으로 나타나는 기간이에요.", "emoji": "📅"},
                {"role": "student", "content": "중간에 팔고 싶으면요?", "emoji": "🤷"},
                {"role": "expert", "content": "감정적으로 판단하지 마세요. 기업 펀더멘털이 나빠졌거나 더 좋은 기회가 있을 때만 고려하세요.", "emoji": "🎯"},
            ]
        },
        {
            "title": "분산투자의 중요성",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "user", "content": "한 종목에 몰빵하면 안 되나요?", "emoji": "🎲"},
                {"role": "teacher", "content": "매우 위험해요! '계란을 한 바구니에 담지 마라'는 격언처럼 분산이 중요합니다.", "emoji": "🧺"},
                {"role": "user", "content": "몇 개 종목을 사야 하나요?", "emoji": "🔢"},
                {"role": "teacher", "content": "개인투자자는 10-20개 정도가 적당해요. 너무 많으면 관리가 어렵고, 적으면 위험해요.", "emoji": "📊"},
                {"role": "user", "content": "같은 업종만 사도 분산인가요?", "emoji": "🏭"},
                {"role": "teacher", "content": "아니요! 업종도 분산해야 해요. IT, 금융, 헬스케어, 소비재 등 다양하게 투자하세요.", "emoji": "🌈"},
            ]
        },
        {
            "title": "공포·탐욕 지수 활용법",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "trader", "content": "공포·탐욕 지수가 뭔가요?", "emoji": "📊"},
                {"role": "analyst", "content": "시장 심리를 0-100으로 나타낸 지표예요. 0에 가까울수록 공포, 100에 가까울수록 탐욕입니다.", "emoji": "🎭"},
                {"role": "trader", "content": "어떻게 활용하나요?", "emoji": "🤔"},
                {"role": "analyst", "content": "역발상 전략이에요. 극단적 공포일 때 매수, 극단적 탐욕일 때 매도를 고려하죠.", "emoji": "🔄"},
                {"role": "trader", "content": "정확한가요?", "emoji": "🎯"},
                {"role": "analyst", "content": "100% 정확하진 않지만, 시장 과열/침체를 판단하는 참고 지표로 유용합니다.", "emoji": "📈"},
            ]
        },
        {
            "title": "절세 계좌 활용하기",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "investor", "content": "ISA, 연금저축... 뭐가 뭔지 모르겠어요", "emoji": "😵"},
                {"role": "advisor", "content": "절세 계좌들이에요. 세금 혜택을 받으면서 투자할 수 있죠. 각각 장단점이 있어요.", "emoji": "💰"},
                {"role": "investor", "content": "어떤 차이가 있나요?", "emoji": "❓"},
                {"role": "advisor", "content": "ISA는 3년 의무보유에 200-400만원 비과세, 연금저축은 연말정산 혜택이 큽니다.", "emoji": "📋"},
                {"role": "investor", "content": "둘 다 해야 하나요?", "emoji": "🤷"},
                {"role": "advisor", "content": "여유가 된다면 둘 다 활용하세요. 세금을 아끼는 게 곧 수익률입니다!", "emoji": "✨"},
            ]
        },
        {
            "title": "뉴스 제대로 읽기",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "beginner", "content": "뉴스를 보는데 뭐가 중요한지 모르겠어요", "emoji": "📰"},
                {"role": "expert", "content": "제목만 보지 말고 본문을 읽고, 여러 기사를 비교하세요. 편향된 시각을 걸러내야 해요.", "emoji": "🔍"},
                {"role": "beginner", "content": "어떤 뉴스를 봐야 하나요?", "emoji": "❓"},
                {"role": "expert", "content": "실적 발표, 신제품 출시, 인수합병, 정책 변화 등 기업 실적에 영향을 주는 뉴스가 중요해요.", "emoji": "📈"},
                {"role": "beginner", "content": "찌라시는 어떻게 구별하나요?", "emoji": "🚨"},
                {"role": "expert", "content": "출처가 불분명하거나 과장된 표현이 많으면 의심하세요. 공식 공시를 먼저 확인하세요!", "emoji": "✅"},
            ]
        },
        {
            "title": "증권사 고르는 법",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "user", "content": "증권사가 너무 많은데 어디가 좋아요?", "emoji": "🏦"},
                {"role": "advisor", "content": "수수료, 앱 사용성, 리서치 정보, 해외주식 지원 등을 비교해보세요.", "emoji": "📱"},
                {"role": "user", "content": "수수료가 제일 중요한가요?", "emoji": "💰"},
                {"role": "advisor", "content": "중요하지만 전부는 아니에요. 앱이 불편하거나 정보가 부족하면 수수료가 싸도 손해일 수 있어요.", "emoji": "⚖️"},
                {"role": "user", "content": "여러 개 써도 되나요?", "emoji": "🤔"},
                {"role": "advisor", "content": "네! 국내주식은 A증권사, 해외주식은 B증권사 이런 식으로 용도별로 나눠 쓰는 것도 좋습니다.", "emoji": "👍"},
            ]
        },
        {
            "title": "투자 전 재무 정리",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "student", "content": "빚이 있는데 투자해도 될까요?", "emoji": "😰"},
                {"role": "mentor", "content": "고금리 빚(카드론, 대출)은 먼저 갚는 게 좋아요. 투자 수익보다 이자가 더 클 수 있거든요.", "emoji": "💳"},
                {"role": "student", "content": "비상금은 얼마나 필요해요?", "emoji": "🚨"},
                {"role": "mentor", "content": "월 생활비의 3-6개월치는 비상금으로 확보하세요. 그 다음에 투자를 시작하는 게 안전합니다.", "emoji": "🛡️"},
                {"role": "student", "content": "투자 비중은 어떻게 정하나요?", "emoji": "📊"},
                {"role": "mentor", "content": "100-나이 공식을 참고하세요. 30세면 자산의 70%까지 주식 투자 가능하다는 뜻이에요.", "emoji": "🎯"},
            ]
        },
        {
            "title": "투자 일기 쓰기",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "investor", "content": "투자 일기를 쓰라는데 왜 필요한가요?", "emoji": "📝"},
                {"role": "coach", "content": "매수·매도 이유를 기록하면 실수를 반복하지 않게 돼요. 성장하는 투자자의 비결이죠!", "emoji": "📈"},
                {"role": "investor", "content": "뭘 써야 하나요?", "emoji": "❓"},
                {"role": "coach", "content": "매수 이유, 목표가, 손절선, 그리고 그날의 시장 상황과 내 감정을 적으세요.", "emoji": "✍️"},
                {"role": "investor", "content": "귀찮을 것 같은데...", "emoji": "😅"},
                {"role": "coach", "content": "처음엔 그렇지만 몇 달 후 보면 큰 도움이 됩니다. 같은 실수를 막아주니까요!", "emoji": "💪"},
            ]
        },
        {
            "title": "위기 시 대처법",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "beginner", "content": "주가가 폭락하면 어떻게 해야 하나요?", "emoji": "😱"},
                {"role": "expert", "content": "일단 침착하세요! 패닉 매도가 가장 위험합니다. 보유 이유를 다시 점검하세요.", "emoji": "🧘"},
                {"role": "beginner", "content": "모든 종목이 떨어지는데요?", "emoji": "📉"},
                {"role": "expert", "content": "시장 전체가 떨어질 때는 기다리거나 분할 매수를 고려하세요. 역사적으로 시장은 회복해왔어요.", "emoji": "📊"},
                {"role": "beginner", "content": "손실이 너무 커서 무섭습니다", "emoji": "😰"},
                {"role": "expert", "content": "투자 원칙을 지켰다면 회복을 기다리세요. 감정적으로 판단하면 저점에 팔게 됩니다.", "emoji": "💎"},
            ]
        },
        {
            "title": "투자 심리 관리",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "trader", "content": "매일 주가를 보면 스트레스받아요", "emoji": "😫"},
                {"role": "psychologist", "content": "장기투자자라면 매일 볼 필요 없어요. 주 1-2회 정도로 줄이세요. 감정 소모가 큽니다.", "emoji": "🧠"},
                {"role": "trader", "content": "손실이 나면 잠을 못 자요", "emoji": "😴"},
                {"role": "psychologist", "content": "투자 금액이 과한 거예요. '잃어도 생활에 지장 없는 돈'으로만 투자하세요.", "emoji": "💰"},
                {"role": "trader", "content": "다른 사람이 수익냈다는데 부러워요", "emoji": "😔"},
                {"role": "psychologist", "content": "남과 비교하지 마세요. 자신의 목표와 계획에 집중하는 게 장기적으로 성공하는 길입니다!", "emoji": "🎯"},
            ]
        },
        {
            "title": "세력주 피하는 법",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "newbie", "content": "세력주가 뭐예요?", "emoji": "❓"},
                {"role": "veteran", "content": "특정 세력이 주가를 인위적으로 조작하는 종목이에요. 개미들을 유인한 후 매도하죠.", "emoji": "🎣"},
                {"role": "newbie", "content": "어떻게 알아볼 수 있나요?", "emoji": "🔍"},
                {"role": "veteran", "content": "갑자기 거래량이 폭증하거나, 이유 없이 급등하거나, 공시 없이 소문만 무성하면 의심하세요.", "emoji": "🚨"},
                {"role": "newbie", "content": "잡혀있으면 어떡하죠?", "emoji": "😰"},
                {"role": "veteran", "content": "손실이 크지 않다면 빨리 나오세요. 세력주는 결국 폭락합니다. 정석으로 투자하세요!", "emoji": "🏃"},
            ]
        },
        {
            "title": "리밸런싱 타이밍",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "investor", "content": "리밸런싱이 뭔가요?", "emoji": "⚖️"},
                {"role": "planner", "content": "포트폴리오의 비중을 재조정하는 거예요. 주식이 너무 올랐으면 일부 팔고 채권을 사는 식이죠.", "emoji": "🔄"},
                {"role": "investor", "content": "언제 해야 하나요?", "emoji": "📅"},
                {"role": "planner", "content": "목표 비중에서 5-10% 이상 벗어났을 때나, 정기적으로 분기/반기마다 하세요.", "emoji": "⏰"},
                {"role": "investor", "content": "꼭 해야 하나요?", "emoji": "🤔"},
                {"role": "planner", "content": "네! 수익은 실현하고, 위험은 관리하는 중요한 습관이에요. 안 하면 편중 위험이 커집니다.", "emoji": "🎯"},
            ]
        },
        {
            "title": "좋은 종목 찾는 체크리스트",
            "level": "elementary",
            "category": "팁",
            "messages": [
                {"role": "student", "content": "종목을 고를 때 뭘 봐야 하나요?", "emoji": "📋"},
                {"role": "teacher", "content": "1) 이해할 수 있는 사업인지 2) 실적이 꾸준히 성장하는지 3) 부채가 적은지 4) 배당은 있는지 확인하세요.", "emoji": "✅"},
                {"role": "student", "content": "전부 다 완벽한 종목은 없을 것 같은데요?", "emoji": "🤷"},
                {"role": "teacher", "content": "맞아요. 완벽한 종목은 없죠. 4가지 중 3가지 이상 만족하면 투자를 고려할 만 합니다.", "emoji": "👍"},
                {"role": "student", "content": "주가가 너무 비싸면요?", "emoji": "💰"},
                {"role": "teacher", "content": "PER, PBR로 밸류에이션을 확인하세요. 좋은 기업이라도 비싸게 사면 수익이 적어요.", "emoji": "🏷️"},
            ]
        },

        # Intermediate - 분석기법 (18개)
        {
            "title": "ROE 제대로 이해하기",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "analyst", "content": "ROE가 뭔가요?", "emoji": "📊"},
                {"role": "expert", "content": "자기자본이익률이에요. 주주가 투자한 돈으로 얼마나 이익을 냈는지 보는 지표죠. ROE=당기순이익/자기자본*100", "emoji": "💡"},
                {"role": "analyst", "content": "몇 %면 좋은 건가요?", "emoji": "🎯"},
                {"role": "expert", "content": "업종마다 다르지만 일반적으로 10% 이상이면 양호, 15% 이상이면 우수합니다.", "emoji": "📈"},
                {"role": "analyst", "content": "ROE만 보면 되나요?", "emoji": "❓"},
                {"role": "expert", "content": "아니요! 부채로 ROE를 높일 수도 있어요. 부채비율도 함께 확인해야 합니다.", "emoji": "⚠️"},
            ]
        },
        {
            "title": "현금흐름표 읽기",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "student", "content": "손익계산서랑 현금흐름표가 뭐가 다른가요?", "emoji": "📄"},
                {"role": "professor", "content": "손익계산서는 회계상 이익, 현금흐름표는 실제 돈의 움직임을 보여줘요. 실질적 건강도는 현금흐름이 중요하죠.", "emoji": "💰"},
                {"role": "student", "content": "어떤 걸 봐야 하나요?", "emoji": "🔍"},
                {"role": "professor", "content": "영업활동 현금흐름이 플러스인지 확인하세요. 돈을 벌고 있다는 뜻이에요.", "emoji": "✅"},
                {"role": "student", "content": "마이너스면 망하는 건가요?", "emoji": "😰"},
                {"role": "professor", "content": "단기간은 괜찮지만 지속되면 위험해요. 투자나 대출로 버티는 거라 주의가 필요합니다.", "emoji": "🚨"},
            ]
        },
        {
            "title": "PER과 PBR 활용법",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "investor", "content": "PER이 낮으면 무조건 싼 거예요?", "emoji": "🏷️"},
                {"role": "analyst", "content": "아니요! 낮은 이유가 중요해요. 실적 악화로 낮을 수도 있거든요. 동종업계 평균과 비교하세요.", "emoji": "📊"},
                {"role": "investor", "content": "PBR은 뭐가 다른가요?", "emoji": "❓"},
                {"role": "analyst", "content": "PBR은 순자산 대비 주가예요. 1 미만이면 회사를 청산해도 이득이란 뜻이죠. 저평가 신호입니다.", "emoji": "💎"},
                {"role": "investor", "content": "둘 다 낮으면 무조건 사야겠네요?", "emoji": "🤔"},
                {"role": "analyst", "content": "함정일 수도 있어요! 실적 추이, 산업 전망, 경영진 능력도 함께 봐야 합니다. 저PER·PBR에는 이유가 있어요.", "emoji": "🎯"},
            ]
        },
        {
            "title": "차트 기본: 지지선과 저항선",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "trader", "content": "지지선이랑 저항선이 뭔가요?", "emoji": "📈"},
                {"role": "technician", "content": "지지선은 주가가 떨어지다가 반등하는 가격대, 저항선은 오르다가 막히는 가격대예요.", "emoji": "📊"},
                {"role": "trader", "content": "왜 생기나요?", "emoji": "❓"},
                {"role": "technician", "content": "많은 투자자가 그 가격에서 사거나 팔려고 하기 때문이에요. 심리적 저항이죠.", "emoji": "🧠"},
                {"role": "trader", "content": "어떻게 활용하나요?", "emoji": "💡"},
                {"role": "technician", "content": "지지선 근처에서 매수, 저항선 근처에서 매도를 고려해요. 돌파하면 추세가 바뀔 신호입니다!", "emoji": "🎯"},
            ]
        },
        {
            "title": "이동평균선 활용하기",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "beginner", "content": "이동평균선이 뭔가요?", "emoji": "📉"},
                {"role": "expert", "content": "일정 기간의 평균 주가를 선으로 이은 거예요. 5일, 20일, 60일선 등이 있죠.", "emoji": "📊"},
                {"role": "beginner", "content": "어떻게 보나요?", "emoji": "🔍"},
                {"role": "expert", "content": "단기선이 장기선을 아래에서 위로 뚫으면 '골든크로스'로 매수 신호, 반대는 '데드크로스'로 매도 신호예요.", "emoji": "✨"},
                {"role": "beginner", "content": "100% 정확한가요?", "emoji": "🎯"},
                {"role": "expert", "content": "아니요. 후행지표라 늦을 수 있어요. 다른 지표들과 함께 종합적으로 판단하세요!", "emoji": "⚖️"},
            ]
        },
        {
            "title": "거래량 패턴 분석",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "student", "content": "거래량을 어떻게 분석하나요?", "emoji": "📊"},
                {"role": "teacher", "content": "상승과 함께 거래량 증가는 강세, 하락과 거래량 증가는 약세 신호예요. 추세의 힘을 보여줍니다.", "emoji": "💪"},
                {"role": "student", "content": "거래량 없이 오르면요?", "emoji": "📈"},
                {"role": "teacher", "content": "힘 없는 상승이라 반전 위험이 커요. 진정한 상승은 거래량이 뒷받침돼야 합니다.", "emoji": "⚠️"},
                {"role": "student", "content": "갑자기 거래량이 터지면요?", "emoji": "🚀"},
                {"role": "teacher", "content": "중요한 신호예요! 뉴스나 공시를 확인하세요. 큰 변화의 시작일 수 있습니다.", "emoji": "🔔"},
            ]
        },
        {
            "title": "부채비율 체크하기",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "analyst", "content": "부채비율은 어떻게 보나요?", "emoji": "📊"},
                {"role": "expert", "content": "부채비율=부채/자기자본*100이에요. 100% 미만이 안전, 200% 이상이면 위험 수준입니다.", "emoji": "⚖️"},
                {"role": "analyst", "content": "부채가 많으면 무조건 나쁜가요?", "emoji": "❓"},
                {"role": "expert", "content": "아니요! 성장 중인 기업은 투자를 위해 부채를 쓸 수 있어요. 중요한 건 이자 부담을 감당할 수 있는지예요.", "emoji": "💡"},
                {"role": "analyst", "content": "어떻게 확인하나요?", "emoji": "🔍"},
                {"role": "expert", "content": "이자보상배율을 보세요. 영업이익/이자비용이 3 이상이면 안정적입니다.", "emoji": "✅"},
            ]
        },
        {
            "title": "배당성향 분석",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "investor", "content": "배당성향이 뭔가요?", "emoji": "💰"},
                {"role": "advisor", "content": "순이익 중 몇 %를 배당으로 지급하는지 보는 지표예요. 배당성향=배당금/순이익*100", "emoji": "📊"},
                {"role": "investor", "content": "높을수록 좋은 거죠?", "emoji": "📈"},
                {"role": "advisor", "content": "꼭 그렇진 않아요. 너무 높으면(80% 이상) 재투자 여력이 없어 성장이 둔화될 수 있어요.", "emoji": "⚠️"},
                {"role": "investor", "content": "적정 수준은요?", "emoji": "🎯"},
                {"role": "advisor", "content": "30-50%가 적당해요. 배당도 주고 성장 투자도 하는 균형 잡힌 수준이죠.", "emoji": "⚖️"},
            ]
        },
        {
            "title": "산업 라이프사이클 이해",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "student", "content": "산업도 수명이 있나요?", "emoji": "🔄"},
                {"role": "professor", "content": "네! 도입→성장→성숙→쇠퇴 단계를 거쳐요. 단계마다 투자 전략이 달라야 합니다.", "emoji": "📊"},
                {"role": "student", "content": "어떻게 구분하나요?", "emoji": "❓"},
                {"role": "professor", "content": "성장률, 진입장벽, 경쟁 강도를 보세요. AI는 성장기, 자동차는 성숙기, 신문은 쇠퇴기죠.", "emoji": "🏭"},
                {"role": "student", "content": "쇠퇴 산업은 피해야 하나요?", "emoji": "🤔"},
                {"role": "professor", "content": "꼭 그렇진 않아요. 독점 기업이라면 안정적 배당주로 가치가 있을 수 있습니다.", "emoji": "💡"},
            ]
        },
        {
            "title": "컨센서스 활용법",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "trader", "content": "컨센서스가 뭔가요?", "emoji": "📋"},
                {"role": "analyst", "content": "증권사 애널리스트들의 평균 의견이에요. 실적 예상치, 목표주가 등을 제시하죠.", "emoji": "👔"},
                {"role": "trader", "content": "믿을 만한가요?", "emoji": "🤔"},
                {"role": "analyst", "content": "참고는 되지만 맹신하면 안 돼요. 실제 실적이 컨센서스를 상회/하회하는지가 중요합니다.", "emoji": "⚖️"},
                {"role": "trader", "content": "어디서 보나요?", "emoji": "🔍"},
                {"role": "analyst", "content": "증권사 리서치, FnGuide, 네이버 금융 등에서 확인할 수 있어요. 무료로도 볼 수 있죠!", "emoji": "💻"},
            ]
        },
        {
            "title": "공매도 잔고 활용",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "investor", "content": "공매도 잔고는 어떻게 활용하나요?", "emoji": "📊"},
                {"role": "expert", "content": "공매도 잔고가 많다는 건 하락 베팅이 많다는 뜻이에요. 역으로 반등 시 강한 상승('숏커버')이 올 수 있죠.", "emoji": "🚀"},
                {"role": "investor", "content": "몇 %면 많은 건가요?", "emoji": "🔢"},
                {"role": "expert", "content": "5% 이상이면 상당히 높은 편이에요. 10% 넘으면 숏스퀴즈 가능성이 커집니다.", "emoji": "📈"},
                {"role": "investor", "content": "어디서 확인하나요?", "emoji": "🔍"},
                {"role": "expert", "content": "한국거래소 홈페이지나 증권사 앱에서 일별로 공개돼요. 추이를 지켜보세요!", "emoji": "💻"},
            ]
        },
        {
            "title": "외국인·기관 수급 보기",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "beginner", "content": "외국인이 사면 오르나요?", "emoji": "🌍"},
                {"role": "expert", "content": "대체로 그래요. 외국인과 기관의 순매수는 긍정적 신호죠. 자금력이 크고 분석이 체계적이니까요.", "emoji": "💪"},
                {"role": "beginner", "content": "며칠 동안 봐야 하나요?", "emoji": "📅"},
                {"role": "expert", "content": "최소 1주일, 추세를 보려면 한 달 정도 관찰하세요. 하루 수급에 일희일비하지 마세요.", "emoji": "⏰"},
                {"role": "beginner", "content": "개미는 항상 반대로 하나요?", "emoji": "🤷"},
                {"role": "expert", "content": "꼭 그렇진 않지만, 역사적으로 외국인·기관과 반대 방향일 때가 많아요. 감정적 매매를 조심하세요!", "emoji": "⚠️"},
            ]
        },
        {
            "title": "신용융자 잔고 해석",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "student", "content": "신용융자가 뭔가요?", "emoji": "💰"},
                {"role": "teacher", "content": "돈을 빌려서 주식을 사는 거예요. 레버리지 투자죠. 융자 잔고가 많으면 낙관적 심리가 강하다는 뜻이에요.", "emoji": "📈"},
                {"role": "student", "content": "많으면 좋은 거네요?", "emoji": "😊"},
                {"role": "teacher", "content": "단기적으로는 그렇지만, 너무 많으면 위험해요. 하락 시 강제청산으로 급락할 수 있거든요.", "emoji": "⚠️"},
                {"role": "student", "content": "적정 수준은요?", "emoji": "🎯"},
                {"role": "teacher", "content": "시가총액 대비 5% 이내가 안전해요. 10% 넘으면 과열 신호로 봐야 합니다.", "emoji": "🔔"},
            ]
        },
        {
            "title": "재무비율 종합 분석",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "analyst", "content": "재무비율이 너무 많은데 뭘 봐야 하나요?", "emoji": "😵"},
                {"role": "expert", "content": "핵심 5가지만 보세요: ROE(수익성), 부채비율(안정성), 유동비율(유동성), PER(밸류에이션), 배당성향(주주환원)", "emoji": "📊"},
                {"role": "analyst", "content": "전부 좋아야 하나요?", "emoji": "✅"},
                {"role": "expert", "content": "완벽한 기업은 없어요. 산업 특성에 따라 중요도가 달라요. IT는 성장성, 금융은 안정성이 중요하죠.", "emoji": "🏭"},
                {"role": "analyst", "content": "과거 추이도 봐야 하나요?", "emoji": "📈"},
                {"role": "expert", "content": "네! 3-5년 추세를 보세요. 개선 중인지, 악화 중인지가 현재 숫자보다 중요할 수 있어요.", "emoji": "🔍"},
            ]
        },
        {
            "title": "업종 순환 투자",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "investor", "content": "업종 순환이 뭔가요?", "emoji": "🔄"},
                {"role": "strategist", "content": "경기 사이클에 따라 잘 나가는 업종이 바뀌는 거예요. 초기엔 IT, 중기엔 경기소비재, 후기엔 필수소비재가 강세죠.", "emoji": "📊"},
                {"role": "investor", "content": "지금 어느 국면인지 어떻게 아나요?", "emoji": "❓"},
                {"role": "strategist", "content": "경제지표(GDP, 금리, 고용)와 시장 움직임을 보세요. 전문가들의 분석도 참고하고요.", "emoji": "📈"},
                {"role": "investor", "content": "한 업종만 하면 안 되나요?", "emoji": "🤔"},
                {"role": "strategist", "content": "위험해요! 순환에 맞춰 비중을 조절하되, 기본적으로는 업종 분산을 유지하세요.", "emoji": "🎯"},
            ]
        },
        {
            "title": "시가총액으로 종목 분류",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "beginner", "content": "대형주, 중소형주 차이가 뭔가요?", "emoji": "📏"},
                {"role": "advisor", "content": "시가총액 기준이에요. 대형주는 5조 이상, 중형주는 1-5조, 소형주는 1조 미만 정도로 나눠요.", "emoji": "💰"},
                {"role": "beginner", "content": "어느 게 나은가요?", "emoji": "⚖️"},
                {"role": "advisor", "content": "대형주는 안정적이지만 수익률이 낮고, 소형주는 변동성은 크지만 고수익 가능성이 있어요.", "emoji": "📊"},
                {"role": "beginner", "content": "초보자는요?", "emoji": "🌱"},
                {"role": "advisor", "content": "대형주 70%, 중형주 20%, 소형주 10% 정도로 시작하세요. 경험이 쌓이면 조절하고요!", "emoji": "🎯"},
            ]
        },
        {
            "title": "실적 발표 시즌 대응",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "trader", "content": "실적 발표 전에 사야 하나요, 후에 사야 하나요?", "emoji": "⏰"},
                {"role": "expert", "content": "실적이 확실하면 발표 후가 안전해요. 서프라이즈 기대하면 전에 사되, 리스크를 감수해야죠.", "emoji": "🎲"},
                {"role": "trader", "content": "실적이 좋은데 주가가 떨어지는 이유는요?", "emoji": "📉"},
                {"role": "expert", "content": "'소식에 사서 뉴스에 팔아라'는 격언처럼 이미 반영됐거나, 기대치보다 낮았을 수 있어요.", "emoji": "💭"},
                {"role": "trader", "content": "실적 시즌엔 어떻게 해야 하나요?", "emoji": "📅"},
                {"role": "expert", "content": "보유 종목의 실적 발표 일정을 체크하고, 컨센서스와 비교 준비를 하세요. 급변동에 대비하고요!", "emoji": "✅"},
            ]
        },
        {
            "title": "가치주 vs 성장주 전략",
            "level": "intermediate",
            "category": "분석기법",
            "messages": [
                {"role": "investor", "content": "가치주랑 성장주 뭐가 다른가요?", "emoji": "❓"},
                {"role": "analyst", "content": "가치주는 저평가된 안정적 기업, 성장주는 고성장 가능성이 높은 기업이에요. 투자 접근이 달라요.", "emoji": "📊"},
                {"role": "investor", "content": "어느 게 나아요?", "emoji": "⚖️"},
                {"role": "analyst", "content": "시장 상황에 따라 달라요. 경기 불황엔 가치주, 호황엔 성장주가 유리한 경향이 있죠.", "emoji": "🔄"},
                {"role": "investor", "content": "둘 다 담으면요?", "emoji": "🤔"},
                {"role": "analyst", "content": "좋은 전략이에요! 60:40 정도로 분산하면 위험을 줄이면서 기회를 잡을 수 있습니다.", "emoji": "🎯"},
            ]
        },
    ]

    try:
        for i, article_data in enumerate(articles, 1):
            article = EducationArticle(
                title=article_data["title"],
                level=article_data["level"],
                category=article_data["category"],
                content=json.dumps(article_data["messages"], ensure_ascii=False),
                views=0
            )
            db.add(article)
            db.commit()
            print(f"✅ Created ({i}/{len(articles)}): {article.title} ({article.level} - {article.category}) - {len(article_data['messages'])} messages")

        print(f"\n✨ Successfully created {len(articles)} additional articles!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_articles()
