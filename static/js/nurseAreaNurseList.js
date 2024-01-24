function SwitchSearchPage(){
    location.href = rootUrl + 'Y';
}

function AdjustPage(){
    location.href = rootUrl + `NAadjust/emp`;
}

function AddNurse(){
    let empNo = document.getElementById("empNo").value;
    let nurseName = document.getElementById("nurseName").value;
    let formData = new FormData(document.getElementById("nurseInfo"));
    let originLocation = location.href;
    formData.append("empNo", empNo);
    formData.append("nurseName", nurseName);
    result = {};
    for (let p of formData.entries()) {
        result[p[0]] = p[1];
    }
    console.log(result);
    $.ajax({
        url: "NurseList",
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

function DeleteNurse(empNo){
    result = {
        'empNo': empNo
    };
    $.ajax({
        url: "DeleteNurse",
        method: "POST",
        headers: {
            "X-CSRFToken": $('[name="csrfmiddlewaretoken"]')[0].value,
        },
        dataType: "json",
        data: result,
        success: (res) => {
            if (res["status"] == "success") {
                // 頁面跳轉
                alert("Delete success.");
            } else {
                // 畫面提醒 送出表單失敗
                alert("Delete fail.\n" + res["msg"]);
            }
            location.reload();
        },
        error: (res) => {
            console.log(res);
        },
    });
}

window.onclick = function (event) {
    if (event.target.id == "nurseInfoModal") {
        OperateNurseModal();
    }
}

function OperateNurseModal(){
    const NImodal = document.getElementById("nurseInfoModal");
    NImodal.classList.toggle("hidden");
}