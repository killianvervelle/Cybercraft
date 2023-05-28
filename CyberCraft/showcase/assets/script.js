// Global variable(s)
let debug = false;      // set this to true to activate logs in the console
let root_url = "";     // the root url of the showcase


// Tab switching function from output to CURL command
let jQuery = $(document).ready(function () {
    // Init materialize tab
    M.Tabs.init($('#tabs'), {});
    // get the root url
    const parts = window.location.href.split("/");
    root_url = parts[0] + "/";
    for (let i = 1; i < parts.length - 1; i++) {
        if (parts[i].length !== 0) {
            root_url += "/" + parts[i];
        }
    }
    if (debug) console.log("root_url: " + root_url);
});

function reset(){
    document.getElementById('slider').value ='';
    updateValue('sliderValue', '5000')
}

function execute(){
    // this is the path to the API route
    let url = root_url + "/" + "build";
    let response_array = [];
    let budget = document.getElementById('sliderValue').textContent
    let cpu_brand = document.getElementById('cpu_brand').value
    let gpu_brand = document.getElementById('gpu_brand').value
    let gpu_mem = document.getElementById('gpu_mem').value
    let ram_brand = document.getElementById('ram_brand').value
    let ram_sticks = document.getElementById('ram_sticks').value
    let ram_capa = document.getElementById('ram_capa').value
    let ssd_brand = document.getElementById('ssd_brand').value
    let ssd_capa = document.getElementById('ssd_capa').value
    let mother_brand = document.getElementById('mother_brand').value  

    // build the request
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", url);
    xhttp.setRequestHeader("Content-Type","application/json");
    xhttp.responseType = "json";
    xhttp.onload = () => {
    const htmlOutput = composeOutput(xhttp.response);
    $("#outputText").html(htmlOutput);
    };

    xhttp.onreadystatechange = function () {
        if (xhttp.readyState === 4 && xhttp.status !== 200) {
            alert("Process failed")
        }
    };

    let param = {};  // this will hold the parameters passed to the API
    param.budget = budget
    param.cpu_brand = cpu_brand
    param.gpu_brand = gpu_brand
    param.gpu_mem = gpu_mem
    param.ram_brand = ram_brand
    param.ram_sticks = ram_sticks
    param.ram_capa = ram_capa
    param.ssd_brand = ssd_brand
    param.ssd_capa = ssd_capa
    param.mother_brand = mother_brand
    const data = JSON.stringify(param);
    console.log("data sent: " + data)
    xhttp.send(data);

    let command = "curl "
    + "-H \"Content-Type: application/json\" "
    + "-H \"accept: application/json\" "
    + "-d '" + data
    + "' -X POST " + url;

    $("#id-curl").text(command);
}

function composeOutput(result) {
    // Log the values
    let html = "<ol>";
    html += "</ol>";
    if (result.length == 1) {
        alert(result)
    }
    else {
    for (obj in result){
        const componentValues = JSON.parse(result[obj]);
        html += "<p style='white-space: nowrap;'>" + "<b>" + componentValues[0].type + "</b>" + ": " + "<br>" + 
        "Nom:  " + componentValues[0].name + "<br>" + 
        "Meilleur prix:  " + "<a href='"+ componentValues[0].lowest_supplier_url + "'>"+componentValues[0].lowest_supplier_url+"</a>" + "</p>";
        }
    }
    return html;
    }

function copyToClipboard(){
    /* Get the text field */
    var copyText = document.getElementById("id-curl").innerHTML;
    /* Copy the text inside the text field */
    navigator.clipboard.writeText(copyText);
    M.toast({html: 'Curl command copied to clipboard'});
}

function updateValue(sliderId, newValue) {
    if (sliderId == "slider1Value"){
        if (newValue ==1) {
            document.getElementById(sliderId).textContent = "1080p";
        }
        else if (newValue ==2) {
            document.getElementById(sliderId).textContent = "1440p";
        }
        else if (newValue ==3) {
            document.getElementById(sliderId).textContent = "2160p";
        }
    }
    else {
    document.getElementById(sliderId).textContent = newValue;
    return newValue
    }
}

// // Depending on the tab selected, the dropdown list is updated
// function dynamicdropdown(tab){
//     let trans_fields = ['t_id', 't_date', 't_price'];
//     let brok_fields = ['broker_id', 'broker_type', 'broker_firstname', 
//     'broker_lastname', 'broker_acc_id', 'broker_net_id', 'broker_acc_name', 
//     'broker_acc_lat', 'broker_acc_lng'];
//     let obj_fields = ['obj_id', 'obj_add_date', 'obj_main_category', 
//     'obj_category', 'obj_deal', 'obj_price', 'obj_postalcode', 'obj_city', 
//     'obj_rooms', 'obj_canton', 'obj_grade', 'obj_lat', 'obj_lng'];
//     var select = document.getElementById("genDropdown");
//     var options = (tab == "transactions") ? trans_fields : ( (tab == "brokers") ? brok_fields : obj_fields );
//     if (select) {
//         while(select.firstElementChild) {
//             select.firstElementChild.remove();
//         }
//     };
//     for(var i = 0; i < options.length; i++) {
//         var opt = options[i];
//         var el = document.createElement("option");
//         el.textContent = opt;
//         el.value = opt;
//         select.appendChild(el);
//     }
// }