const rootUrl = "http://127.0.0.1:8000/index/";

function AdjustPage(){
    location.href = "http://127.0.0.1:8000/index/" + "Z";
}

function SearchFunc(){
    let nurseId = document.getElementById('nurseId').value;
    let setTmp = JSON.parse(sessionStorage.getItem(nurseId));
    let bedStr = "emp";
    if(setTmp != null){
        bedStr = setTmp.join("-");
    }
    targetUrl = rootUrl + `NASearch/${nurseId}/${bedStr}`;
    location.href = targetUrl;
}

function ClickOnPatient(bed, idh, name, mode, done) {
    if (idh > 85 && done == 'True') {
        pBed = document.getElementById("patientBed");
        pName = document.getElementById("patientName");
        pBed.innerText = bed;
        pName.innerText = name;
        console.log("danger");
        warningModal.classList.toggle("hidden");
    } else {
        let nurseId = document.getElementById('nurseId').value;
        location.href = rootUrl + `get_nurse_detail/${nurseId}/${bed}/${idh}`;
    }
}

window.onclick = function (event) {
  if (event.target.id == "modal") {
    close_modal();
  }
};

function close_modal() {
    document.getElementById("modal").classList.toggle("hidden");
    SearchFunc();
    // location.href = "http://127.0.0.1:8000/index/" + "Y";
}
  