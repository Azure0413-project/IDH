function TimeAppend(p_id){
    console.log(p_id);
    let idh_time_list = document.getElementById(`idh-time-${p_id}`);
    let idh_time = document.getElementById(`idh-select-${p_id}`).value;
    // idh_time_list.value = idh_time_list.value + "test";
    // console.log(`time list: ${idh_time_list}, time: ${idh_time}`);
    if(idh_time_list.value.length != 0){
        idh_time_list.value += ",";
    }
    // idh_time_list += "test";
    idh_time_list.value += `${idh_time.replace(":", "")}`;
    // console.log(`time list: ${idh_time_list}, time: ${idh_time}`);
    return;
}