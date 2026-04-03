import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from utils.data_manager import get_diaries, load_dummy_data
from utils.book_api import get_book_templates, estimate_book_cost, validate_diary_selection, get_photobook_specs

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

@app.post("/create-photobook", response_class=HTMLResponse)
async def create_photobook(request: Request, selected_diaries: str = Form(...)):
    """선택된 일기들로 포토북 생성"""
    try:
        # 선택된 일기 ID 파싱
        if not selected_diaries.strip():
            return RedirectResponse(url="/?error=no_selection", status_code=303)
        
        selected_ids = [id.strip() for id in selected_diaries.split(',') if id.strip()]
        selected_count = len(selected_ids)
        
        # 선택 개수 검증
        validation = validate_diary_selection(selected_count)
        if not validation["valid"]:
            error_msg = validation["message"].replace(" ", "_")
            return RedirectResponse(url=f"/?error={error_msg}", status_code=303)
        
        # 선택된 일기 데이터 가져오기
        all_diaries = get_diaries()
        selected_diaries_data = []
        
        for diary in all_diaries:
            if str(diary["id"]) in selected_ids:
                selected_diaries_data.append(diary)
        
        # 실제 선택된 일기 수와 요청된 수가 다르면 에러
        if len(selected_diaries_data) != selected_count:
            return RedirectResponse(url="/?error=invalid_selection", status_code=303)
        
        # 미리보기 페이지로 리다이렉트 (쿼리 파라미터 사용)
        selected_ids_str = ','.join(selected_ids)
        return RedirectResponse(url=f"/preview?selected={selected_ids_str}", status_code=303)
        
    except Exception as e:
        print(f"[ERROR] 포토북 생성 중 오류: {e}")
        return RedirectResponse(url="/?error=server_error", status_code=303)

@app.get("/preview", response_class=HTMLResponse)
async def preview_photobook(request: Request, selected: str = None):
    """포토북 미리보기 페이지"""
    if not selected:
        # 선택된 일기가 없으면 홈으로 리다이렉트
        return RedirectResponse(url="/", status_code=303)
    
    try:
        # 선택된 일기 ID 파싱
        selected_ids = [id.strip() for id in selected.split(',') if id.strip()]
        selected_count = len(selected_ids)
        
        # 선택된 일기 데이터 가져오기
        all_diaries = get_diaries()
        selected_diaries_data = []
        
        for diary in all_diaries:
            if str(diary["id"]) in selected_ids:
                selected_diaries_data.append(diary)
        
        # 검증 및 비용 계산
        validation = validate_diary_selection(selected_count)
        cost_info = estimate_book_cost(selected_count)
        specs = get_photobook_specs()
        templates_list = get_book_templates()
        
        return templates.TemplateResponse(
            request=request,
            name="preview.html",
            context={
                "page_title": "포토북 미리보기",
                "selected_diaries": selected_diaries_data,
                "selected_count": selected_count,
                "validation": validation,
                "cost_info": cost_info,
                "specs": specs,
                "templates": templates_list,
                "selected_ids": selected_ids
            }
        )
        
    except Exception as e:
        print(f"[ERROR] 미리보기 페이지 로드 중 오류: {e}")
        return RedirectResponse(url="/?error=preview_error", status_code=303)

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