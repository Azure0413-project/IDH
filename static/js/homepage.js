
const threshold = 85;

// mode:
// 0 -> dashboard
// 1 -> each tag
function ClickOnPatient(bed, idh, name, mode, done, first_click, SBP, DBP, random_code) {
  console.log("FIRST_CLICK:", first_click);
  SBP = parseInt(SBP);
  DBP = parseInt(DBP);
  random_code = parseInt(random_code);
if (random_code == 1 && idh > threshold && done == 'False' && first_click == 'False') {
  let warningModal = document.getElementById("warningModal");
  
  let sbpBox = document.getElementById("warning-left-SBP");
  if (sbpBox) sbpBox.style.display = '';

  let dbpBox = document.getElementById("warning-left-DBP");
  if (dbpBox) dbpBox.style.display = '';

  let rightBox = document.getElementById("warning-right");
  if (rightBox) rightBox.style.display = '';

  let confirmBtn = document.getElementById("confirmWarningBtn");
  if (confirmBtn) confirmBtn.style.display = '';

  let clickBtn = document.getElementById("warningClickBtn");
  if (clickBtn) clickBtn.style.display = 'None';

  let bedSpan = document.getElementById("patientBed");
  if (bedSpan) bedSpan.innerText = bed;

  let nameSpan = document.getElementById("patientName");
  if (nameSpan) nameSpan.innerText = name;

  let sbpInput = document.getElementById("SBP");
  if (sbpInput) sbpInput.value = SBP;

  let dbpInput = document.getElementById("DBP");
  if (dbpInput) dbpInput.value = DBP;

  console.log("danger");

  if (warningModal) warningModal.classList.toggle("hidden");
}

  // else if (random_code == 1 && idh > threshold && done == 'False' && first_click == 'False') {
  //   warningModal.classList.toggle("hidden");
  //   document.getElementById("warning-left-SBP").style.display='None';
  //   document.getElementById("warning-left-DBP").style.display='None';
  //   document.getElementById("warning-right").style.display='None';
  //   document.getElementById("confirmWarningBtn").style.display='None';
  //   document.getElementById("warningClickBtn").style.display='';
  //   document.getElementById("patientBed").innerText = bed;
  //   document.getElementById("patientName").innerText = name;
  //   document.getElementById("SBP").value = SBP;
  //   document.getElementById("DBP").value = DBP;
    // $.get(rootUrl+`warning_click/${bed}/${name}`, ()=>{ //0416
    //   console.log("first warning click.");
    // });
    // location.reload();
  // }
   else {
    let targetUrl = "";
    let urlArr = location.href.split("/");
    for(let i=0; i<urlArr.length-1; ++i){
      targetUrl += urlArr[i] + "/";
    }
    if (mode == 0) {
      location.href = targetUrl + `get_detail/dashboard/${bed}/${idh}`;
    } else {
      location.href = targetUrl + `get_detail/${bed[0]}/${bed}/${idh}`;
    }
  }
}

function CloseWarningModal() {
  let warningModal = document.getElementById("warningModal");
  warningModal.classList.toggle("hidden");
}

function OpenWarningModal(){
  
}

function CloseExportFileModal() {
  let exportFileModal = document.getElementById("exportFileModal");
  exportFileModal.classList.toggle("hidden");
}

function SubmitWarningClick() {
  let pBed = document.getElementById("patientBed").innerText;
  let pName = document.getElementById("patientName").innerText;
  let formData = new FormData(document.getElementById("warningReport"));
  let originLocation = location.href;
  formData.append("patientBed", pBed);
  formData.append("patientName", pName);
  result = {};
  for (let p of formData.entries()) {
    result[p[0]] = p[1];
  }
  $.ajax({
    url: rootUrl+"warning_click/",
    method: "POST",
    headers: {
      "X-CSRFToken": $('[name="csrf-token"]').attr("content"),
    },
    dataType: "json",
    data: result,
    success: (res) => {
      if (res["status"] == "success") {
        // 頁面跳轉
        alert("Add success.");
        // 記錄床號與時間
        location.href = originLocation;
      } else {
        // 畫面提醒 送出表單失敗
        alert("Add fail.\n" + res["msg"]);
      }
    },
    error: (res) => {
      console.log(res);
    },
  });
}

function SubmitWarning() {
  let pBed = document.getElementById("patientBed").innerText;
  let pName = document.getElementById("patientName").innerText;
  let formData = new FormData(document.getElementById("warningReport"));
  let originLocation = location.href;
  formData.append("patientBed", pBed);
  formData.append("patientName", pName);
  result = {};
  for (let p of formData.entries()) {
    result[p[0]] = p[1];
  }
  $.ajax({
    url: rootUrl+"warningFeedback/",
    method: "POST",
    headers: {
      "X-CSRFToken": $('[name="csrf-token"]').attr("content"),
    },
    dataType: "json",
    data: result,
    success: (res) => {
      if (res["status"] == "success") {
        // 頁面跳轉
        alert("Add success.");
        // 記錄床號與時間
        location.href = originLocation;
      } else {
        // 畫面提醒 送出表單失敗
        alert("Add fail.\n" + res["msg"]);
      }
    },
    error: (res) => {
      console.log(res);
    },
  });
}

function SubmitExportFile() {
  let start_time = document.getElementById("export-file-start").value;
  let end_time = document.getElementById("export-file-end").value;
  let formData = new FormData(document.getElementById("exportFileForm"));
  formData.append("start_time", start_time);
  formData.append("end_time", end_time);
  result = {};
  for (let p of formData.entries()) {
    result[p[0]] = p[1];
  }
  $.ajax({
    url: rootUrl+"export_file/",
    method: "POST",
    headers: {
      "X-CSRFToken": $('[name="csrfmiddlewaretoken"]')[0].value,
    },
    xhrFields: {
      responseType: 'blob' // to avoid binary data being mangled on charset conversion
    },
    dataType: "binary",
    data: result,
    success: (res) => {
      console.log("this status:", res);
      console.log(new Blob([res]))
      var blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      var url = window.URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'PatientData.xlsx';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    },
    error: (xhr, status, error) => {
      console.log("err res:", error);
    },
  });
}

$(document).ready(function () {
  document.getElementById('other-other-check').onchange = function(){
    document.getElementById('other-other-text').disabled = !this.checked;
  }
  document.getElementById('nursing-other-check').onchange = function(){
    document.getElementById('nursing-other-text').disabled = !this.checked;
  }
  document.getElementById('setting-other-check').onchange = function(){
    document.getElementById('setting-other-text').disabled = !this.checked;
  }
  document.getElementById('inject-other-check').onchange = function(){
    document.getElementById('inject-other-text').disabled = !this.checked;
  }
  document.getElementById('drug-other-check').onchange = function(){
    document.getElementById('drug-other-text').disabled = !this.checked;
  }
});
