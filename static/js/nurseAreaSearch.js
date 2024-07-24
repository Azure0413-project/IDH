function AdjustPage(){
    let nurseId = document.getElementById("nurseId").value;
    location.href = rootUrl + `NAadjust/${nurseId}`;
}

function SearchFunc(){
    let nurseId = document.getElementById('nurseId').value;
    let setTmp = JSON.parse(sessionStorage.getItem(nurseId));
    let bedStr = "emp";
    if(setTmp && setTmp.length > 0){
        bedStr = setTmp.join("-");
    }
    targetUrl = rootUrl + `NASearch/${nurseId}/${bedStr}`;
    location.href = targetUrl;
    console.log('search');
}

function SwitchNurseList(){
  targetUrl = rootUrl + `NurseArea/NurseList`;
  location.href = targetUrl;
}

function ClickOnPatient(bed, idh, name, mode, done, first_click, SBP, DBP, random_code) {
  console.log("FIRST_CLICK:", first_click);
  SBP = parseInt(SBP);
  DBP = parseInt(DBP);
  random_code = parseInt(random_code);
  if (random_code == 1 && idh > 85 && done == 'False' && first_click == 'True') {
    let warningModal = document.getElementById("warningModal");
    document.getElementById("warning-left-SBP").style.display='';
    document.getElementById("warning-left-DBP").style.display='';
    document.getElementById("warning-right").style.display='';
    document.getElementById("confirmWarningBtn").style.display='';
    document.getElementById("warningClickBtn").style.display='None';
    document.getElementById("patientBed").innerText = bed;
    document.getElementById("patientName").innerText = name;
    document.getElementById("SBP").value = SBP;
    document.getElementById("DBP").value = DBP;
    console.log("danger");
    warningModal.classList.toggle("hidden");
  } else if (random_code == 1 && idh > 85 && done == 'False' && first_click == 'False') {
    warningModal.classList.toggle("hidden");
    document.getElementById("warning-left-SBP").style.display='None';
    document.getElementById("warning-left-DBP").style.display='None';
    document.getElementById("warning-right").style.display='None';
    document.getElementById("confirmWarningBtn").style.display='None';
    document.getElementById("warningClickBtn").style.display='';
    document.getElementById("patientBed").innerText = bed;
    document.getElementById("patientName").innerText = name;
    document.getElementById("SBP").value = SBP;
    document.getElementById("DBP").value = DBP;
    // $.get(rootUrl+`warning_click/${bed}/${name}`, ()=>{ //0416
    //   console.log("first warning click.");
    // });
    // location.reload();
  } else {
    let nurseId = document.getElementById('nurseId').value;
    location.href = rootUrl + `get_nurse_detail/${nurseId}/${bed}/${idh}`;
  }
}

// function ClickOnPatient(bed, idh, name, mode, done, first_click) {
//   if (idh > 70 && done == 'False' && first_click == 'True') {
//     let warningModal = document.getElementById("warningModal");
//     pBed = document.getElementById("patientBed");
//     pName = document.getElementById("patientName");
//     pBed.innerText = bed;
//     pName.innerText = name;
//     console.log("danger");
//     warningModal.classList.toggle("hidden");
//   } else if (idh > 70 && done == 'False' && first_click == 'False') {
//     $.get(rootUrl+`warning_click/${bed}/${name}`, ()=>{ //0416
//       console.log("first warning click.");
//     });
//     location.reload();
//   } else {
//     let nurseId = document.getElementById('nurseId').value;
//     location.href = rootUrl + `get_nurse_detail/${nurseId}/${bed}/${idh}`;
//   }
// }

window.onclick = function (event) {
  if (event.target.id == "modal") {
    close_modal();
  } else if(event.target.id == "warningModal"){
    CloseWarningModal();
  }
};

function close_modal() {
    let nurseId = location.href.split("/")[5];
    let setTmp = JSON.parse(sessionStorage.getItem(nurseId));
    let bedStr = "emp";
    if (setTmp && setTmp.length > 0) {
      bedStr = setTmp.join("-");
    }
    targetUrl = rootUrl + `NASearch/${nurseId}/${bedStr}`;
    location.href = targetUrl;
    console.log("search");
}

function liClickEvent(e) {
    console.log(e);
    SearchFunc();
}
  
function CloseWarningModal() {
    document.getElementById("warningModal").classList.toggle("hidden");
    // SearchFunc();
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
      url: rootUrl + "warningFeedback/",
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