"""Education API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.education import EducationArticle, UserProgress
import json

router = APIRouter(tags=["education"])


class ArticleCreate(BaseModel):
    """Schema for creating education article"""
    topic: str
    level: str
    category: str = "용어"


class ArticleResponse(BaseModel):
    """Schema for education article response"""
    id: int
    title: str
    category: str
    level: str
    content: str
    views: int
    created_at: str

    class Config:
        from_attributes = True


@router.get("/articles", response_model=List[ArticleResponse])
def get_articles(
    level: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all education articles with optional filters"""
    query = db.query(EducationArticle)
    
    if level:
        query = query.filter(EducationArticle.level == level)
    if category:
        query = query.filter(EducationArticle.category == category)
    
    articles = query.order_by(desc(EducationArticle.created_at)).all()
    
    return [
        ArticleResponse(
            id=article.id,
            title=article.title,
            category=article.category,
            level=article.level,
            content=article.content,
            views=article.views,
            created_at=article.created_at.isoformat() if article.created_at else ""
        )
        for article in articles
    ]


@router.get("/articles/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get specific education article and increment views"""
    article = db.query(EducationArticle).filter(EducationArticle.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment views
    article.views += 1
    db.commit()
    db.refresh(article)
    
    return ArticleResponse(
        id=article.id,
        title=article.title,
        category=article.category,
        level=article.level,
        content=article.content,
        views=article.views,
        created_at=article.created_at.isoformat() if article.created_at else ""
    )


@router.post("/articles/generate")
async def generate_article(request: ArticleCreate, db: Session = Depends(get_db)):
    """Generate AI education article"""
    import anthropic
    import os
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="AI API key not configured")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Create prompt for AI
    prompt = f"""당신은 투자 교육 전문가입니다. 다음 주제에 대해 {request.level} 수준의 교육 콘텐츠를 생성해주세요.

주제: {request.topic}
카테고리: {request.category}
레벨: {request.level}

대화 형식으로 학생과 선생님의 질문-답변 형태로 작성해주세요.
JSON 형식으로 응답해주세요:

{{
    "title": "강의 제목 (간단명료하게)",
    "messages": [
        {{"role": "student", "content": "질문 내용", "emoji": "🤔"}},
        {{"role": "teacher", "content": "답변 내용", "emoji": "👨‍🏫"}},
        ...
    ]
}}

레벨별 가이드:
- beginner: 매우 기초적인 용어와 개념, 일상 비유 사용
- elementary: 기본 개념과 원리, 간단한 예시
- intermediate: 실전 응용과 전략, 구체적 사례
- advanced: 심화 분석과 고급 기법, 복잡한 상황 대응

최소 4개 이상의 메시지를 작성하고, 자연스러운 대화 흐름을 유지해주세요."""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]
        ai_response = json.loads(json_str)
        
        # Create article in database
        article = EducationArticle(
            title=ai_response["title"],
            category=request.category,
            level=request.level,
            content=json.dumps(ai_response["messages"], ensure_ascii=False),
            views=0
        )
        
        db.add(article)
        db.commit()
        db.refresh(article)
        
        return {
            "success": True,
            "article": ArticleResponse(
                id=article.id,
                title=article.title,
                category=article.category,
                level=article.level,
                content=article.content,
                views=article.views,
                created_at=article.created_at.isoformat() if article.created_at else ""
            )
        }
    
    except Exception as e:
        print(f"Error generating article: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate article: {str(e)}")


@router.post("/progress/{article_id}")
def mark_as_viewed(article_id: int, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Mark article as viewed"""
    progress = UserProgress(user_id=user_id, article_id=article_id)
    db.add(progress)
    db.commit()
    
    return {"success": True}


@router.delete("/articles/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    """Delete education article"""
    article = db.query(EducationArticle).filter(EducationArticle.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    db.delete(article)
    db.commit()
    
    return {"success": True}
