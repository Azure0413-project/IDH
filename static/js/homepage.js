// mode:
// 0 -> dashboard
// 1 -> each tag
function ClickOnPatient(bed, idh, name, mode, done) {
  if (idh > 85 && done == 'False') {
    pBed = document.getElementById("patientBed");
    pName = document.getElementById("patientName");
    pBed.innerText = bed;
    pName.innerText = name;
    console.log("danger");
    warningModal.classList.toggle("hidden");
  } else {
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
    url: "warningFeedback/",
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
