const patientBedList = new Set([
  'A1', 'A2', 'A3', 'A5', 'A6', 'A7', 'A8', 'A9', 
  'B1', 'B2', 'B3', 'B5', 'B6', 'B7', 'B8', 'B9', 
  'C1', 'C2', 'C3', 'C5', 'C6', 'C7', 'C8', 'C9', 
  'D1', 'D2', 'D3', 'D5', 'D6', 'D7', 'D8', 'D9', 
  'E1', 'E2', 'E3', 'E5', 'E6', 'E7', 'E8', 'E9', 
  'I1', 'I2', 'I3', 'I5', 'I6', 'I7', 'I8', 'I9'])

$(document).ready(function () {
  const nurseId = document.getElementById("nurseId").value;
  const existedList = document.getElementById("existedList");
  const notInList = document.getElementById("notInList");
  if (!sessionStorage.getItem(nurseId)) {
    sessionStorage.setItem(nurseId, JSON.stringify(new Array()));
  }
  let tmp = new Set(JSON.parse(sessionStorage.getItem(nurseId)));
  tmp.forEach((val) => {
    const rightLi = document.createElement("li");
    rightLi.textContent = val;
    rightLi.classList.add("list-cell-format");
    existedList.appendChild(rightLi);
  });
  patientBedList.forEach((val) => {
    if(!tmp.has(val)){
      const leftLi = document.createElement("li");
      leftLi.textContent = val;
      leftLi.classList.add("list-cell-format");
      notInList.appendChild(leftLi);
    }
  });
  existedList.addEventListener("click", (e) => {
    const nurseId = document.getElementById("nurseId").value;
    let setTmp = new Set(JSON.parse(sessionStorage.getItem(nurseId)));
    existedList.removeChild(e.target);
    notInList.appendChild(e.target);
    setTmp.delete(e.target.innerText);
    sessionStorage.setItem(nurseId, JSON.stringify(Array.from(setTmp)));
  });
  notInList.addEventListener("click", (e) => {
    const nurseId = document.getElementById("nurseId").value;
    if (!sessionStorage.getItem(nurseId)) {
      sessionStorage.setItem(nurseId, JSON.stringify(new Array()));
    }
    let setTmp = new Set(JSON.parse(sessionStorage.getItem(nurseId)));
    notInList.removeChild(e.target);
    existedList.appendChild(e.target);
    setTmp.add(e.target.innerText);
    sessionStorage.setItem(nurseId, JSON.stringify(Array.from(setTmp)));
  });
});

function AdjustPage(){
  const nurseId = document.getElementById("nurseId").value;
  const existedList = document.getElementById("existedList");
  const notInList = document.getElementById("notInList");
  removeAllNodes(existedList);
  removeAllNodes(notInList);
  let tmp = new Set(JSON.parse(sessionStorage.getItem(nurseId)));
  console.log(tmp);
  tmp.forEach((val) => {
    const rightLi = document.createElement("li");
    rightLi.textContent = val;
    rightLi.classList.add("list-cell-format");
    existedList.appendChild(rightLi);
  })
  patientBedList.forEach((val) => {
    if(!tmp.has(val)){
      const leftLi = document.createElement("li");
      leftLi.textContent = val;
      leftLi.classList.add("list-cell-format");
      notInList.appendChild(leftLi);
    }
  })
}

function SearchPage(){
  location.href = location_path + "Y";
}

function removeAllNodes(tag){
  while(tag.firstChild){
    tag.removeChild(tag.firstChild);
  }
  return;
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
