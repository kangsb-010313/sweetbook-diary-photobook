/**
 * 개인 일기 포토북 서비스 - 메인 JavaScript
 */

// DOM 로드 완료 후 실행
document.addEventListener('DOMContentLoaded', function() {
    console.log('📖 일기 포토북 서비스가 시작되었습니다.');
    
    // 페이지별 초기화
    initializePage();
    
    // 공통 기능 초기화
    initializeCommonFeatures();
    
    // 홈페이지인 경우 추가 초기화 (안전장치)
    if (getCurrentPage() === 'home') {
        setTimeout(() => {
            console.log('홈페이지 추가 초기화 체크...');
            const checkboxes = document.querySelectorAll('.diary-checkbox');
            if (checkboxes.length > 0 && !updateSelectionInfo) {
                console.log('일기 선택 기능 재초기화 필요');
                initializeDiarySelection();
            }
        }, 200);
    }
});

/**
 * 페이지별 초기화 함수
 */
function initializePage() {
    const currentPage = getCurrentPage();
    
    switch(currentPage) {
        case 'home':
            initializeHomePage();
            break;
        case 'write':
            initializeWritePage();
            break;
        case 'preview':
            initializePreviewPage();
            break;
        case 'success':
            initializeSuccessPage();
            break;
        default:
            console.log('알 수 없는 페이지:', currentPage);
    }
}

/**
 * 현재 페이지 식별
 */
function getCurrentPage() {
    const path = window.location.pathname;
    
    if (path === '/' || path === '/index') {
        return 'home';
    } else if (path === '/write') {
        return 'write';
    } else if (path === '/preview') {
        return 'preview';
    } else if (path === '/success') {
        return 'success';
    }
    
    return 'unknown';
}

/**
 * 공통 기능 초기화
 */
function initializeCommonFeatures() {
    // 툴팁 초기화 (Bootstrap)
    initializeTooltips();
    
    // 부드러운 스크롤
    initializeSmoothScroll();
    
    // 로딩 상태 관리
    initializeLoadingStates();
    
    // 에러 처리
    initializeErrorHandling();
}

/**
 * 홈페이지 초기화
 */
function initializeHomePage() {
    console.log('홈페이지 초기화 중...');
    
    // 일기 카드 애니메이션
    animateElements('.card', 'fade-in');
    
    // 일기 카드 호버 효과
    enhanceDiaryCards();
    
    // 일기 선택 기능 초기화 (DOM 로딩 완료 후)
    setTimeout(() => {
        console.log('일기 선택 기능 초기화 시작...');
        initializeDiarySelection();
    }, 100);
}

/**
 * 일기 작성 페이지 초기화
 */
function initializeWritePage() {
    console.log('일기 작성 페이지 초기화 중...');
    
    // 폼 유효성 검사
    initializeFormValidation();
    
    // 자동 저장 기능 (선택사항)
    initializeAutoSave();
    
    // 글자 수 카운터
    initializeCharacterCounter();
}

/**
 * 미리보기 페이지 초기화
 */
function initializePreviewPage() {
    console.log('미리보기 페이지 초기화 중...');
    
    // 템플릿 선택 기능은 이미 HTML에 구현됨
    // 추가 기능이 필요하면 여기에 구현
}

/**
 * 성공 페이지 초기화
 */
function initializeSuccessPage() {
    console.log('성공 페이지 초기화 중...');
    
    // 축하 애니메이션
    celebrateSuccess();
}

/**
 * 툴팁 초기화
 */
function initializeTooltips() {
    // Bootstrap 툴팁이 있다면 초기화
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (window.bootstrap && bootstrap.Tooltip) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * 부드러운 스크롤
 */
function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * 로딩 상태 관리
 */
function initializeLoadingStates() {
    // 버튼 클릭 시 로딩 상태 표시
    document.querySelectorAll('.btn[type="submit"]').forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                showButtonLoading(this);
            }
        });
    });
}

/**
 * 에러 처리 초기화
 */
function initializeErrorHandling() {
    // 전역 에러 처리
    window.addEventListener('error', function(e) {
        console.error('JavaScript 에러:', e.error);
        // 사용자에게 친화적인 에러 메시지 표시 (선택사항)
    });
    
    // Promise 에러 처리
    window.addEventListener('unhandledrejection', function(e) {
        console.error('처리되지 않은 Promise 에러:', e.reason);
    });
}

/**
 * 요소 애니메이션
 */
function animateElements(selector, animationClass) {
    const elements = document.querySelectorAll(selector);
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add(animationClass);
        }, index * 100);
    });
}

/**
 * 일기 카드 향상
 */
function enhanceDiaryCards() {
    const diaryCards = document.querySelectorAll('.card');
    
    diaryCards.forEach(card => {
        // 호버 시 그림자 효과
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow-soft');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow-soft');
        });
    });
}

