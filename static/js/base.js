let originalTitle = document.title;  // 儲存原本的標題
let blinkInterval;  // 儲存標題閃爍的定時器ID
let alertInterval;  // 儲存圖示閃爍的定時器ID
let isTabVisible = true;

let originalFavicon = "/static/img/kidney.svg"; // 原本的圖示
let alertFavicon = "/static/img/kidney_warning.svg"; // 警告圖示

// 開始閃爍標題
function startBlinkingTitle() {
    if (!blinkInterval) {
        blinkInterval = setInterval(() => {
            document.title = document.title === originalTitle ? "請回來！ ⏳" : originalTitle;
        }, 1000);  // 每1秒變更一次
    }
}

// 停止閃爍標題
function stopBlinkingTitle() {
    clearInterval(blinkInterval);
    blinkInterval = null;
    document.title = originalTitle;
}

// 創建/切換圖示
function createFavicon(href) {
    const existingFavicon = document.getElementById("favicon");
    if (existingFavicon) {
        existingFavicon.remove();
    }
    const newFavicon = document.createElement("link");
    newFavicon.id = "favicon";
    newFavicon.rel = "icon";
    newFavicon.href = href;
    newFavicon.type = "image/x-icon";
    document.head.appendChild(newFavicon);
}

// 開始閃爍圖示
function startFaviconAlert() {
    if (!alertInterval) {
        alertInterval = setInterval(() => {
            const currentFavicon = document.getElementById("favicon").href;
            createFavicon(currentFavicon.includes("kidney.svg") ? alertFavicon : originalFavicon);
        }, 100);  // 圖示閃爍間隔
    }
}

// 停止閃爍圖示
function stopFaviconAlert() {
    clearInterval(alertInterval);
    alertInterval = null;
    createFavicon(originalFavicon);
}

// 檢查是否有 .alert-trigger 元素並根據需要啟動或停止特效
function checkForAlertTrigger() {
    const alertElement = document.querySelector('.danger-bg');
    if (alertElement && document.hidden) {
        console.log(alertElement);
        startBlinkingTitle();
        startFaviconAlert();
    } else {
        stopBlinkingTitle();
        stopFaviconAlert();
    }
}

// 當頁面進入背景或變為可見時觸發檢查
document.addEventListener("visibilitychange", function() {
    isTabVisible = !document.hidden;
    checkForAlertTrigger();
});

// 定期檢查 `.alert-trigger` 是否出現
setInterval(checkForAlertTrigger, 1000);  // 每秒檢查一次

// 頁面載入時設置初始圖示
document.addEventListener("DOMContentLoaded", function() {
    createFavicon(originalFavicon);
});

// refresh web
let idleTime = 0; // 閒置時間計數
const idleThreshold = 300; // 閒置時間閾值為 300 秒

// 重置閒置時間計數
function resetIdleTime() {
    idleTime = 0;
}

// 每秒增加閒置時間計數
setInterval(() => {
    idleTime++;
    if (idleTime % idleThreshold == 0) {
        location.reload();
    }
}, 1000);

// 當使用者有操作時，重置閒置時間並停止自動重新載入
window.addEventListener("mousemove", resetIdleTime);
window.addEventListener("keypress", resetIdleTime);
window.addEventListener("scroll", resetIdleTime);
window.addEventListener("click", resetIdleTime);
