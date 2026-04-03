import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from utils.data_manager import get_diaries, load_dummy_data
from utils.book_api import (
    get_book_templates, estimate_book_cost, validate_diary_selection, get_photobook_specs,
    create_book_with_diaries, get_book_estimate, create_book_order
)
from datetime import datetime

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
    print(f"[DEBUG] 포토북 생성 요청 받음 - selected_diaries: '{selected_diaries}'")
    try:
        # 선택된 일기 ID 파싱
        if not selected_diaries.strip():
            print("[DEBUG] 선택된 일기가 없음 - 홈으로 리다이렉트")
            return RedirectResponse(url="/?error=no_selection", status_code=303)
        
        selected_ids = [id.strip() for id in selected_diaries.split(',') if id.strip()]
        selected_count = len(selected_ids)
        print(f"[DEBUG] 파싱된 일기 ID들: {selected_ids}")
        print(f"[DEBUG] 선택된 일기 개수: {selected_count}")
        
        # 선택 개수 검증
        validation = validate_diary_selection(selected_count)
        print(f"[DEBUG] 검증 결과: {validation}")
        if not validation["valid"]:
            error_msg = validation["message"].replace(" ", "_")
            print(f"[DEBUG] 검증 실패 - 홈으로 리다이렉트: {error_msg}")
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
        print(f"[DEBUG] 미리보기 페이지로 리다이렉트: /preview?selected={selected_ids_str}")
        return RedirectResponse(url=f"/preview?selected={selected_ids_str}", status_code=303)
        
    except Exception as e:
        print(f"[ERROR] 포토북 생성 중 오류: {e}")
        return RedirectResponse(url="/?error=server_error", status_code=303)

@app.get("/preview", response_class=HTMLResponse)
async def preview_photobook(request: Request, selected: str = None, error: str = None):
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
        
        # 검증
        validation = validate_diary_selection(selected_count)
        specs = get_photobook_specs()
        templates_list = get_book_templates()
        
        # 실제 포토북 생성 및 견적 조회 시도
        print(f"[DEBUG] 실제 포토북 생성 시도 - 선택된 일기 수: {selected_count}")
        book_success, book_result = create_book_with_diaries(selected_diaries_data)
        
        if book_success and "book_id" in book_result:
            # 실제 견적 조회
            print(f"[DEBUG] 견적 조회 시도 - Book ID: {book_result['book_id']}")
            estimate_success, cost_info = get_book_estimate(book_result["book_id"])
            
            if not estimate_success:
                print(f"[WARNING] 견적 조회 실패, 임시 추정 사용: {cost_info}")
                cost_info = estimate_book_cost(selected_count)
        else:
            # 포토북 생성 실패 시 임시 추정 사용
            print(f"[WARNING] 포토북 생성 실패, 임시 추정 사용: {book_result}")
            cost_info = estimate_book_cost(selected_count)
        
        # 상태 메시지 생성
        status_info = {
            "type": "success",
            "message": "제작 가능",
            "description": ""
        }
        
        if selected_count < 22:
            status_info = {
                "type": "error",
                "message": "제작 불가",
                "description": f"최소 22개 일기가 필요합니다. (현재: {selected_count}개)"
            }
        elif selected_count > 128:
            status_info = {
                "type": "error", 
                "message": "제작 불가",
                "description": f"최대 128개까지 선택 가능합니다. (현재: {selected_count}개)"
            }
        elif 30 <= selected_count <= 50:
            status_info = {
                "type": "recommended",
                "message": "권장 범위",
                "description": f"최적의 포토북 분량입니다. ({selected_count}개 선택)"
            }
        elif 22 <= selected_count < 30:
            status_info = {
                "type": "warning",
                "message": "제작 가능",
                "description": f"권장 범위보다 적습니다. (권장: 30~50개)"
            }
        else:  # 51~128개
            status_info = {
                "type": "warning",
                "message": "제작 가능",
                "description": f"권장 범위보다 많습니다. (권장: 30~50개)"
            }
        
        print(f"[DEBUG] Preview 페이지 렌더링 - 선택 개수: {selected_count}, 상태: {status_info['type']}")
        
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
                "selected_ids": selected_ids,
                "status_info": status_info,
                "error_message": error  # 에러 메시지 추가
            }
        )
        
    except Exception as e:
        print(f"[ERROR] 미리보기 페이지 로드 중 오류: {e}")
        return RedirectResponse(url="/?error=preview_error", status_code=303)

