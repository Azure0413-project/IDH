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
function openCity(evt, cityName) {
    // Declare all variables
    var i, tabcontent, tablinks;

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
