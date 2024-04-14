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
  if (bed.classList.contains("bed-feedback-active")) {
    idh_bed.value = idh_bed.value.replace(bed_num + '-', "");
    console.log(idh_bed);
  } else {
    idh_bed.value += bed_num + "-";
    console.log(idh_bed);
  }
  bed.classList.toggle("bed-feedback-active");
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