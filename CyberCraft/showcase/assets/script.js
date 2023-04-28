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
    for (obj in result){
        const componentValues = JSON.parse(result[obj]);
        html += "<p style='white-space: nowrap;'>" + "<b>" + componentValues[0].type + "</b>" + ": " + "<br>" + 
        "Nom:  " + componentValues[0].name + "<br>" + 
        "Meilleur prix:  " + "<a href='"+ componentValues[0].lowest_supplier_url + "'>"+componentValues[0].lowest_supplier_url+"</a>" + "</p>";
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