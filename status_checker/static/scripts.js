/* Uncheck all of the checkboxes beside visible books */
function unselectBooks(){
    var rows = document.getElementsByTagName('input');
    for (var i = 0; i < rows.length; i++){
        if (rows[i].name=="check"){
            rows[i].checked = false;
        }
    }
}
