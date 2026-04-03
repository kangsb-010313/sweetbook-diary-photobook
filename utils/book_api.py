"""
BookPrint API 연동 모듈
TODO: 추후 Sweetbook Book Print API 연동 예정
현재는 placeholder 함수들만 구현되어 있습니다.
"""

from typing import Dict, Any, List
import json

def create_book_payload(diary_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    일기 데이터를 BookPrint API용 페이로드로 변환합니다.
    TODO: 실제 BookPrint API 스펙에 맞춰 구현 예정
    """
    # Placeholder 구현
    payload = {
        "book_spec_uid": "SQUAREBOOK_HC",
        "title": diary_data.get("title", "나의 일기 포토북"),
        "creation_type": "TEST",
        "content": diary_data.get("content", ""),
        "date": diary_data.get("date", "")
    }
    
    print(f"[DEBUG] 포토북 페이로드 생성: {payload}")
    return payload

def submit_book_order(book_data: Dict[str, Any], shipping_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    포토북 주문을 BookPrint API에 제출합니다.
    TODO: 실제 BookPrint API Orders 엔드포인트 연동 예정
    """
    # Placeholder 구현
    order_result = {
        "success": True,
        "order_id": "test_order_123456",
        "book_id": book_data.get("book_id", "test_book_123"),
        "status": "PENDING",
        "message": "주문이 성공적으로 접수되었습니다. (테스트 모드)"
    }
    
    print(f"[DEBUG] 주문 제출 결과: {order_result}")
    return order_result

def get_book_templates() -> List[Dict[str, Any]]:
    """
    사용 가능한 포토북 템플릿 목록을 반환합니다.
    TODO: 실제 BookPrint API Templates 엔드포인트 연동 예정
    """
    # Placeholder 구현
    templates = [
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
    
    return templates

def calculate_page_count(selected_count: int) -> int:
    """
    선택된 일기 수를 기반으로 최종 페이지 수를 계산합니다.
    
    Args:
        selected_count: 선택된 일기 개수
        
    Returns:
        최종 페이지 수 (2페이지 단위로 올림)
    """
    # 총 페이지 = 표지(2페이지) + 선택한 일기 수(각 1페이지)
    total_pages = 2 + selected_count
    
    # 2페이지 단위로 올림
    if total_pages % 2 != 0:
        total_pages += 1
    
    # 최소/최대 페이지 제한 적용
    total_pages = max(24, min(130, total_pages))
    
    return total_pages

def validate_diary_selection(selected_count: int) -> Dict[str, Any]:
    """
    일기 선택 개수를 검증합니다.
    
    Args:
        selected_count: 선택된 일기 개수
        
    Returns:
        검증 결과 딕셔너리
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
    선택된 일기 수를 기반으로 포토북 제작 비용을 추정합니다.
    
    Args:
        selected_count: 선택된 일기 개수
        
    Returns:
        비용 정보 딕셔너리
    """
    page_count = calculate_page_count(selected_count)
    
    # SQUAREBOOK_HC 기준 가격 (BookPrint API 문서 기반)
    base_price = 19800  # 24페이지 기본 가격
    base_pages = 24
    price_per_2pages = 500  # 2페이지당 추가 비용
    
    # 추가 페이지 비용 계산
    if page_count > base_pages:
        additional_pages = page_count - base_pages
        additional_cost = (additional_pages // 2) * price_per_2pages
    else:
        additional_cost = 0
    
    book_price = base_price + additional_cost
    shipping_fee = 3000  # 기본 배송비
    vat_rate = 0.1  # 부가세 10%
    
    subtotal = book_price + shipping_fee
    vat_amount = int(subtotal * vat_rate)
    total_price = subtotal + vat_amount
    
    cost_info = {
        "book_spec_uid": "SQUAREBOOK_HC",
        "selected_count": selected_count,
        "page_count": page_count,
        "base_price": base_price,
        "additional_cost": additional_cost,
        "book_price": book_price,
        "shipping_fee": shipping_fee,
        "subtotal": subtotal,
        "vat_amount": vat_amount,
        "vat_included": True,
        "total_price": total_price,
        "currency": "KRW",
        "price_breakdown": {
            "기본 가격 (24페이지)": f"{base_price:,}원",
            "추가 페이지 비용": f"{additional_cost:,}원" if additional_cost > 0 else "없음",
            "도서 제작비": f"{book_price:,}원",
            "배송비": f"{shipping_fee:,}원",
            "부가세 (10%)": f"{vat_amount:,}원",
            "총 결제 금액": f"{total_price:,}원"
        }
    }
    
    return cost_info

def get_photobook_specs() -> Dict[str, Any]:
    """
    포토북 사양 정보를 반환합니다.
    
    Returns:
        포토북 사양 정보
    """
    specs = {
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
    
    return specs