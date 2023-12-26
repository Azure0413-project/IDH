function AdjustPage(){
    let urlArr = location.href.split("/");
    let targetUrl = ""
    for(let i=0; i<urlArr.length-1; ++i){
        targetUrl += urlArr[i] + "/";
    }
    targetUrl += "Z";
    location.href = targetUrl;
}

function SearchPage(){
    let urlArr = location.href.split("/");
    let targetUrl = ""
    for(let i=0; i<urlArr.length-1; ++i){
        targetUrl += urlArr[i] + "/";
    }
    targetUrl += "Y";
    location.href = targetUrl;
    let setTmp = new Set(JSON.parse(sessionStorage.getItem(nurseId)));
    $.ajax({
        url: "nurseArea/SearchFunc/",
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

function removeAllNodes(tag){
    while(tag.firstChild){
        tag.removeChild(tag.firstChild);
    }
    return;
}

function closeModal() {
    document.getElementById("modal").classList.toggle("hidden");
}

// function SaveAdjust(){
// const existedList = document.getElementById("existedList");
// let result = [];
// let childList = existedList.childNodes;
// for(let i=1; i<childList.length; ++i){
//   result.push(childList.innerText);
// }
// result.sort();
// sessionStorage.setItem(nurseId, JSON.stringify(Array.from(result)));
// alert("success!")
// console.log(existedList.childNodes);
// }

function liClickEvent(e) {
    console.log(e);
}
  