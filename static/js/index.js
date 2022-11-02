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

    if(nowH < 10) { nowH = '0' + nowH; }
    if(nowI < 10) { nowI = '0' + nowI; }
    if(nowS < 10) { nowS = '0' + nowS; }
    switch(nowW) {
        case 0: nowW = '日'; break;
        case 1: nowW = '一'; break;
        case 2: nowW = '二'; break;
        case 3: nowW = '三'; break;
        case 4: nowW = '四'; break;
        case 5: nowW = '五'; break;
        case 6: nowW = '六'; break;
    }

    let nowStr = nowY + ' 年 ' + nowM + ' 月 ' + nowD + ' 日 星期' + nowW + '  ' + nowH + ':' + nowI + ':' + nowS;
    timeDiv.innerText = nowStr;
}

runTime();
setInterval(runTime, 1000);

// Left panel
document.getElementById("defaultOpen").click();
function openTab(evt, cityName) {
    // Declare all variables
    let i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the link that opened the tab
    document.getElementById(cityName).style.display = "block";
    evt.currentTarget.className += " active";
}

const bed = ['a1', 'a2', 'a3', 'a5', 'a6', 'a7', 'a8', 'a9', 
             'b1', 'b2', 'b3', 'b5', 'b6', 'b7', 'b8', 'b9', 
             'c1', 'c2', 'c3', 'c5', 'c6', 'c7', 'c8', 'c9', 
             'd1', 'd2', 'd3', 'd5', 'd6', 'd7', 'd8', 'd9', 
             'e1', 'e2', 'e3', 'e5', 'e6', 'e7', 'e8', 
             'i1', 'i2']
const modal = document.getElementById("modal");

window.onclick = function (event) {
    if (event.target == modal) {
        modal.classList.add("hidden");
    }
};

function openModal(bed_id) {
    modal.classList.remove('hidden');
    document.getElementById("patient").innerText = bed_id + "  陳O鳳";
    document.getElementById("idhrate").innerText = "45%";
}
function closeModal() {
    modal.classList.add('hidden');
}

let jsonData = JSON.parse('{{ data }}');
console.log(jsonData);