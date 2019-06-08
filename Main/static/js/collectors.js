let userURL = "";

function getAPIInfo() {
    // TODO: Add URL Prompt
    console.log("Getting user API Key");
    let token = window.prompt("Insert API Token Below!", "example: 1234567910");
    if (token) {
        console.log("Testing token");
        $.ajax({
            url: "{% url 'CanvasWrapper:test-token' %}",
            method: "GET",
            dataType: "json",
            data: {"token": token},
            success: function (results) {
                console.log("LOGGING IN......");
                window.location.replace("http://127.0.0.1:8000/courseview")
            },
            error: function (error) {
                console.log(error);
            }
        })
    }
    else {
        console.log("No token was provided, exiting!");
    }
}

function test(){
    console.log("I got here");
    // $.ajax({
    //     url: "http://127.0.0.1:5000/test",
    //     method: "GET",
    //     success: function(results){
    //         console.log(results)
    //     },
    //     error: function(results) {
    //         console.log(results);
    //     }
    // });
}

test();

