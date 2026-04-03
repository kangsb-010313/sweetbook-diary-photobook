import json
import os
from datetime import datetime
from typing import Dict, List, Any


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _json_path() -> str:
    return os.path.join(_project_root(), "data", "dummy_data.json")


def load_dummy_data() -> Dict[str, Any]:
    """
    data/dummy_data.json 파일을 읽어서 반환합니다.
    파일이 없거나 JSON이 비정상일 경우 기본 구조를 반환합니다.
    """
    try:
        json_path = _json_path()
        
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

def save_dummy_data(data: Dict[str, Any]) -> None:
    """
    data/dummy_data.json 에 전체 데이터를 UTF-8, ensure_ascii=False 로 저장합니다.
    임시 파일에 쓴 뒤 replace 로 원자적 교체합니다.
    """
    path = _json_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def add_diary(
    title: str,
    content: str,
    date: str,
    image_path: str = "",
) -> Dict[str, Any]:
    """
    새 일기를 diaries 배열에 추가하고 JSON 파일에 저장합니다.
    id 는 기존 최대 id + 1, created_at 은 ISO8601 문자열.
    image_path 는 프로젝트 기준 상대경로(예: static/uploads/xxx.jpg) 또는 빈 문자열.
    """
    data = load_dummy_data()
    diaries = data.get("diaries", [])
    next_id = max((d["id"] for d in diaries if isinstance(d.get("id"), int)), default=0) + 1

    entry: Dict[str, Any] = {
        "id": next_id,
        "title": title.strip(),
        "content": content.strip(),
        "date": date.strip(),
        "created_at": datetime.now().replace(microsecond=0).isoformat(),
        "image_path": (image_path or "").strip(),
    }

    diaries.append(entry)
    data["diaries"] = diaries
    save_dummy_data(data)
    return entry


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