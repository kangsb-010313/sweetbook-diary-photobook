"""
BookPrint API 연동 모듈
실제 Sweetbook Book Print API SDK를 사용하여 포토북 생성 및 주문 처리
"""

import os
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# BookPrint API SDK import
try:
    from bookprintapi import Client, ApiError
    SDK_AVAILABLE = True
except ImportError:
    print("[WARNING] BookPrint API SDK를 찾을 수 없습니다.")
    SDK_AVAILABLE = False
    ApiError = Exception  # type: ignore

# 환경변수 로드
load_dotenv()

# 프로젝트 루트 (static/... 이미지 경로 해석용)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SDK 예제 examples/server_pipeline.py 과 동일 — SQUAREBOOK_HC 일기장A 템플릿 UID
TPL_COVER = "79yjMH3qRPly"
TPL_GANJI = "5M3oo7GlWKGO"
TPL_NAEJI = "5B4ds6i0Rywx"
TPL_PUBLISH = "5nhOVBjTnIVE"
TPL_BLANK = "2mi1ao0Z4Vxl"

def get_api_client() -> Optional[Client]:
    """
    BookPrint API 클라이언트를 초기화합니다.
    
    Returns:
        Client 인스턴스 또는 None (실패 시)
    """
    if not SDK_AVAILABLE:
        print("[ERROR] BookPrint API SDK가 설치되지 않았습니다.")
        return None
    
    try:
        # 환경변수 키 이름 호환성 처리 (BOOKPRINTAPIKEY 또는 BOOKPRINT_API_KEY)
        api_key = os.getenv('BOOKPRINTAPIKEY') or os.getenv('BOOKPRINT_API_KEY')
        if not api_key:
            print("[ERROR] BOOKPRINTAPIKEY 또는 BOOKPRINT_API_KEY 환경변수가 설정되지 않았습니다.")
            return None
        
        client = Client()
        print(f"[INFO] BookPrint API 클라이언트 초기화 완료")
        return client
        
    except Exception as e:
        print(f"[ERROR] BookPrint API 클라이언트 초기화 실패: {e}")
        return None

def _static_path_to_absolute(rel: Optional[str]) -> Optional[str]:
    """dummy_data의 image_path(프로젝트 기준 상대경로) → 절대경로. 파일 없으면 None."""
    if not rel:
        return None
    p = os.path.normpath(os.path.join(PROJECT_ROOT, rel.replace("/", os.sep)))
    return p if os.path.isfile(p) else None


def _diary_month_day(date_str: str) -> Tuple[str, str]:
    parts = (date_str or "").strip().split("-")
    if len(parts) >= 3:
        return str(int(parts[1])), str(int(parts[2]))
    return "1", "1"


def _ganji_meta(date_str: str) -> Dict[str, str]:
    parts = (date_str or "2026-01-01").split("-")
    year = parts[0] if parts else "2026"
    month = int(parts[1]) if len(parts) > 1 else 1
    season = "봄"
    if month in (12, 1, 2):
        season = "겨울"
    elif month in (3, 4, 5):
        season = "봄"
    elif month in (6, 7, 8):
        season = "여름"
    elif month in (9, 10, 11):
        season = "가을"
    return {
        "year": year,
        "monthTitle": f"{month}월",
        "chapterNum": "1",
        "season_title": season,
    }


def _ensure_cover_photo_path(selected_diaries: List[Dict[str, Any]]) -> str:
    """표지용 로컬 JPEG 경로. 일기 이미지가 없으면 PIL로 임시 파일 생성."""
    for d in selected_diaries:
        ap = _static_path_to_absolute(d.get("image_path"))
        if ap:
            print(f"[DEBUG] 표지용 사진: 기존 파일 사용 {ap}")
            return ap
    from PIL import Image
    import tempfile
    img = Image.new("RGB", (800, 600), color=(240, 248, 255))
    fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
    os.close(fd)
    img.save(tmp_path, "JPEG", quality=85)
    print(f"[DEBUG] 표지용 사진: 임시 JPEG 생성 {tmp_path}")
    return tmp_path


def _insert_diary_book_content(
    client: Client,
    book_uid: str,
    selected_diaries: List[Dict[str, Any]],
    book_title: str,
) -> None:
    """photos.upload → covers.create → contents.insert(간지/내지/발행). SDK 예제와 동일 흐름."""
    cover_path = _ensure_cover_photo_path(selected_diaries)
    upload_resp = client.photos.upload(book_uid, cover_path)
    print(f"[DEBUG] photos.upload response: {upload_resp}")
    photo_name = upload_resp.get("data", {}).get("fileName")
    if not photo_name:
        raise RuntimeError(f"photos.upload 응답에 fileName 없음: {upload_resp}")

    start_date = selected_diaries[0].get("date", "") if selected_diaries else ""
    end_date = selected_diaries[-1].get("date", "") if selected_diaries else start_date
    date_range = f"{start_date} ~ {end_date}".replace("-", ".")[:120]

    cover_resp = client.covers.create(
        book_uid,
        template_uid=TPL_COVER,
        parameters={
            "title": book_title[:80],
            "dateRange": date_range,
            "coverPhoto": photo_name,
        },
    )
    print(f"[DEBUG] covers.create response: {cover_resp}")
    time.sleep(0.15)

    first_date = selected_diaries[0].get("date", "2026-01-01") if selected_diaries else "2026-01-01"
    ins_g = client.contents.insert(
        book_uid,
        template_uid=TPL_GANJI,
        parameters=_ganji_meta(first_date),
    )
    print(f"[DEBUG] contents.insert (GANJI) response: {ins_g}")
    time.sleep(0.15)

    for i, diary in enumerate(selected_diaries):
        m, dday = _diary_month_day(diary.get("date", ""))
        body = ((diary.get("title") or "") + "\n\n" + (diary.get("content") or "")).strip()[:3500]
        ins = client.contents.insert(
            book_uid,
            template_uid=TPL_NAEJI,
            parameters={"monthNum": m, "dayNum": dday, "diaryText": body},
        )
        print(f"[DEBUG] contents.insert (NAEJI {i + 1}/{len(selected_diaries)}) response: {ins}")
        time.sleep(0.05)

    pub_date = datetime.now().strftime("%Y.%m.%d")
    ins_p = client.contents.insert(
        book_uid,
        template_uid=TPL_PUBLISH,
        parameters={
            "title": book_title[:80],
            "publishDate": pub_date,
            "author": "일기 포토북",
        },
    )
    print(f"[DEBUG] contents.insert (PUBLISH) response: {ins_p}")
    time.sleep(0.15)


def _finalize_book_with_min_pages(client: Client, book_uid: str) -> dict:
    """finalize 성공할 때까지 최소 페이지 미달 시 빈 내지 추가 (SDK 예제와 동일 패턴)."""
    last_err: Optional[ApiError] = None
    for attempt in range(30):
        try:
            fin = client.books.finalize(book_uid)
            print(f"[DEBUG] books.finalize response: {fin}")
            if not fin or not fin.get("success"):
                msg = (fin or {}).get("message", "finalize 응답 실패")
                raise RuntimeError(msg)
            return fin
        except ApiError as e:
            last_err = e
            print(f"[ERROR] books.finalize ApiError status_code: {getattr(e, 'status_code', None)}")
            print(f"[ERROR] books.finalize ApiError details: {getattr(e, 'details', None)}")
            print(f"[ERROR] books.finalize raw response: {getattr(e, 'response', None)}")
            detail_text = ""
            if e.details:
                detail_text = (
                    " ".join(str(x) for x in e.details)
                    if isinstance(e.details, (list, tuple))
                    else str(e.details)
                )
            if "최소 페이지" in detail_text:
                print(f"[INFO] 최소 페이지 부족 — 빈 내지 4p 추가 후 재시도 ({attempt + 1})")
                for _ in range(4):
                    br = client.contents.insert(book_uid, template_uid=TPL_BLANK, break_before="page")
                    print(f"[DEBUG] contents.insert (BLANK) response: {br}")
                    time.sleep(0.05)
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("books.finalize 실패: 반복 한도 초과")


def create_book_with_diaries(
    selected_diaries: List[Dict[str, Any]],
    template_id: str = "template_001",
) -> Tuple[bool, Dict[str, Any]]:
    """
    선택된 일기로 BookPrint 책 생성 → 표지/내지 삽입 → finalize 까지 수행.
    finalize 실패 시 성공으로 반환하지 않음 (주문/견적 금지).
    """
    client = get_api_client()
    if not client:
        return False, {"error": "API 클라이언트 초기화 실패"}

    book_title = f"나의 일기 포토북 ({len(selected_diaries)}개 일기)"
    book_create_params = {
        "book_spec_uid": "SQUAREBOOK_HC",
        "title": book_title,
        "creation_type": "TEST",
        "external_ref": f"diary_photobook_{len(selected_diaries)}_entries"[:100],
    }

    try:
        print(f"[INFO] 포토북 생성 시작 - 일기 수: {len(selected_diaries)}")
        print(f"[DEBUG] books.create params: {book_create_params}")

        book_response = client.books.create(**book_create_params)
        print(f"[DEBUG] books.create response: {book_response}")

        if not book_response or not book_response.get("success") or "data" not in book_response:
            error_msg = book_response.get("message", "알 수 없는 오류") if book_response else "응답 없음"
            print(f"[ERROR] books.create 실패 - 전체 응답: {book_response}")
            return False, {"error": f"책 생성 실패: {error_msg}"}

        book_id = book_response["data"]["bookUid"]
        print(f"[INFO] 책 생성 완료 - bookUid: {book_id}")

        _insert_diary_book_content(client, book_id, selected_diaries, book_title)

        finalize_response = _finalize_book_with_min_pages(client, book_id)
        page_count_api = finalize_response.get("data", {}).get("pageCount")
        page_count = int(page_count_api) if page_count_api is not None else calculate_page_count(len(selected_diaries))

        return True, {
            "book_id": book_id,
            "title": book_title,
            "page_count": page_count,
            "diary_count": len(selected_diaries),
            "template_id": template_id,
            "created_at": datetime.now().isoformat(),
            "status": "FINALIZED",
            "finalize_attempted": True,
            "finalize_response": finalize_response,
        }

    except ApiError as e:
        print(f"[ERROR] 포토북 생성 ApiError status_code: {getattr(e, 'status_code', None)}")
        print(f"[ERROR] 포토북 생성 ApiError details: {getattr(e, 'details', None)}")
        print(f"[ERROR] 포토북 생성 ApiError raw response: {getattr(e, 'response', None)}")
        user_error_msg = str(e)
        if getattr(e, "details", None):
            user_error_msg = f"{user_error_msg} - {e.details}"
        return False, {"error": f"포토북 생성 실패: {user_error_msg}"}

    except Exception as e:
        print(f"[ERROR] 포토북 생성 중 오류: {e}")
        print(f"[ERROR] 포토북 생성 오류 타입: {type(e).__name__}")
        return False, {"error": f"포토북 생성 실패: {str(e)}"}

def get_book_estimate(book_id: str) -> Tuple[bool, Dict[str, Any]]:
    """
    완성된 책의 제작 견적을 조회합니다.
    
    Args:
        book_id: 책 ID
        
    Returns:
        (성공 여부, 견적 데이터)
    """
    client = get_api_client()
    if not client:
        return False, {"error": "API 클라이언트 초기화 실패"}
    
    try:
        print(f"[INFO] 견적 조회 시작 - Book ID: {book_id}")
        items_arg = [{"bookUid": book_id, "quantity": 1}]
        print(f"[DEBUG] orders.estimate params: {items_arg}")
        estimate_response = client.orders.estimate(items_arg)
        print(f"[DEBUG] orders.estimate response: {estimate_response}")

        if not estimate_response or not estimate_response.get("success"):
            error_msg = estimate_response.get("message", "알 수 없는 오류") if estimate_response else "응답 없음"
            print(f"[ERROR] 견적 조회 실패 응답: {estimate_response}")
            return False, {"error": f"견적 조회 실패: {error_msg}"}

        estimate_data_raw = estimate_response.get("data", {})
        paid = estimate_data_raw.get("paidCreditAmount")
        total_price = int(paid) if paid is not None else int(
            estimate_data_raw.get("totalPrice")
            or estimate_data_raw.get("total_price")
            or 0
        )

        estimate_data = {
            "book_id": book_id,
            "book_spec_uid": estimate_data_raw.get("bookSpecUid", estimate_data_raw.get("book_spec_uid", "SQUAREBOOK_HC")),
            "page_count": estimate_data_raw.get("pageCount", estimate_data_raw.get("page_count", 0)),
            "book_price": estimate_data_raw.get("bookPrice", estimate_data_raw.get("book_price", 0)),
            "shipping_fee": estimate_data_raw.get("shippingFee", estimate_data_raw.get("shipping_fee", 0)),
            "vat_amount": estimate_data_raw.get("vatAmount", estimate_data_raw.get("vat_amount", 0)),
            "vat_included": True,
            "total_price": total_price,
            "currency": estimate_data_raw.get("currency", "KRW"),
            "credit_sufficient": estimate_data_raw.get("creditSufficient", True),
            "is_estimate": False,
            "estimate_note": "실제 BookPrint API orders.estimate 결과입니다.",
            "price_breakdown": format_price_breakdown(estimate_data_raw),
            "_raw_estimate": estimate_data_raw,
        }

        return True, estimate_data

    except ApiError as e:
        print(f"[ERROR] 견적 조회 ApiError status_code: {getattr(e, 'status_code', None)}")
        print(f"[ERROR] 견적 조회 ApiError details: {getattr(e, 'details', None)}")
        print(f"[ERROR] 견적 조회 ApiError raw response: {getattr(e, 'response', None)}")
        return False, {"error": f"견적 조회 실패: {str(e)} - {getattr(e, 'details', '')}"}

    except Exception as e:
        print(f"[ERROR] 견적 조회 중 오류: {e}")
        return False, {"error": f"견적 조회 실패: {str(e)}"}

def format_price_breakdown(estimate_response: Dict[str, Any]) -> Dict[str, str]:
    """
    견적 응답을 가격 분석표 형태로 포맷팅합니다.
    
    Args:
        estimate_response: API 견적 응답
        
    Returns:
        포맷팅된 가격 분석표
    """
    try:
        breakdown = {}
        bp = estimate_response.get("bookPrice", estimate_response.get("book_price"))
        if bp is not None:
            breakdown["도서 제작비"] = f"{int(bp):,}원"
        sf = estimate_response.get("shippingFee", estimate_response.get("shipping_fee"))
        if sf is not None:
            breakdown["배송비"] = f"{int(sf):,}원"
        va = estimate_response.get("vatAmount", estimate_response.get("vat_amount"))
        if va is not None:
            vat_rate = estimate_response.get("vatRate", estimate_response.get("vat_rate", 10))
            breakdown[f"부가세 ({vat_rate}%)"] = f"{int(va):,}원"
        paid = estimate_response.get("paidCreditAmount")
        if paid is not None:
            breakdown["결제(충전금)"] = f"{int(paid):,}원"
        return breakdown
        
    except Exception as e:
        print(f"[ERROR] 가격 분석표 포맷팅 실패: {e}")
        return {"제작비": "계산 중..."}

def create_book_order(book_id: str, shipping_info: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    완성된 책으로 실제 주문을 생성합니다.
    
    Args:
        book_id: 책 ID
        shipping_info: 배송 정보
        
    Returns:
        (성공 여부, 주문 데이터)
    """
    client = get_api_client()
    if not client:
        return False, {"error": "API 클라이언트 초기화 실패"}

    order_params = None
    try:
        print(f"[INFO] 주문 생성 시작 - Book ID: {book_id}")

        order_params = {
            "items": [{"bookUid": book_id, "quantity": 1}],
            "shipping": {
                "recipientName": shipping_info.get("name", "테스트 사용자"),
                "recipientPhone": shipping_info.get("phone", "010-0000-0000"),
                "postalCode": shipping_info.get("postalCode", "06100"),
                "address1": shipping_info.get("address", "서울특별시 강남구 테헤란로 123"),
                "address2": shipping_info.get("address2", ""),
                "memo": shipping_info.get("memo", "포토북 배송"),
            },
            "external_ref": f"diary_photobook_{book_id[:8]}"[:100],
        }
        
        print(f"[DEBUG] 주문 생성 파라미터: {order_params}")
        print(f"[DEBUG] 파라미터 검증:")
        print(f"  - bookUid: {book_id} (길이: {len(book_id)})")
        print(f"  - shipping.recipientName: {order_params['shipping']['recipientName']}")
        print(f"  - shipping.postalCode: {order_params['shipping']['postalCode']}")
        print(f"  - external_ref: {order_params['external_ref']}")
        
        order_response = client.orders.create(**order_params)
        print(f"[DEBUG] orders.create response: {order_response}")
        
        if not order_response or not order_response.get('success') or 'data' not in order_response:
            error_msg = order_response.get('message', '알 수 없는 오류') if order_response else '응답 없음'
            print(f"[ERROR] 주문 생성 실패 - 전체 응답: {order_response}")
            return False, {"error": f"주문 생성 실패: {error_msg}"}
        
        order_id = order_response['data']['orderUid']
        print(f"[INFO] 주문 생성 완료 - Order ID: {order_id}")
        print(f"[DEBUG] 주문 데이터: {order_response['data']}")
        
        order_data_raw = order_response['data']
        order_data = {
            "order_id": order_id,
            "book_id": book_id,
            "status": order_data_raw.get("status", "PENDING"),
            "status_display": order_data_raw.get("statusDisplay", "주문 접수됨"),
            "total_price": order_data_raw.get("totalPrice", order_data_raw.get("total_price", 0)),
            "order_status": order_data_raw.get("orderStatus", order_data_raw.get("status", "PENDING")),
            "created_at": order_data_raw.get("createdAt", datetime.now().isoformat()),
            "payment_status": order_data_raw.get("paymentStatus", "PENDING"),
            "shipping_status": order_data_raw.get("shippingStatus", "PENDING"),
            "estimated_delivery": order_data_raw.get("estimatedDelivery"),
            "tracking_number": order_data_raw.get("trackingNumber"),
            # 원본 응답 데이터도 포함 (디버깅용)
            "_raw_response": order_data_raw
        }
        
        print(f"[INFO] 주문 데이터 정리 완료: {order_data}")
        return True, order_data
        
    except Exception as e:
        print(f"[ERROR] 주문 생성 중 오류: {e}")
        print(f"[ERROR] 오류 타입: {type(e).__name__}")
        print(f"[ERROR] 사용된 전체 파라미터: {order_params if order_params is not None else '(미구성)'}")
        
        # ApiError인 경우 상세 정보 출력
        if hasattr(e, 'status_code'):
            print(f"[ERROR] orders.create ApiError status_code: {e.status_code}")
        if hasattr(e, 'details'):
            print(f"[ERROR] orders.create ApiError details: {e.details}")
        if hasattr(e, 'response'):
            print(f"[ERROR] orders.create raw response: {e.response}")
        if hasattr(e, 'message'):
            print(f"[ERROR] orders.create error message: {e.message}")
            
        # 사용자 친화적 에러 메시지 생성 (details 포함)
        user_error_msg = str(e)
        if hasattr(e, 'details') and e.details:
            user_error_msg = f"{str(e)} - {e.details}"
            
        return False, {"error": f"주문 생성 실패: {user_error_msg}"}

# 기존 함수들 (호환성을 위해 유지, 내부적으로 실제 API 호출)
def calculate_page_count(selected_count: int) -> int:
    """
    선택된 일기 수를 기반으로 최종 페이지 수를 계산합니다.
    """
    total_pages = 2 + selected_count  # 표지 2페이지 + 일기 페이지들
    if total_pages % 2 != 0:
        total_pages += 1
    return max(24, min(130, total_pages))

def validate_diary_selection(selected_count: int) -> Dict[str, Any]:
    """
    일기 선택 개수를 검증합니다.
    """
    min_diaries = 22
    max_diaries = 128
    recommended_min = 30
    recommended_max = 50
    
    result = {
        "valid": False,
        "message": "",
        "is_recommended": False,
        "page_count": calculate_page_count(selected_count),
        "selected_count": selected_count
    }
    
    if selected_count < min_diaries:
        result["message"] = f"최소 {min_diaries}개 일기를 선택해주세요. (현재: {selected_count}개)"
        return result
    
    if selected_count > max_diaries:
        result["message"] = f"최대 {max_diaries}개까지 선택 가능합니다. (현재: {selected_count}개)"
        return result
    
    result["valid"] = True
    
    if recommended_min <= selected_count <= recommended_max:
        result["is_recommended"] = True
        result["message"] = f"권장 범위입니다! ({selected_count}개 선택)"
    else:
        result["message"] = f"선택 완료 (권장: {recommended_min}~{recommended_max}개)"
    
    return result

def estimate_book_cost(selected_count: int) -> Dict[str, Any]:
    """
    임시 비용 추정 (실제 API 연동 전 fallback)
    실제로는 create_book_with_diaries + get_book_estimate 사용 권장
    """
    print("[WARNING] 임시 비용 추정 사용 중. 실제 견적은 create_book_with_diaries + get_book_estimate 사용하세요.")
    
    page_count = calculate_page_count(selected_count)
    
    # 임시 추정값
    base_price = 19800
    additional_cost = max(0, (page_count - 24) // 2 * 500)
    book_price = base_price + additional_cost
    shipping_fee = 3000
    vat_amount = int((book_price + shipping_fee) * 0.1)
    total_price = book_price + shipping_fee + vat_amount
    
    return {
        "book_spec_uid": "SQUAREBOOK_HC",
        "selected_count": selected_count,
        "page_count": page_count,
        "base_price": base_price,
        "additional_cost": additional_cost,
        "book_price": book_price,
        "shipping_fee": shipping_fee,
        "vat_amount": vat_amount,
        "vat_included": True,
        "total_price": total_price,
        "currency": "KRW",
        "is_estimate": True,
        "estimate_note": "임시 추정 비용입니다. 정확한 견적은 포토북 생성 후 확인됩니다.",
        "price_breakdown": {
            "기본 제작비 (24페이지)": f"{base_price:,}원",
            "추가 페이지 비용": f"{additional_cost:,}원" if additional_cost > 0 else "없음",
            "소계 (제작비)": f"{book_price:,}원",
            "배송비": f"{shipping_fee:,}원",
            "부가세 (10%)": f"{vat_amount:,}원"
        }
    }

def get_photobook_specs() -> Dict[str, Any]:
    """
    포토북 사양 정보를 반환합니다.
    """
    return {
        "book_spec_uid": "SQUAREBOOK_HC",
        "name": "스퀘어북 하드커버",
        "size": "243 × 248mm",
        "cover_type": "하드커버",
        "binding_type": "PUR 제본",
        "min_pages": 24,
        "max_pages": 130,
        "page_increment": 2,
        "recommended_diaries": {
            "min": 22,
            "max": 128,
            "recommended_min": 30,
            "recommended_max": 50
        },
        "layout_info": {
            "image_area": "상단 40%",
            "text_area": "하단 60%",
            "max_characters": 600,
            "pages_per_diary": 1
        }
    }

def get_book_templates() -> List[Dict[str, Any]]:
    """
    사용 가능한 포토북 템플릿 목록을 반환합니다.
    """
    return [
        {
            "template_id": "template_001",
            "name": "클래식 포토북",
            "description": "심플하고 깔끔한 디자인"
        },
        {
            "template_id": "template_002", 
            "name": "모던 포토북",
            "description": "현대적이고 세련된 디자인"
        }
    ]