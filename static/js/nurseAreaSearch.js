function AdjustPage(){
    location.href = "http://127.0.0.1:8000/index/" + "Z";
}

function SearchPage(){
    location.href = "http://127.0.0.1:8000/index/" + "Y";
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
        location.href =  "http://127.0.0.1:8000/index/" + `get_nurse_detail/${bed}/${idh}`;
    }
}

function removeAllNodes(tag){
    while(tag.firstChild){
        tag.removeChild(tag.firstChild);
    }
    return;
}

function close_modal() {
    document.getElementById("modal").classList.toggle("hidden");
    location.href = "http://127.0.0.1:8000/index/" + "Y";
}

function liClickEvent(e) {
    console.log(e);
}
  