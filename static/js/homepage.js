// mode:
// 0 -> dashboard
// 1 -> each tag
function ClickOnPatient(bed, idh, name, mode) {
  if (idh > 85) {
    pBed = document.getElementById("patientBed");
    pName = document.getElementById("patientName");
    pBed.innerText = bed;
    pName.innerText = name;
    console.log("danger");
    warningModal.classList.toggle("hidden");
  } else {
    if (mode == 0) {
      location.href = `get_detail/dashboard/${bed}/${idh}`;
    } else {
      location.href = `get_detail/${bed[0]}/${bed}/${idh}`;
    }
  }
  // if(serverity_level == 1){
  //     pBed = document.getElementById('patientBed');
  //     pName = document.getElementById('patientName');
  //     pBed.innerText = bed;
  //     pName.innerText = name;
  //     console.log("danger");
  //     warningModal.classList.toggle("hidden");
  // } else {
  //     console.log(bed, idh, serverity_level)
  //     location.href = `get_detail/dashboard/${bed}/${idh}`;
  // }
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
        location.href = originLocation;
      } else {
        // 畫面提醒 送出表單失敗
        alert("Add fail...");
      }
    },
    error: (res) => {
      console.log(res);
    },
  });
}