/**
 * 폼 유효성 검사
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // 첫 번째 에러 필드로 스크롤
                const firstError = form.querySelector(':invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstError.focus();
                }
            }
            
            form.classList.add('was-validated');
        });
    });
}

/**
 * 자동 저장 기능
 */
function initializeAutoSave() {
    const textareas = document.querySelectorAll('textarea');
    const inputs = document.querySelectorAll('input[type="text"]');
    
    [...textareas, ...inputs].forEach(element => {
        let timeout;
        
        element.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                saveToLocalStorage(this.name, this.value);
                showAutoSaveIndicator();
            }, 2000); // 2초 후 자동 저장
        });
        
        // 페이지 로드 시 저장된 내용 복원
        const savedValue = getFromLocalStorage(element.name);
        if (savedValue) {
            element.value = savedValue;
        }
    });
}

/**
 * 글자 수 카운터
 */
function initializeCharacterCounter() {
    const textarea = document.querySelector('#diaryContent');
    const counter = document.querySelector('#charCount');
    
    if (textarea && counter) {
        function updateCounter() {
            const length = textarea.value.length;
            const maxLength = 600;
            
            counter.textContent = length;
            
            // 색상 변경
            if (length > maxLength * 0.9) { // 90% 이상
                counter.classList.add('text-warning');
                counter.classList.remove('text-success');
            } else if (length > maxLength * 0.7) { // 70% 이상
                counter.classList.add('text-success');
                counter.classList.remove('text-warning');
            } else {
                counter.classList.remove('text-warning', 'text-success');
            }
            
            // 최대 길이 초과 시 경고
            if (length >= maxLength) {
                counter.classList.add('text-danger');
                counter.classList.remove('text-warning', 'text-success');
            } else {
                counter.classList.remove('text-danger');
            }
        }
        
        textarea.addEventListener('input', updateCounter);
        updateCounter(); // 초기 카운트
    }
}

/**
 * 버튼 로딩 상태 표시
 */
function showButtonLoading(button) {
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="loading"></span> 처리중...';
    
    // 원래 상태로 복원 (5초 후)
    setTimeout(() => {
        button.disabled = false;
        button.innerHTML = originalText;
    }, 5000);
}

/**
 * 자동 저장 표시
 */
function showAutoSaveIndicator() {
    const indicator = document.getElementById('autoSaveIndicator') || createAutoSaveIndicator();
    indicator.style.display = 'block';
    indicator.textContent = '자동 저장됨';
    
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 2000);
}

/**
 * 자동 저장 표시기 생성
 */
function createAutoSaveIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'autoSaveIndicator';
    indicator.className = 'position-fixed top-0 end-0 m-3 alert alert-success alert-dismissible';
    indicator.style.display = 'none';
    indicator.style.zIndex = '9999';
    document.body.appendChild(indicator);
    return indicator;
}

/**
 * 로컬 스토리지 저장
 */
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(`diary_${key}`, value);
    } catch (e) {
        console.warn('로컬 스토리지 저장 실패:', e);
    }
}

/**
 * 로컬 스토리지 읽기
 */
function getFromLocalStorage(key) {
    try {
        return localStorage.getItem(`diary_${key}`);
    } catch (e) {
        console.warn('로컬 스토리지 읽기 실패:', e);
        return null;
    }
}

/**
 * 축하 애니메이션
 */
function celebrateSuccess() {
    // 성공 아이콘 애니메이션
    const successIcon = document.querySelector('.bi-check-lg');
    if (successIcon) {
        successIcon.parentElement.classList.add('success-icon');
    }
    
    // 간단한 축하 효과
    setTimeout(() => {
        console.log('🎉 포토북 주문이 완료되었습니다!');
    }, 1000);
}

// 전역 변수로 선택 정보 업데이트 함수 정의
let updateSelectionInfo;

/**
 * 일기 선택 기능 초기화
 */
