import os
import shutil
import uuid
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from utils.data_manager import (
    get_diaries,
    load_dummy_data,
    add_diary,
    get_diary_by_id,
    delete_diary,
    update_diary,
    try_delete_upload_rel_path,
)
from utils.book_api import (
    get_book_templates,
    validate_diary_selection,
    get_photobook_specs,
    create_book_order,
    get_photobook_quote,
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

# 주문 완료 화면 PRG(POST → Redirect → GET)용 세션
_session_secret = os.getenv("SESSION_SECRET_KEY", "").strip()
if not _session_secret:
    _session_secret = "dev-only-insecure-session-key-change-in-production-32chars"
app.add_middleware(SessionMiddleware, secret_key=_session_secret)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")

ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}


def save_diary_image_file(image: UploadFile | None) -> tuple[str | None, str | None]:
    """
    업로드 이미지를 static/uploads/ 에 저장합니다.
    반환: (상대경로, 에러메시지). 업로드 없음 → (None, None). 실패 → (None, str).
    """
    if image is None or not image.filename or not str(image.filename).strip():
        return None, None
    suffix = Path(image.filename).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXT:
        return None, "이미지는 jpg, jpeg, png, webp 만 업로드할 수 있습니다."
    safe_ext = suffix if suffix else ".jpg"
    unique = f"{uuid.uuid4().hex}{safe_ext}"
    upload_dir = Path(__file__).resolve().parent / "static" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / unique
    with dest.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return f"static/uploads/{unique}", None


def _write_page_defaults() -> dict:
    return {
        "is_edit": False,
        "form_action": "/write",
        "submit_label": "저장하기",
        "page_heading": "새 일기 작성",
        "page_subtitle": "오늘의 소중한 순간을 기록해보세요",
        "existing_image_path": "",
        "diary_id": None,
    }


