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

// Left panel
function openTab(evt, tabName, area) {
  document.location.href = "http://140.116.247.175:80/index/" + area;
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
  }
};

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
  let back = document.location.href;
  let area = back.split("/");
  if (area[4] == "get_record") {
    document.getElementById("modal").classList.add("hidden");
    // console.log(modal);
  } else {
    document.location.href = "http://140.116.247.175:80/index/" + area[5];
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
  if (bed.classList.contains("bed-feedback-active")) {
    bed.children[1].remove();
  } else {
    let inputEle = document.createElement("input");
    inputEle.type = "hidden";
    inputEle.value = bed.id.split("-")[1];
    inputEle.name = "idh-patient";
    bed.appendChild(inputEle);
  }
  bed.classList.toggle("bed-feedback-active");
}