function initializeDiarySelection() {
    console.log('일기 선택 기능 초기화 실행 중...');
    
    const checkboxes = document.querySelectorAll('.diary-checkbox');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const deselectAllBtn = document.getElementById('deselectAllBtn');
    const selectionInfo = document.getElementById('selectionInfo');
    const selectedCountSpan = document.getElementById('selectedCount');
    const estimatedPagesSpan = document.getElementById('estimatedPages');
    const validationMessage = document.getElementById('validationMessage');
    const createPhotobookBtn = document.getElementById('createPhotobookBtn');
    const selectedDiariesInput = document.getElementById('selectedDiariesInput');
    
    console.log('체크박스 개수:', checkboxes.length);
    console.log('필수 DOM 요소들 존재 여부:', {
        selectionInfo: !!selectionInfo,
        selectedCountSpan: !!selectedCountSpan,
        estimatedPagesSpan: !!estimatedPagesSpan,
        validationMessage: !!validationMessage,
        createPhotobookBtn: !!createPhotobookBtn,
        selectedDiariesInput: !!selectedDiariesInput
    });
    
    // 필수 요소들이 없으면 초기화 중단
    if (!selectionInfo || !selectedCountSpan || !estimatedPagesSpan || 
        !validationMessage || !createPhotobookBtn || !selectedDiariesInput) {
        console.error('필수 DOM 요소를 찾을 수 없습니다. 초기화를 중단합니다.');
        return;
    }
    
    // 선택 정보 업데이트 함수 정의
    updateSelectionInfo = function() {
        console.log('선택 정보 업데이트 중...');
        const selectedCheckboxes = document.querySelectorAll('.diary-checkbox:checked');
        const selectedCount = selectedCheckboxes.length;
        const selectedIds = Array.from(selectedCheckboxes).map(cb => cb.value);
        
        console.log('선택된 체크박스 수:', selectedCount);
        console.log('선택된 ID들:', selectedIds);
        
        // 페이지 수 계산
        const totalPages = calculatePages(selectedCount);
        
        // 검증 결과
        const validation = validateDiarySelection(selectedCount);
        
        // UI 업데이트
        if (selectedCount > 0) {
            selectionInfo.style.display = 'block';
            selectedCountSpan.textContent = selectedCount;
            estimatedPagesSpan.textContent = totalPages;
            selectedDiariesInput.value = selectedIds.join(',');
            
            console.log('Hidden input에 설정된 값:', selectedDiariesInput.value);
            
            // 검증 메시지 표시
            validationMessage.innerHTML = validation.message;
            validationMessage.className = `small mb-2 ${validation.valid ? 'text-success' : 'text-danger'}`;
            
            // 버튼 상태
            createPhotobookBtn.disabled = !validation.valid;
            
            // 선택된 카드 강조
            updateCardSelection(selectedIds);
        } else {
            selectionInfo.style.display = 'none';
            selectedDiariesInput.value = '';
            createPhotobookBtn.disabled = true;
            updateCardSelection([]);
        }
    };
    
    // 카드 선택 상태 시각적 표시
    function updateCardSelection(selectedIds) {
        const diaryCards = document.querySelectorAll('.diary-card');
        diaryCards.forEach(card => {
            const diaryId = card.dataset.diaryId;
            if (selectedIds.includes(diaryId)) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
    }
    
    // 체크박스 변경 이벤트 등록
    checkboxes.forEach((checkbox, index) => {
        checkbox.addEventListener('change', updateSelectionInfo);
        console.log(`체크박스 ${index + 1} 이벤트 리스너 등록됨`);
    });
    
    // 전체 선택 버튼
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            console.log('전체 선택 버튼 클릭됨');
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
            updateSelectionInfo();
        });
    }
    
    // 전체 해제 버튼
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function() {
            console.log('전체 해제 버튼 클릭됨');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            updateSelectionInfo();
        });
    }
    
    // 초기 상태 설정
    updateSelectionInfo();
    console.log('일기 선택 기능 초기화 완료');
}

/**
 * 페이지 수 계산
 */
function calculatePages(selectedCount) {
    // 총 페이지 = 표지(2페이지) + 선택한 일기 수
    let totalPages = 2 + selectedCount;
    
    // 2페이지 단위로 올림
    if (totalPages % 2 !== 0) {
        totalPages += 1;
    }
    
    return totalPages;
}

/**
 * 일기 선택 검증
 */
function validateDiarySelection(selectedCount) {
    const minDiaries = 22;
    const maxDiaries = 128;
    const recommendedMin = 30;
    const recommendedMax = 50;
    
    if (selectedCount < minDiaries) {
        return {
            valid: false,
            message: `<i class="bi bi-exclamation-triangle"></i> 최소 ${minDiaries}개 일기를 선택해주세요. (현재: ${selectedCount}개)`
        };
    }
    
    if (selectedCount > maxDiaries) {
        return {
            valid: false,
            message: `<i class="bi bi-exclamation-triangle"></i> 최대 ${maxDiaries}개까지 선택 가능합니다. (현재: ${selectedCount}개)`
        };
    }
    
    // 권장 범위 체크
    if (selectedCount >= recommendedMin && selectedCount <= recommendedMax) {
        return {
            valid: true,
            message: `<i class="bi bi-check-circle"></i> 권장 범위입니다! (${selectedCount}개 선택)`
        };
    }
    
    return {
        valid: true,
        message: `<i class="bi bi-info-circle"></i> 선택 완료 (권장: ${recommendedMin}~${recommendedMax}개)`
    };
}

/**
 * 유틸리티 함수들
 */

// 날짜 포맷팅
function formatDate(date) {
    return new Date(date).toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// 텍스트 자르기
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// 디바운스 함수
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 전역으로 노출할 함수들
window.DiaryApp = {
    formatDate,
    truncateText,
    debounce,
    showButtonLoading,
    celebrateSuccess
};

console.log('📖 일기 포토북 서비스 JavaScript 로드 완료');