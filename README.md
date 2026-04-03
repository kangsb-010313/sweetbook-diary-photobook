# 개인 일기 포토북 서비스

일상의 소중한 순간을 기록한 일기와 사진을 아름다운 포토북으로 제작하는 서비스입니다.

## 타겟 고객
- 일기 작성을 좋아하는 개인 사용자
- 추억을 책으로 보관하고 싶은 사람들
- 개인 맞춤형 포토북을 원하는 고객

## 주요 기능
- 일기 작성 및 사진 업로드
- 포토북 미리보기 및 생성 (BookPrint API 연동)
- 포토북 주문 및 배송 정보 입력
- 더미 데이터로 즉시 서비스 체험 가능

---

## 실행 방법

### 1. 저장소 클론 및 이동
```bash
git clone https://github.com/kangsb-010313/sweetbook-diary-photobook.git
cd sweetbook-diary-photobook
```

### 2. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python -m venv sweetbook

# 가상환경 활성화
source sweetbook/bin/activate  # macOS/Linux
# Windows의 경우: sweetbook\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 BOOKPRINT_API_KEY에 실제 API Key 입력
# BOOKPRINT_API_KEY=SBxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. 서버 실행
```bash
python app.py
```

### 6. 브라우저에서 접속
```
http://127.0.0.1:8000
```

**실행 후 확인사항:**
- 메인 페이지에서 더미 일기 목록이 표시되는지 확인
- 네비게이션 메뉴로 각 페이지 이동이 가능한지 확인
- 일기 작성 페이지에서 폼이 정상 표시되는지 확인

---

## 사용한 API 목록

> **개발 진행 중** - 구현 완료 후 업데이트 예정

BookPrint API의 다음 엔드포인트들을 사용할 예정입니다:

| API | 용도 | 호출 위치 |
|-----|------|-----------|
| POST /books | 새 포토북 생성 | 포토북 미리보기 페이지 |
| POST /orders | 포토북 주문 처리 | 주문 페이지 |
| GET /books/{bookUid} | 포토북 상세 조회 | 주문 완료 페이지 |

*실제 구현에서 사용된 API 목록으로 업데이트될 예정입니다.*

---

## AI 도구 사용 내역

> **개발 진행 중** - 구현 완료 후 업데이트 예정

| AI 도구 | 활용 내용 |
|---------|-----------|
| Claude (Cursor) | 프로젝트 구조 설계 및 환경 설정 |
| Claude (Cursor) | README.md 초안 작성 |
| *추가 예정* | *개발 과정에서 사용한 내용으로 업데이트* |

*개발 과정에서 실제로 사용한 AI 도구와 활용 방법으로 업데이트될 예정입니다.*

---

## 설계 의도

### 서비스 선택 이유
- **명확한 사용 사례**: 개인의 일상 기록이라는 직관적이고 이해하기 쉬운 서비스
- **자연스러운 API 활용**: Books API와 Orders API 사용이 서비스 플로우에 자연스럽게 통합됨
- **적절한 구현 복잡도**: 과제 기간 내 완성 가능한 범위로 설계
- **즉시 체험 가능**: 더미 데이터를 통해 심사자가 바로 서비스를 확인할 수 있음

### 기술 스택 선택 이유
- **FastAPI**: 빠른 개발 속도와 자동 API 문서 생성
- **HTML/CSS/JS**: 복잡한 빌드 과정 없이 바로 실행 가능
- **JSON 파일**: 데이터베이스 설치 없이 간단한 데이터 관리
- **BookPrint API SDK**: 안정적인 API 연동

### 비즈니스 가능성
- **개인화 트렌드**: 개인 맞춤형 콘텐츠에 대한 수요 증가
- **아날로그 회귀**: 디지털 피로감으로 인한 실물 제품 선호 증가
- **선물 시장**: 특별한 의미가 있는 선물용 시장 확장 가능성
- **구독 모델**: 월간/연간 포토북 구독 서비스로 발전 가능

### 추가하고 싶은 기능
- **사용자 인증**: 개인 계정 및 로그인 시스템
- **템플릿 다양화**: 다양한 포토북 레이아웃 및 디자인 옵션
- **소셜 기능**: 포토북 공유 및 선물하기 기능
- **배송 추적**: 실시간 주문 상태 및 배송 추적
- **모바일 최적화**: 반응형 웹 또는 모바일 앱
- **AI 기능**: 자동 사진 정렬 및 텍스트 요약

---

## 프로젝트 구조

```
sweetbook-diary-photobook/
├── README.md                    # 프로젝트 안내 문서
├── requirements.txt             # Python 의존성 목록
├── .env.example                 # 환경변수 설정 예시
├── .gitignore                   # Git 제외 파일 목록
├── app.py                       # FastAPI 메인 애플리케이션 (예정)
├── static/                      # 정적 파일 (CSS, JS, 이미지)
├── templates/                   # HTML 템플릿
├── data/                        # JSON 더미 데이터
└── sweetbook/                   # Python 가상환경
```

---

## 개발 환경
- Python 3.12.11
- FastAPI 0.135.3
- BookPrint API Python SDK
- 가상환경: sweetbook

## 현재 구현 상태

### ✅ 완료된 기능
- FastAPI 기본 서버 구동
- 메인 페이지 (일기 목록 표시)
- 일기 작성 페이지 (UI만 구현)
- 포토북 미리보기 페이지
- 주문 완료 페이지
- 더미 데이터 표시
- 반응형 웹 디자인
- 정적 파일 서빙

### 🚧 구현 예정 기능
- 실제 일기 저장 기능
- BookPrint API Books 연동
- BookPrint API Orders 연동
- 이미지 업로드 기능
- 실제 포토북 생성 및 주문 처리