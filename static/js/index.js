function runTime() {
  let now = new Date();
  let timeDiv = document.getElementById("currentTime");
  let nowY = now.getFullYear();
  let nowM = now.getMonth() + 1;
  let nowD = now.getDate();
  let nowW = now.getDay();
  let nowH = now.getHours();
  let nowI = now.getMinutes();
  let nowS = now.getSeconds();

  if (nowH < 10) {
    nowH = "0" + nowH;
  }
  if (nowI < 10) {
    nowI = "0" + nowI;
  }
  if (nowS < 10) {
    nowS = "0" + nowS;
  }
  switch (nowW) {
    case 0:
      nowW = "日";
      break;
    case 1:
      nowW = "一";
      break;
    case 2:
      nowW = "二";
      break;
    case 3:
      nowW = "三";
      break;
    case 4:
      nowW = "四";
      break;
    case 5:
      nowW = "五";
      break;
    case 6:
      nowW = "六";
      break;
  }

  let nowStr =
    nowY +
    " 年 " +
    nowM +
    " 月 " +
    nowD +
    " 日 星期" +
    nowW +
    "  " +
    nowH +
    ":" +
    nowI +
    ":" +
    nowS;
  timeDiv.innerText = nowStr;
}

runTime();
setInterval(runTime, 1000);

function refresh() {
  window.location.reload();
}
setInterval(refresh, 180000);

// const rootUrl = "http://127.0.0.1:8000/index/";
const rootUrl = "http://192.168.83.226:8000/index/";

// Left panel
function openTab(evt, tabName, area) {
  document.location.href = rootUrl + area;
}

function openNurseArea(){
  console.log("open nurse area.");
  document.location.href = rootUrl + 'Y';
}

const bed = [
  "A1", "A2", "A3", "A5", "A6", "A7", "A8", "A9",
  "B1", "B2", "B3", "B5", "B6", "B7", "B8", "B9",
  "C1", "C2", "C3", "C5", "C6", "C7", "C8", "C9",
  "D1", "D2", "D3", "D5", "D6", "D7", "D8", "D9",
  "E1", "E2", "E3", "E5", "E6", "E7", "E8",
  "I1", "I2",
];
const modal = document.getElementById("modal");
window.onclick = function (event) {
  if (event.target.id == "modal") {
    clear();
  // } else if(event.target.id == "feedbackModal"){
  //   document.getElementById("feedbackModal").classList.toggle("hidden");
  } else if(event.target.id == "warningModal"){
    document.getElementById("warningModal").classList.toggle("hidden");
  } else if(event.target.id == "exportFileModal"){
    document.getElementById("exportFileModal").classList.toggle("hidden");
  }
};

function openExportFileModal() {
  document.getElementById("exportFileModal").classList.toggle("hidden");
}

function closeModal() {
  clear();
}
let flag = true;
function next() {

  if (flag) {
    flag = false;
    document.getElementById("patient2").innerText = document.getElementById("patient").innerText;
    document.getElementsByClassName("modal-left")[0].style.display = "none";
    document.getElementsByClassName("modal-right")[0].style.display = "none";
    document.getElementsByClassName("modal-table")[0].classList.remove("hidden");
    document.getElementById("left").src = "/static/img/left_active.svg";
    document.getElementById("right").src = "/static/img/right_inactive.svg";
  }
}

function prev() {
  if (!flag) {
    flag = true;
    document.getElementsByClassName("modal-left")[0].style.display = "flex";
    document.getElementsByClassName("modal-right")[0].style.display = "flex";
    document.getElementsByClassName("modal-table")[0].classList.add("hidden");
    document.getElementById("left").src = "/static/img/left_inactive.svg";
    document.getElementById("right").src = "/static/img/right_active.svg";
  }
}

function clear() {
  console.log("clear");
  let back = document.location.href;
  let area = back.split("/");
  if (area[4] == "get_record") {
    let tmp_form = document.getElementById("idh-tmp-form");
    let sign_checked = document.querySelectorAll('[type=radio]:checked');
    let treatment_checked = document.querySelectorAll('[type=checkbox]:checked');
    let tmp_list = "";
    for(let i = 0; i < sign_checked.length; i++) {
      let p_id = sign_checked[i].name.split("-");
      tmp_list = tmp_list + p_id[1] + '-' + sign_checked[i].value;
      for(let j = 0; j < treatment_checked.length; j++) {
        let tmp_id = treatment_checked[j].name.split("-")[1];
        if(tmp_id == p_id[1]){
          tmp_list = tmp_list + '+' + treatment_checked[j].value;
        }
      }
      tmp_list += '/'
    }
    tmp_form.value = tmp_list;
    console.log(tmp_list);
    document.getElementById("modal").classList.add("hidden");
    // console.log(modal);
  } else {
    document.location.href = rootUrl + area[5];
    document.getElementsByClassName("modal-left")[0].style.display = "flex";
    document.getElementsByClassName("modal-right")[0].style.display = "flex";
    document.getElementsByClassName("modal-table")[0].classList.add("hidden");
    document.getElementById("left").src = "/static/img/left_inactive.svg";
    document.getElementById("right").src = "/static/img/right_active.svg";
    modal.classList.add("hidden");
    flag = true;
  }
}

