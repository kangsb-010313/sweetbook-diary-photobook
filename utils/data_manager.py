import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _project_root_path() -> Path:
    return Path(__file__).resolve().parent.parent


def try_delete_upload_rel_path(rel_path: str) -> None:
    """
    static/uploads/ 아래에 있는 파일만 삭제합니다.
    샘플(static/images/...) 등은 경로 조건에 걸리지 않아 삭제하지 않습니다.
    """
    rel = (rel_path or "").strip().replace("\\", "/")
    if not rel.startswith("static/uploads/") or ".." in rel:
        return
    root = _project_root_path()
    full = (root / rel).resolve()
    uploads = (root / "static" / "uploads").resolve()
    try:
        full.relative_to(uploads)
    except ValueError:
        return
    try:
        if full.is_file():
            full.unlink()
    except OSError as e:
        print(f"[WARN] 업로드 이미지 삭제 실패 ({rel}): {e}")


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
    print(f"[DEBUG] save_dummy_data 대상 경로 (_json_path) = {path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)
    print(f"[DEBUG] save_dummy_data 완료: {path} (diaries {len(data.get('diaries', []))}건)")


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
    print(f"[DEBUG] add_diary: 새 id={next_id}, title={title.strip()!r}")
    save_dummy_data(data)
    return entry


def get_diaries() -> List[Dict[str, Any]]:
    """일기 목록을 반환합니다."""
    data = load_dummy_data()
    return data.get("diaries", [])


def get_diary_by_id(diary_id: int) -> Optional[Dict[str, Any]]:
    """id에 해당하는 일기 한 건을 반환합니다. 없으면 None."""
    for d in get_diaries():
        if isinstance(d.get("id"), int) and d["id"] == diary_id:
            return dict(d)
    return None


def delete_diary(diary_id: int) -> bool:
    """
    일기를 JSON에서 제거하고 저장합니다.
    image_path가 static/uploads/ 이면 해당 파일 삭제를 시도합니다.
    """
    try:
        data = load_dummy_data()
        diaries = data.get("diaries", [])
        idx = next(
            (
                i
                for i, d in enumerate(diaries)
                if isinstance(d.get("id"), int) and d["id"] == diary_id
            ),
            None,
        )
        if idx is None:
            return False
        removed = diaries.pop(idx)
        try_delete_upload_rel_path(removed.get("image_path") or "")
        data["diaries"] = diaries
        save_dummy_data(data)
        return True
    except Exception as e:
        print(f"[ERROR] delete_diary 실패: {e}")
        return False


def update_diary(
    diary_id: int,
    title: str,
    content: str,
    date: str,
    *,
    new_image_relpath: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    일기 본문/날짜/제목을 수정합니다.
    new_image_relpath가 None이면 기존 image_path를 유지합니다.
    비어 있지 않은 문자열이면 해당 경로로 교체하고, 기존 경로가 uploads면 파일 삭제를 시도합니다.
    """
    try:
        data = load_dummy_data()
        diaries = data.get("diaries", [])
        entry = next(
            (
                d
                for d in diaries
                if isinstance(d.get("id"), int) and d["id"] == diary_id
            ),
            None,
        )
        if entry is None:
            return None

        old_path = (entry.get("image_path") or "").strip()
        if new_image_relpath is not None and new_image_relpath.strip():
            new_path = new_image_relpath.strip()
            try_delete_upload_rel_path(old_path)
            entry["image_path"] = new_path

        entry["title"] = title.strip()
        entry["content"] = content.strip()
        entry["date"] = date.strip()

        save_dummy_data(data)
        return dict(entry)
    except Exception as e:
        print(f"[ERROR] update_diary 실패: {e}")
        return None

def get_photobooks() -> List[Dict[str, Any]]:
    """포토북 목록을 반환합니다."""
    data = load_dummy_data()
    return data.get("photobooks", [])

def get_orders() -> List[Dict[str, Any]]:
    """주문 목록을 반환합니다."""
    data = load_dummy_data()
    return data.get("orders", [])