@app.post("/success", response_class=HTMLResponse)
async def create_order(request: Request, 
                      selected_diaries: str = Form(...),
                      template_id: str = Form(...),
                      page_count: int = Form(...),
                      total_cost: int = Form(...)):
    """실제 주문 생성 및 완료 페이지"""
    try:
        print(f"[DEBUG] 주문 생성 요청 - 선택된 일기: {selected_diaries}")
        
        # 선택된 일기 데이터 파싱
        selected_ids = [id.strip() for id in selected_diaries.split(',') if id.strip()]
        all_diaries = get_diaries()
        selected_diaries_data = []
        
        for diary in all_diaries:
            if str(diary["id"]) in selected_ids:
                selected_diaries_data.append(diary)
        
        if not selected_diaries_data:
            print("[ERROR] 선택된 일기 데이터를 찾을 수 없음")
            return RedirectResponse(url="/?error=no_diaries", status_code=303)
        
        # 실제 포토북 생성
        print(f"[DEBUG] 포토북 생성 시작 - 일기 수: {len(selected_diaries_data)}")
        book_success, book_result = create_book_with_diaries(selected_diaries_data, template_id)
        
        if not book_success:
            print(f"[ERROR] 포토북 생성 실패: {book_result}")
            # 포토북 생성 실패 시 preview로 리다이렉트 (에러 메시지 포함)
            error_msg = book_result.get("error", "포토북 생성에 실패했습니다.")
            return RedirectResponse(
                url=f"/preview?selected={selected_diaries}&error={error_msg}", 
                status_code=303
            )
        
        book_id = book_result["book_id"]
        print(f"[DEBUG] 포토북 생성 완료 - Book ID: {book_id}")
        
        # TODO: 실제 서비스에서는 사용자 입력 폼에서 배송 정보를 받아야 함
        shipping_info = {
            "name": "테스트 사용자",
            "address": "서울시 테스트구 테스트동 123-45", 
            "phone": "010-0000-0000",
            "email": "test@example.com"
        }
        
        # 실제 주문 생성
        print(f"[DEBUG] 주문 생성 시작 - Book ID: {book_id}")
        order_success, order_result = create_book_order(book_id, shipping_info)
        
        if not order_success:
            print(f"[ERROR] 주문 생성 실패: {order_result}")
            # 주문 생성 실패 시 preview로 리다이렉트 (에러 메시지 포함)
            error_msg = order_result.get("error", "주문 생성에 실패했습니다.")
            return RedirectResponse(
                url=f"/preview?selected={selected_diaries}&error={error_msg}", 
                status_code=303
            )
        
        print(f"[DEBUG] 주문 생성 완료 - Order ID: {order_result.get('order_id')}")
        
        # 성공 페이지 렌더링 - 실제 API 응답 데이터 사용
        return templates.TemplateResponse(
            request=request,
            name="success.html",
            context={
                "page_title": "포토북 주문 완료",
                "success": True,
                "book_uid": book_id,
                "order_uid": order_result.get("order_id"),
                "order_status": order_result.get("status", "PENDING"),
                "order_status_display": order_result.get("status_display", "주문 접수됨"),
                "selected_count": len(selected_diaries_data),
                "page_count": page_count,
                "total_cost": order_result.get("total_price", total_cost),
                "book_title": book_result.get("title", "나의 일기 포토북"),
                "template_id": template_id,
                "shipping_info": shipping_info,
                "created_at": order_result.get("created_at", datetime.now().isoformat())
            }
        )
        
    except Exception as e:
        print(f"[ERROR] 주문 처리 중 오류: {e}")
        # 예외 발생 시 preview로 리다이렉트 (에러 메시지 포함)
        error_msg = f"주문 처리 중 오류가 발생했습니다: {str(e)}"
        return RedirectResponse(
            url=f"/preview?selected={selected_diaries}&error={error_msg}", 
            status_code=303
        )

@app.get("/success", response_class=HTMLResponse)
async def order_success_get(request: Request):
    """GET 요청으로 접근 시 홈으로 리다이렉트"""
    return RedirectResponse(url="/", status_code=303)

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