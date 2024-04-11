
// Display file content. When clicked, read the file content and display in the textarea
const reader = new FileReader();
const jsonFormatter = new JSONFormatter("json-thingdescription", false);
const $registerBtn = $("#submit");

reader.onload = function (file) {
    let fileContent = file.target.result;
    if (!jsonFormatter.setJSONString(fileContent)) {
        show_prompt("Input is not in JSON format.");
    }
};

/* 
* change the name display in the file upload dialog accordingly
*/
$('#customFile').change(function (e) {
    let files = e.target.files;
    if (files.length == 1) {
        reader.readAsText(files[0]);
        // change display filename
        $(".custom-file label").text(files[0].name);
    } else if (jsonFormatter.getJSONString() === null) {
        show_prompt('Please Choose One File.');
    }
});


// Submit button. send request to register API
$("#submit").click(function (e) {

    let text = jsonFormatter.getJSONString();
    if (text == null || text.trim().length == 0) {
        show_prompt("Please Filled All Input Fields", title = 'Alert');
        return;
    }

    // get form data, and check whether it's a valid json
    let td_json = null;
    try {
        td_json = { "td": JSON.parse(text.trim())};
    } catch (error) {
        show_prompt("Input is not in JSON format. Please try again");
        return;
    }
    // send out the register request
    lock_btn($registerBtn);
    added_msg = true;   // hide redundant thing added notification
    $.ajax({
        url: COMMAND_URL,
        type: "POST",
        data: JSON.stringify(td_json),
        contentType: "application/json",
        error: function (jqXHR, textStatus, errorThrown) {
            unlock_btn($registerBtn);
            let response = JSON.parse(jqXHR.responseText)
            if (response.error == "Double Check") {
                if(window.confirm(response.message)){
                    // function to call api to execute command
                    show_prompt("Command Executed Successfully!");
                }
            } else {
                show_prompt(response.message, "Deny");
            }
        },
        success: function (data, textStatus, jqXHR) {
            unlock_btn($registerBtn);
            show_prompt("Command Executed Successfully!");
        }
    });
});