let chart, xAxis, SBP, pulse, CVP, exist, linechart, bands;
let linecharts = [];

function changeStatus(bed_id) {
  let bed = document.getElementById(bed_id);
  bed_num = bed_id.split('-')[1];
  let idh_bed = document.getElementById("idh-patients-list");
  if(sessionStorage.getItem("orangeList") == null){
    sessionStorage.setItem("orangeList", "[]");
    sessionStorage.setItem("yellowList", "[]");
  }
  if (bed.classList.contains("bed-feedback-active")) {
    idh_bed.value = idh_bed.value.replace(bed_num + '-', "");
    bed.classList.toggle("bed-feedback-active");
    console.log(idh_bed);
  } else if(bed.classList.contains("bed-feedback-active-20ver")){
    idh_bed.value = idh_bed.value.replace(bed_num + '-', "");
    let listTmp = JSON.parse(sessionStorage.getItem("yellowList"));
    if(!listTmp.includes(bed_num)){
      listTmp.push(bed_num);
    }
    sessionStorage.setItem("yellowList", JSON.stringify(listTmp));
    bed.classList.toggle("bed-feedback-active-20ver");
  } else if(bed.classList.contains("bed-feedback-active-bothver")){
    idh_bed.value = idh_bed.value.replace(bed_num + '-', "");
    let listTmp = JSON.parse(sessionStorage.getItem("orangeList"));
    if(!listTmp.includes(bed_num)){
      listTmp.push(bed_num);
    }
    sessionStorage.setItem("orangeList", JSON.stringify(listTmp));
    bed.classList.toggle("bed-feedback-active-bothver");
  } else {
    let yellowTmp = JSON.parse(sessionStorage.getItem("yellowList"));
    let orangeTmp = JSON.parse(sessionStorage.getItem("orangeList"));
    if(yellowTmp.includes(bed_num)){
      bed.classList.toggle("bed-feedback-active-20ver");
    } else if(orangeTmp.includes(bed_num)){
      bed.classList.toggle("bed-feedback-active-bothver");
    } else{
      bed.classList.toggle("bed-feedback-active");
    }
    idh_bed.value += bed_num + "-";
    console.log(idh_bed);
  }
}

function SwitchNurseList() {
  targetUrl = rootUrl + `NurseArea/NurseList`;
  location.href = targetUrl;
}

function SwitchRandomCodeDisplay(){
  let allRedCheckList = $('img.redCheck');
  for(let i=0; i<allRedCheckList.length; ++i){
    if(allRedCheckList[i].hidden == true){
      allRedCheckList[i].hidden = false;
    } else {
      allRedCheckList[i].hidden = true;
    }
  }
}

// 護理師處置時間
document.addEventListener("DOMContentLoaded", function() {
  const handleSelect = document.getElementById("handle-select");
  const handleTime = document.getElementById("handle-time");
  
  // Generate times in 15-minute intervals
  const interval = 5; // Interval in minutes
  const now = new Date();
  const currentHours = now.getHours();
  const currentMinutes = now.getMinutes();
  let defaultTime = "";

  // Populate the select options
  for (let hour = 0; hour <= currentHours; hour++) {
      for (let minute = 0; minute < 60; minute += interval) {
          if (hour === currentHours && minute > currentMinutes) break; // Stop if time exceeds current time
          
          const time = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
          const option = document.createElement("option");
          option.value = time.replace(":", ""); // For easier handling in JS
          option.textContent = time;
          handleSelect.appendChild(option);
          
          // Set default time to current time
          if (hour === currentHours && minute <= currentMinutes) {
            defaultTime = time; // Store the value for the default time
          }
      }
  }
  handleTime.value = defaultTime;
  
});

function HandleTimeAppend(){
  
  let handle_time = document.getElementById(`handle-time`);  //input text
  let selected_handle_time = document.getElementById(`handle-select`).value; //selected time

  // current_time = selected_handle_time.replace(":", "");
  handle_time.value = selected_handle_time.slice(0,2)+":"+selected_handle_time.slice(2);
  
  
  return;
}

// blinking
let originalTitle = document.title;  // 儲存原本的標題
let blinkInterval;  // 儲存標題閃爍的定時器ID
let alertInterval;  // 儲存圖示閃爍的定時器ID
let isTabVisible = true;

const originalFavicon = "/static/img/kidney.svg"; // 原本的圖示
const alertFavicon = "/static/img/kidney_warning.svg"; // 警告圖示

// 開始閃爍標題
function startBlinkingTitle() {
    if (!blinkInterval) {
        blinkInterval = setInterval(() => {
            document.title = document.title === originalTitle ? " 請查看此頁面！ ⏳" : originalTitle;
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
    const alertElement = document.querySelector('.alert-trigger');
    if (alertElement && document.hidden) {
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