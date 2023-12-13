$(document).ready(function () {
  const nurseId = document.getElementById("nurseId").value;
  const existedList = document.getElementById("existedList");
  const notInList = document.getElementById("notInList");
  if (!sessionStorage.getItem(nurseId)) {
    sessionStorage.setItem(nurseId, JSON.stringify(new Array()));
  }
  let tmp = new Set(JSON.parse(sessionStorage.getItem(nurseId)));
  for (let i = 0; i < tmp.size; ++i) {
    const newLI = document.createElement("li");
    newLI.textContent = tmp[i];
    existedList.appendChild(newLI);
  }
  existedList.addEventListener("click", (e) => {
    let setTmp = new Set(JSON.parse(sessionStorage.getItem(nurseId)));
    existedList.removeChild(e.target);
    notInList.appendChild(e.target);
    setTmp.delete(e.target.innerText);
    sessionStorage.setItem(nurseId, JSON.stringify(Array.from(setTmp)));
  });
  notInList.addEventListener("click", (e) => {
    // console.log(e);
    let setTmp = new Set(JSON.parse(sessionStorage.getItem(nurseId)));
    notInList.removeChild(e.target);
    existedList.appendChild(e.target);
    setTmp.add(e.target.innerText);
    sessionStorage.setItem(nurseId, JSON.stringify(Array.from(setTmp)));
  });
});

function liClickEvent(e) {
  console.log(e);
}
