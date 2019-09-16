setupItems = [
    {
        "item": $("#terms-and-conditions"),
        "can-click": true,
    },
    {
        "item": $("#account-creation"),
        "can-click": false,
    },
    {
        "item": $("#account-settings"),
        "can-click": false,
    },
    {
        "item": $("#canvas-integration"),
        "can-click": false
    }
];


function nextSetup(current) {
    console.log(current);
    // setupItems[current]["item"].hide();
    // setupItems[current + 1]["item"].show();
    $("#" + setupItems[current]["item"].attr("id") + "-trigger").removeClass("current-setup-item");
    $("#" + setupItems[current + 1]["item"].attr("id") + "-trigger").addClass("current-setup-item");
    setupItems[current]["item"].fadeOut(200);
    setTimeout(function() {
        $("#placeholder").hide();
        setupItems[current + 1]["item"].slideDown(500, () => {
        });
    }, 190);

}

function onAgree() {
    nextSetup(0);
}

function onSubmitProfile() {
    attemptAccountRegister();
    return false;
}

function onSubmitSettings() {
    window.localStorage.setItem("autoencoder-iterations", $("#autoencoder-iterations").val());
    window.localStorage.setItem("save_data", $("#save-data").val());
    nextSetup(2);
    return false;
}


$(document).ready(function() {
    // Password variable decelerations
    let confirm_password = $("#confirm-password-input");
    let password = $("#password-input");


    function passwordFieldValidation(e) {
        if (confirm_password.val() !== "" && password.val() !== "") {
            if (confirm_password.val() + e.key !== password.val() + e.key) {
                $("#confirm-password-warning").show();
                $("#password-warning").show();
                password.addClass("is-danger");
                confirm_password.addClass("is-danger");
                $("#submit-profile-info").attr("disabled", true);
            } else {
                $("#confirm-password-warning").hide();
                $("#password-warning").hide();
                password.removeClass("is-danger");
                confirm_password.removeClass("is-danger");
                $("#submit-profile-info").attr("disabled", false);
            }
        }
    }

    confirm_password.on("keydown", passwordFieldValidation);
    password.on("keydown", passwordFieldValidation);

    // $(".setup-wizard-trigger").on("click", (e) => {
    //     $(".current-setup-item").each((_, elt) => {
    //         elt.className = elt.className.replace("current-setup-item", "");
    //     });
    //
    //     e.target.className += " current-setup-item";
    //     let targetID = e.target.id.replace("-trigger", "");
    //     let target = $("#" + targetID);
    //     if (lastSetupItem !== undefined) {
    //         lastSetupItem.fadeOut(200);
    //         setTimeout(function() {
    //             $("#placeholder").hide();
    //             target.slideDown(500, () => {
    //             });
    //         }, 190);
    //     }
    //     lastSetupItem = target;
    // });


    $("#canvas-modal-background").on("click", (e) => {
        e.target.parentNode.className = "modal";
        document.getElementById("blurrable").style.filter = "none";
    });

    $(".animated-first").each((index, element) => {
        $(element).slideDown(750);
    });
    $(".animated-left-to-right").each((index, element) => {
        $(element).show("slide", {direction: "left"}, 1000);
    });
    setTimeout( () => {
        $("#animated-second").slideDown(750, () => {
            $(".animated").each((index, element) => {
                $(element).show("slide", {direction: "left"}, 1000);
            });
        });
    }, 750);
});


/**
 * This function logs a user in via Canvas' OAuth2 implementation see Main/views.py for more information
 * @returns nothing
 */
function showURLInput() {
    document.getElementById("blurrable").style.filter = "blur(15px)";
    document.getElementById("canvas-url").className += " is-active";
    $("#canvas-modal-content").hide();
    // $("#canvas-modal-content").show();
    $("#canvas-modal-content").slideDown(500);
    document.getElementById("canvas-url-input").style.display = "none";
    let input = $("#canvas-url-input");
    input.slideDown(500);
    input.select();
}