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
    if (textarea) {
        const counter = document.createElement('div');
        counter.className = 'text-muted small mt-1';
        counter.id = 'characterCounter';
        textarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            const length = textarea.value.length;
            counter.textContent = `${length.toLocaleString()}자`;
            
            if (length > 1000) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
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