def _edit_page_context(
    diary_id: int,
    *,
    error_message: str | None = None,
    form_title: str = "",
    form_date: str = "",
    form_content: str = "",
    existing_image_path: str = "",
) -> dict:
    return {
        **(
            _write_page_defaults()
            | {
                "page_title": "일기 수정",
                "is_edit": True,
                "form_action": f"/diaries/{diary_id}/edit",
                "submit_label": "수정 반영",
                "page_heading": "일기 수정",
                "page_subtitle": "내용을 수정한 뒤 저장하세요.",
                "diary_id": diary_id,
                "form_title": form_title,
                "form_date": form_date,
                "form_content": form_content,
                "existing_image_path": existing_image_path or "",
                "error_message": error_message,
            }
        )
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지 - 일기 목록 표시"""
    diaries = get_diaries()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "diaries": diaries,
            "page_title": "나의 일기 포토북",
            "saved": request.query_params.get("saved"),
            "deleted": request.query_params.get("deleted"),
            "updated": request.query_params.get("updated"),
            "error_q": request.query_params.get("error"),
        }
    )


@app.get("/write", response_class=HTMLResponse)
async def write_diary_get(request: Request):
    """일기 작성 페이지"""
    success = request.query_params.get("success")
    err_q = request.query_params.get("error")
    today = datetime.now().date().isoformat()
    return templates.TemplateResponse(
        request=request,
        name="write.html",
        context={
            **_write_page_defaults(),
            "page_title": "새 일기 작성",
            "today": today,
            "success": success,
            "error_message": err_q,
            "form_title": "",
            "form_date": "",
            "form_content": "",
        }
    )


@app.post("/write", response_class=HTMLResponse)
async def write_diary_post(
    request: Request,
    title: str = Form(...),
    date: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
):
    """일기 저장: JSON 반영 + 선택적 이미지를 static/uploads/ 에 저장"""
    print("[DEBUG] === /write POST 진입 ===")
    print(f"[DEBUG] title={title!r}, date={date!r}, content_len={len(content or '')}")
    title = (title or "").strip()
    date = (date or "").strip()
    content = (content or "").strip()

    base_ctx = {
        **_write_page_defaults(),
        "page_title": "새 일기 작성",
        "today": datetime.now().date().isoformat(),
    }

    if not title or not date or not content:
        return templates.TemplateResponse(
            request=request,
            name="write.html",
            context={
                **base_ctx,
                "error_message": "제목, 날짜, 내용을 모두 입력해주세요.",
                "form_title": title,
                "form_date": date,
                "form_content": content,
            },
        )

    if len(content) > 600:
        return templates.TemplateResponse(
            request=request,
            name="write.html",
            context={
                **base_ctx,
                "error_message": "본문은 600자 이내로 입력해주세요.",
                "form_title": title,
                "form_date": date,
                "form_content": content,
            },
        )

    img_saved, img_err = save_diary_image_file(image)
    if img_err:
        return templates.TemplateResponse(
            request=request,
            name="write.html",
            context={
                **base_ctx,
                "error_message": img_err,
                "form_title": title,
                "form_date": date,
                "form_content": content,
            },
        )

    image_relpath = img_saved or ""

    try:
        print("[DEBUG] add_diary 호출 직전")
        add_diary(title=title, content=content, date=date, image_path=image_relpath)
        print("[DEBUG] add_diary 호출 완료")
    except Exception as e:
        print(f"[ERROR] 일기 저장 실패: {e}")
        if img_saved:
            try_delete_upload_rel_path(img_saved)
        return templates.TemplateResponse(
            request=request,
            name="write.html",
            context={
                **base_ctx,
                "error_message": "저장 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "form_title": title,
                "form_date": date,
                "form_content": content,
            },
        )

    print("[DEBUG] RedirectResponse → /?saved=1 (303)")
    return RedirectResponse(url="/?saved=1", status_code=303)


@app.post("/diaries/delete")
async def diary_delete_post(diary_id: int = Form(...)):
    """일기 삭제 (POST만 허용)"""
    if delete_diary(diary_id):
        return RedirectResponse(url="/?deleted=1", status_code=303)
    return RedirectResponse(url="/?error=delete_failed", status_code=303)


@app.get("/diaries/{diary_id}/edit", response_class=HTMLResponse)
async def edit_diary_get(request: Request, diary_id: int):
    diary = get_diary_by_id(diary_id)
    if not diary:
        return RedirectResponse(url="/?error=not_found", status_code=303)
    ctx = _edit_page_context(
        diary_id,
        form_title=diary.get("title") or "",
        form_date=diary.get("date") or "",
        form_content=diary.get("content") or "",
        existing_image_path=(diary.get("image_path") or "").strip(),
    )
    ctx["today"] = datetime.now().date().isoformat()
    ctx["success"] = None
    return templates.TemplateResponse(request=request, name="write.html", context=ctx)


@app.post("/diaries/{diary_id}/edit", response_class=HTMLResponse)
async def edit_diary_post(
    request: Request,
    diary_id: int,
    title: str = Form(...),
    date: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),
):
    diary = get_diary_by_id(diary_id)
    if not diary:
        return RedirectResponse(url="/?error=not_found", status_code=303)

    title = (title or "").strip()
    date = (date or "").strip()
    content = (content or "").strip()
    existing_img = (diary.get("image_path") or "").strip()

    def err_response(msg: str) -> HTMLResponse:
        ctx = _edit_page_context(
            diary_id,
            error_message=msg,
            form_title=title,
            form_date=date,
            form_content=content,
            existing_image_path=existing_img,
        )
        ctx["today"] = datetime.now().date().isoformat()
        ctx["success"] = None
        return templates.TemplateResponse(request=request, name="write.html", context=ctx)

    if not title or not date or not content:
        return err_response("제목, 날짜, 내용을 모두 입력해주세요.")
    if len(content) > 600:
        return err_response("본문은 600자 이내로 입력해주세요.")

    img_saved, img_err = save_diary_image_file(image)
    if img_err:
        return err_response(img_err)

    updated = update_diary(
        diary_id,
        title,
        content,
        date,
        new_image_relpath=img_saved if img_saved else None,
    )
    if updated is None:
        if img_saved:
            try_delete_upload_rel_path(img_saved)
        return RedirectResponse(url="/?error=update_failed", status_code=303)

    return RedirectResponse(url="/?updated=1", status_code=303)


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

def _preview_status_info(selected_count: int) -> dict:
    if selected_count < 22:
        return {
            "type": "error",
            "message": "제작 불가",
            "description": f"최소 22개 일기가 필요합니다. (현재: {selected_count}개)",
        }
    if selected_count > 128:
        return {
            "type": "error",
            "message": "제작 불가",
            "description": f"최대 128개까지 선택 가능합니다. (현재: {selected_count}개)",
        }
    if 30 <= selected_count <= 50:
        return {
            "type": "recommended",
            "message": "권장 범위",
            "description": f"최적의 포토북 분량입니다. ({selected_count}개 선택)",
        }
    if 22 <= selected_count < 30:
        return {
            "type": "warning",
            "message": "제작 가능",
            "description": f"권장 범위보다 적습니다. (권장: 30~50개)",
        }
    return {
        "type": "warning",
        "message": "제작 가능",
        "description": f"권장 범위보다 많습니다. (권장: 30~50개)",
    }


def _template_display_name(templates_list: list, template_id: str) -> str:
    for t in templates_list:
        if t.get("template_id") == template_id:
            return t.get("name") or template_id
    return template_id


def _render_preview(
    request: Request,
    selected: str,
    *,
    error_message: str | None = None,
    quote_error: str | None = None,
    show_quote_confirm: bool = False,
    quoted_price: int | None = None,
    quote_book_id: str | None = None,
    quote_page_count: int | None = None,
    quote_template_id: str | None = None,
    quote_book_title: str | None = None,
    quote_template_label: str | None = None,
):
    selected_ids = [s.strip() for s in selected.split(",") if s.strip()]
    selected_count = len(selected_ids)
    all_diaries = get_diaries()
    selected_diaries_data = []
    for diary in all_diaries:
        if str(diary["id"]) in selected_ids:
            selected_diaries_data.append(diary)

    validation = validate_diary_selection(selected_count)
    specs = get_photobook_specs()
    templates_list = get_book_templates()
    status_info = _preview_status_info(selected_count)
    selected_param = ",".join(selected_ids)

    ctx = {
        "page_title": "포토북 미리보기",
        "selected_diaries": selected_diaries_data,
        "selected_count": selected_count,
        "validation": validation,
        "specs": specs,
        "templates": templates_list,
        "selected_ids": selected_ids,
        "selected_param": selected_param,
        "status_info": status_info,
        "error_message": error_message,
        "quote_error": quote_error,
        "show_quote_confirm": show_quote_confirm,
        "quoted_price": quoted_price,
        "quote_book_id": quote_book_id or "",
        "quote_page_count": quote_page_count or 0,
        "quote_template_id": quote_template_id or "",
        "quote_book_title": quote_book_title or "",
        "quote_template_label": quote_template_label or "",
    }
    return templates.TemplateResponse(request=request, name="preview.html", context=ctx)


@app.get("/preview", response_class=HTMLResponse)
async def preview_photobook(request: Request, selected: str = None, error: str = None):
    """포토북 미리보기 페이지 (가격 미표시)"""
    if not selected:
        return RedirectResponse(url="/", status_code=303)

    try:
        selected_ids = [s.strip() for s in selected.split(",") if s.strip()]
        print(f"[DEBUG] Preview 페이지 - 선택 일기 수: {len(selected_ids)}")
        return _render_preview(request, selected, error_message=error)
    except Exception as e:
        print(f"[ERROR] 미리보기 페이지 로드 중 오류: {e}")
        return RedirectResponse(url="/?error=preview_error", status_code=303)


@app.post("/preview/quote", response_class=HTMLResponse)
async def preview_quote(
    request: Request,
    selected_diaries: str = Form(...),
    template_id: str = Form(...),
):
    """포토북 제작 요청: 책 준비 후 금액만 조회 (주문은 하지 않음)"""
    try:
        selected_ids = [s.strip() for s in selected_diaries.split(",") if s.strip()]
        selected_count = len(selected_ids)
        validation = validate_diary_selection(selected_count)
        if not validation["valid"]:
            return RedirectResponse(url="/?error=invalid_selection", status_code=303)

        all_diaries = get_diaries()
        selected_diaries_data = []
        for diary in all_diaries:
            if str(diary["id"]) in selected_ids:
                selected_diaries_data.append(diary)

        if len(selected_diaries_data) != selected_count:
            return _render_preview(
                request,
                selected_diaries,
                quote_error="선택한 일기를 다시 확인해주세요.",
            )

        ok, data = get_photobook_quote(selected_diaries_data, template_id)
        if not ok:
            return _render_preview(
                request,
                selected_diaries,
                quote_error=data.get(
                    "error",
                    "주문 금액을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.",
                ),
            )

        templates_list = get_book_templates()
        label = _template_display_name(templates_list, data["template_id"])

        return _render_preview(
            request,
            selected_diaries,
            show_quote_confirm=True,
            quoted_price=data["quoted_price"],
            quote_book_id=data["book_id"],
            quote_page_count=data["page_count"],
            quote_template_id=data["template_id"],
            quote_book_title=data["book_title"],
            quote_template_label=label,
        )
    except Exception as e:
        print(f"[ERROR] preview/quote 처리 중 오류: {e}")
        try:
            return _render_preview(
                request,
                selected_diaries,
                quote_error="주문 금액을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.",
            )
        except Exception:
            return RedirectResponse(url="/?error=preview_error", status_code=303)


@app.post("/orders/create", response_class=HTMLResponse)
async def orders_create(
    request: Request,
    book_id: str = Form(...),
    selected_diaries: str = Form(...),
    template_id: str = Form(...),
    page_count: int = Form(...),
    quoted_price: int = Form(...),
    book_title: str = Form(...),
):
    """금액 확인 후 실제 주문만 수행 (이미 준비된 책 ID 재사용)"""
    shipping_info = {
        "name": "테스트 사용자",
        "address": "서울특별시 강남구 테헤란로 123",
        "address2": "4층",
        "phone": "010-1234-5678",
        "postalCode": "06100",
        "memo": "부재 시 경비실",
    }

    try:
        bid = (book_id or "").strip()
        if not bid:
            return _render_preview(
                request,
                selected_diaries,
                error_message="주문 정보가 올바르지 않습니다. 처음부터 다시 진행해주세요.",
            )

        selected_ids = [s.strip() for s in selected_diaries.split(",") if s.strip()]
        all_diaries = get_diaries()
        selected_diaries_data = []
        for diary in all_diaries:
            if str(diary["id"]) in selected_ids:
                selected_diaries_data.append(diary)

        if not selected_diaries_data:
            return _render_preview(
                request,
                selected_diaries,
                error_message="선택한 일기를 찾을 수 없습니다. 메인에서 다시 선택해주세요.",
            )

        print(f"[DEBUG] 주문 생성 요청 - book_id={bid}, 일기 수={len(selected_diaries_data)}")
        order_success, order_result = create_book_order(bid, shipping_info)

        if not order_success:
            print(f"[ERROR] 주문 생성 실패: {order_result}")
            return _render_preview(
                request,
                selected_diaries,
                error_message="주문 처리에 실패했습니다. 잠시 후 다시 시도해주세요.",
            )

        print(f"[DEBUG] 주문 생성 완료 - Order ID: {order_result.get('order_id')}")

        try:
            api_total = int(order_result.get("total_price") or 0)
        except (TypeError, ValueError):
            api_total = 0
        try:
            confirmed = int(quoted_price)
        except (TypeError, ValueError):
            confirmed = 0
        # API가 totalPrice=0만 주거나 필드명이 다를 때 → 미리보기에서 확인한 금액 사용
        display_total = api_total if api_total > 0 else confirmed

        request.session["order_success"] = {
            "page_title": "포토북 주문 완료",
            "success": True,
            "book_uid": bid,
            "order_uid": order_result.get("order_id"),
            "order_status": order_result.get("status", "PENDING"),
            "order_status_display": order_result.get("status_display", "주문 접수됨"),
            "selected_count": len(selected_diaries_data),
            "page_count": page_count,
            "total_cost": display_total,
            "book_title": book_title.strip() or "나의 일기 포토북",
            "template_id": template_id,
            "shipping_info": shipping_info,
            "created_at": order_result.get("created_at", datetime.now().isoformat()),
        }
        return RedirectResponse(url="/success", status_code=303)
    except Exception as e:
        print(f"[ERROR] 주문 처리 중 오류: {e}")
        return _render_preview(
            request,
            selected_diaries,
            error_message="주문 처리에 실패했습니다. 잠시 후 다시 시도해주세요.",
        )

@app.get("/success", response_class=HTMLResponse)
async def order_success_get(request: Request):
    """주문 직후 GET 전용(PR). 세션에 저장된 완료 정보를 표시(새로고침 시에도 주문 API 재호출 없음)."""
    payload = request.session.get("order_success")
    if not payload:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="success.html",
        context=payload,
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