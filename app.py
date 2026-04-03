import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from utils.data_manager import get_diaries, load_dummy_data
from utils.book_api import get_book_templates, estimate_book_cost

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="개인 일기 포토북 서비스",
    description="일상의 소중한 순간을 기록한 일기와 사진을 아름다운 포토북으로 제작하는 서비스",
    version="1.0.0"
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지 - 일기 목록 표시"""
    diaries = get_diaries()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "diaries": diaries,
            "page_title": "나의 일기 포토북"
        }
    )

@app.get("/write", response_class=HTMLResponse)
async def write_diary(request: Request):
    """일기 작성 페이지"""
    return templates.TemplateResponse(
        request=request,
        name="write.html",
        context={
            "page_title": "새 일기 작성"
        }
    )

@app.get("/preview", response_class=HTMLResponse)
async def preview_photobook(request: Request):
    """포토북 미리보기 페이지"""
    templates_list = get_book_templates()
    cost_info = estimate_book_cost({})
    
    return templates.TemplateResponse(
        request=request,
        name="preview.html",
        context={
            "page_title": "포토북 미리보기",
            "templates": templates_list,
            "cost_info": cost_info
        }
    )

@app.get("/success", response_class=HTMLResponse)
async def order_success(request: Request):
    """주문 완료 페이지"""
    return templates.TemplateResponse(
        request=request,
        name="success.html",
        context={
            "page_title": "주문 완료"
        }
    )

@app.get("/api/diaries")
async def api_get_diaries():
    """API: 일기 목록 조회"""
    return {"diaries": get_diaries()}

@app.get("/api/data")
async def api_get_all_data():
    """API: 전체 더미 데이터 조회 (디버깅용)"""
    return load_dummy_data()

if __name__ == "__main__":
    import uvicorn
    print("🚀 개인 일기 포토북 서비스를 시작합니다...")
    print("📖 브라우저에서 http://127.0.0.1:8000 으로 접속하세요")
    print("🛑 서버를 종료하려면 Ctrl+C를 누르세요")
    
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )