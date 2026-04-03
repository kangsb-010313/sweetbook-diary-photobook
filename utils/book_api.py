"""
BookPrint API 연동 모듈
실제 Sweetbook Book Print API SDK를 사용하여 포토북 생성 및 주문 처리
"""

import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# BookPrint API SDK import
try:
    from bookprintapi import Client
    SDK_AVAILABLE = True
except ImportError:
    print("[WARNING] BookPrint API SDK를 찾을 수 없습니다.")
    SDK_AVAILABLE = False

# 환경변수 로드
load_dotenv()

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

def create_book_with_diaries(selected_diaries: List[Dict[str, Any]], 
                           template_id: str = "template_001") -> Tuple[bool, Dict[str, Any]]:
    """
    선택된 일기들로 실제 포토북을 생성합니다.
    
    Args:
        selected_diaries: 선택된 일기 데이터 리스트
        template_id: 선택된 템플릿 ID
        
    Returns:
        (성공 여부, 결과 데이터)
    """
    client = get_api_client()
    if not client:
        return False, {"error": "API 클라이언트 초기화 실패"}
    
    try:
        print(f"[INFO] 포토북 생성 시작 - 일기 수: {len(selected_diaries)}")
        
        # 1. 책 생성 (현재는 기본 생성만 지원)
        book_title = f"나의 일기 포토북 ({len(selected_diaries)}개 일기)"
        book_create_params = {
            "book_spec_uid": "SQUAREBOOK_HC",
            "title": book_title,
            "creation_type": "TEST",  # 테스트 환경이므로 TEST 모드
            "external_ref": f"diary_photobook_{len(selected_diaries)}_entries"
        }
        
        print(f"[DEBUG] books.create params: {book_create_params}")
        print(f"[DEBUG] 책 생성 파라미터 검증:")
        print(f"  - book_spec_uid: {book_create_params['book_spec_uid']}")
        print(f"  - creation_type: {book_create_params['creation_type']}")
        print(f"  - title 길이: {len(book_create_params['title'])}")
        print(f"  - external_ref: {book_create_params['external_ref']}")
        
        book_response = client.books.create(**book_create_params)
        print(f"[DEBUG] books.create response: {book_response}")
        
        if not book_response or not book_response.get('success') or 'data' not in book_response:
            error_msg = book_response.get('message', '알 수 없는 오류') if book_response else '응답 없음'
            print(f"[ERROR] books.create 실패 - 전체 응답: {book_response}")
            print(f"[ERROR] books.create 사용 파라미터: {book_create_params}")
            return False, {"error": f"책 생성 실패: {error_msg}"}
        
        book_id = book_response['data']['bookUid']
        print(f"[INFO] 책 생성 완료 - Book ID: {book_id}")
        
        # 2. 책 완성 처리 (선택적 - 콘텐츠 삽입 기능이 없으므로 생략 가능)
        # TODO: 실제 서비스에서는 콘텐츠 삽입 API가 추가되면 여기에 구현
        print("[INFO] 콘텐츠 삽입 기능은 현재 SDK에서 지원하지 않음")
        print("[INFO] 책 생성만 완료된 상태로 진행 (완성 처리는 견적 조회 시 필요하면 시도)")
        
        # 완성 처리는 선택적으로 시도 (실패해도 책 생성 자체는 성공으로 처리)
        finalize_attempted = False
        try:
            print(f"[DEBUG] books.finalize 시도 - Book ID: {book_id}")
            finalize_response = client.books.finalize(book_id)
            print(f"[DEBUG] books.finalize response: {finalize_response}")
            
            if finalize_response and finalize_response.get('success'):
                print(f"[INFO] 책 완성 처리 완료 - Book ID: {book_id}")
                finalize_attempted = True
            else:
                error_msg = finalize_response.get('message', '알 수 없는 오류') if finalize_response else '응답 없음'
                print(f"[WARNING] 책 완성 처리 실패하지만 계속 진행: {error_msg}")
                print(f"[WARNING] finalize 실패 응답: {finalize_response}")
        except Exception as finalize_error:
            print(f"[WARNING] 책 완성 처리 중 오류하지만 계속 진행: {finalize_error}")
            print(f"[WARNING] finalize 오류 타입: {type(finalize_error).__name__}")
            
            # ApiError인 경우 상세 정보 출력
            if hasattr(finalize_error, 'status_code'):
                print(f"[WARNING] finalize ApiError status_code: {finalize_error.status_code}")
            if hasattr(finalize_error, 'details'):
                print(f"[WARNING] finalize ApiError details: {finalize_error.details}")
            if hasattr(finalize_error, 'response'):
                print(f"[WARNING] finalize raw response: {finalize_error.response}")
        
        print(f"[INFO] 포토북 생성 완료 - Book ID: {book_id}")
        
        return True, {
            "book_id": book_id,
            "title": book_title,
            "page_count": calculate_page_count(len(selected_diaries)),
            "diary_count": len(selected_diaries),
            "template_id": template_id,
            "created_at": datetime.now().isoformat(),
            "status": "FINALIZED" if finalize_attempted else "CREATED",
            "finalize_attempted": finalize_attempted
        }
        
    except Exception as e:
        print(f"[ERROR] 포토북 생성 중 오류: {e}")
        print(f"[ERROR] 포토북 생성 오류 타입: {type(e).__name__}")
        
        # ApiError인 경우 상세 정보 출력
        if hasattr(e, 'status_code'):
            print(f"[ERROR] books.create ApiError status_code: {e.status_code}")
        if hasattr(e, 'details'):
            print(f"[ERROR] books.create ApiError details: {e.details}")
        if hasattr(e, 'response'):
            print(f"[ERROR] books.create raw response: {e.response}")
            
        # 사용자 친화적 에러 메시지 생성
        user_error_msg = str(e)
        if hasattr(e, 'details') and e.details:
            user_error_msg = f"{str(e)} - {e.details}"
            
        return False, {"error": f"포토북 생성 실패: {user_error_msg}"}

def add_cover_page(client: Client, book_id: str, selected_diaries: List[Dict[str, Any]]) -> bool:
    """
    표지 페이지를 추가합니다.
    
    Args:
        client: BookPrint API 클라이언트
        book_id: 책 ID
        selected_diaries: 선택된 일기 데이터
        
    Returns:
        성공 여부
    """
    try:
        # 첫 번째와 마지막 일기의 날짜로 기간 표시
        start_date = selected_diaries[0]['date'] if selected_diaries else "2026-01-01"
        end_date = selected_diaries[-1]['date'] if selected_diaries else "2026-12-31"
        
        cover_content = f"""나의 일기 포토북

{start_date} ~ {end_date}

{len(selected_diaries)}개의 소중한 기록"""
        
        # 표지 페이지 삽입
        cover_response = client.books.insert_content(
            book_id=book_id,
            page_number=1,
            content_type="text",
            content=cover_content,
            layout="cover"
        )
        
        print(f"[INFO] 표지 페이지 추가 완료")
        return True
        
    except Exception as e:
        print(f"[ERROR] 표지 페이지 추가 실패: {e}")
        return False

def add_diary_content_pages(client: Client, book_id: str, selected_diaries: List[Dict[str, Any]]) -> bool:
    """
    일기 콘텐츠 페이지들을 추가합니다.
    
    Args:
        client: BookPrint API 클라이언트
        book_id: 책 ID
        selected_diaries: 선택된 일기 데이터
        
    Returns:
        성공 여부
    """
    try:
        for index, diary in enumerate(selected_diaries):
            page_number = index + 2  # 표지 다음부터
            
            # 일기 내용 구성 (40% 이미지 영역, 60% 텍스트 영역 고려)
            diary_content = f"""{diary['title']}

{diary['date']}

{diary['content']}"""
            
            # 일기 페이지 삽입
            content_response = client.books.insert_content(
                book_id=book_id,
                page_number=page_number,
                content_type="text",
                content=diary_content,
                layout="diary_page"
            )
            
            # 이미지가 있는 경우 이미지도 삽입 시도
            if diary.get('image_path'):
                try:
                    image_response = client.books.insert_content(
                        book_id=book_id,
                        page_number=page_number,
                        content_type="image",
                        content=diary['image_path'],
                        layout="diary_image"
                    )
                    print(f"[INFO] 일기 {index+1} 이미지 추가 완료")
                except Exception as img_error:
                    print(f"[WARNING] 일기 {index+1} 이미지 추가 실패: {img_error}")
            
            print(f"[INFO] 일기 {index+1}/{len(selected_diaries)} 페이지 추가 완료")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 일기 콘텐츠 페이지 추가 실패: {e}")
        return False

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
        
        # 주문 견적 조회 (올바른 파라미터 구조 사용)
        estimate_response = client.orders.estimate(items=[{"bookUid": book_id, "quantity": 1}])
        
        if not estimate_response or not estimate_response.get('success'):
            error_msg = estimate_response.get('message', '알 수 없는 오류') if estimate_response else '응답 없음'
            return False, {"error": f"견적 조회 실패: {error_msg}"}
        
        print(f"[INFO] 견적 조회 완료: {estimate_response}")
        
        # 견적 데이터 추출 (API 응답 구조에 맞게)
        estimate_data_raw = estimate_response.get('data', {})
        
        # 견적 데이터 정리
        estimate_data = {
            "book_id": book_id,
            "book_spec_uid": estimate_data_raw.get("book_spec_uid", "SQUAREBOOK_HC"),
            "page_count": estimate_data_raw.get("page_count", 0),
            "book_price": estimate_data_raw.get("book_price", 0),
            "shipping_fee": estimate_data_raw.get("shipping_fee", 0),
            "vat_amount": estimate_data_raw.get("vat_amount", 0),
            "vat_included": estimate_data_raw.get("vat_included", True),
            "total_price": estimate_data_raw.get("total_price", 0),
            "currency": estimate_data_raw.get("currency", "KRW"),
            "is_estimate": False,  # 실제 API 결과
            "estimate_note": "실제 BookPrint API에서 계산된 정확한 비용입니다.",
            "price_breakdown": format_price_breakdown(estimate_data_raw)
        }
        
        return True, estimate_data
        
    except Exception as e:
        print(f"[ERROR] 견적 조회 중 오류: {e}")
        print(f"[INFO] 실제 API 견적 조회 실패, 로컬 추정 비용으로 fallback")
        
        # Fallback: 로컬 추정 비용 사용
        from utils.book_api import estimate_book_cost
        page_count = calculate_page_count(2)  # 기본 2개 일기로 추정
        fallback_estimate = estimate_book_cost(2)
        fallback_estimate["book_id"] = book_id
        fallback_estimate["estimate_note"] = f"실제 API 견적 조회 실패로 인한 임시 추정 비용 (오류: {str(e)})"
        
        return True, fallback_estimate

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
        
        if "book_price" in estimate_response:
            breakdown["도서 제작비"] = f"{estimate_response['book_price']:,}원"
        
        if "shipping_fee" in estimate_response:
            breakdown["배송비"] = f"{estimate_response['shipping_fee']:,}원"
        
        if "vat_amount" in estimate_response:
            vat_rate = estimate_response.get("vat_rate", 10)
            breakdown[f"부가세 ({vat_rate}%)"] = f"{estimate_response['vat_amount']:,}원"
        
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
    
    try:
        print(f"[INFO] 주문 생성 시작 - Book ID: {book_id}")
        
        # 주문 생성 (SDK 스펙에 맞는 파라미터 구조 사용)
        order_params = {
            "items": [{"bookUid": book_id, "quantity": 1}],
            "shipping": {
                "recipientName": shipping_info.get("name", "테스트 사용자"),
                "recipientPhone": shipping_info.get("phone", "010-0000-0000"),
                "postalCode": "12345",  # TODO: 실제 우편번호 필요
                "address1": shipping_info.get("address", "서울시 테스트구 테스트동 123-45"),
                "address2": "",  # 상세주소 (선택사항)
                "memo": "포토북 배송 - 조심히 다뤄주세요"  # 배송 메모 (선택사항)
            },
            "external_ref": f"diary_photobook_{book_id[:8]}"  # 외부 참조 ID
        }
        
        print(f"[DEBUG] 주문 생성 파라미터: {order_params}")
        print(f"[DEBUG] 파라미터 검증:")
        print(f"  - bookUid: {book_id} (길이: {len(book_id)})")
        print(f"  - shipping.recipientName: {order_params['shipping']['recipientName']}")
        print(f"  - shipping.postalCode: {order_params['shipping']['postalCode']}")
        print(f"  - external_ref: {order_params['external_ref']}")
        
        order_response = client.orders.create(**order_params)
        
        print(f"[DEBUG] 주문 생성 API 응답: {order_response}")
        
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
        print(f"[ERROR] 사용된 전체 파라미터: {order_params}")
        
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