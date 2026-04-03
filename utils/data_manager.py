import json
import os
from typing import Dict, List, Any

def load_dummy_data() -> Dict[str, Any]:
    """
    data/dummy_data.json 파일을 읽어서 반환합니다.
    파일이 없거나 JSON이 비정상일 경우 기본 구조를 반환합니다.
    """
    try:
        # 현재 파일의 상위 디렉토리(프로젝트 루트)를 기준으로 경로 설정
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(current_dir, "data", "dummy_data.json")
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 기본 구조 확인 및 보완
        if "diaries" not in data:
            data["diaries"] = []
        if "photobooks" not in data:
            data["photobooks"] = []
        if "orders" not in data:
            data["orders"] = []
            
        return data
    
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"더미 데이터 로드 실패: {e}")
        # 기본 구조 반환
        return {
            "diaries": [],
            "photobooks": [],
            "orders": []
        }

def get_diaries() -> List[Dict[str, Any]]:
    """일기 목록을 반환합니다."""
    data = load_dummy_data()
    return data.get("diaries", [])

def get_photobooks() -> List[Dict[str, Any]]:
    """포토북 목록을 반환합니다."""
    data = load_dummy_data()
    return data.get("photobooks", [])

def get_orders() -> List[Dict[str, Any]]:
    """주문 목록을 반환합니다."""
    data = load_dummy_data()
    return data.get("orders", [])