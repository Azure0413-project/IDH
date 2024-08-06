function TimeAppend(p_id){
    console.log(p_id);
    let idh_time_list = document.getElementById(`idh-time-${p_id}`);
    let idh_time = document.getElementById(`idh-select-${p_id}`).value;
    current_time = idh_time.replace(":", "");
    current_time_set = new Set(idh_time_list.value.split(","));
    if(current_time_set.has(current_time)){
        current_time_set.delete(current_time);
        idh_time_list.value = [...current_time_set].join(",");
    } else {
        if(idh_time_list.value.length != 0){
            idh_time_list.value += ",";
        } 
        idh_time_list.value += `${idh_time.replace(":", "")}`;
    }
    return;
}