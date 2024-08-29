
function authenticate_email(){
    console.log("Authenticating email!");
    window.location.href = "/auth/google/email/login";
}

function authenticate_spreadsheet(){
    console.log("Authenticating Spreadsheet!");
    window.location.href = "/auth/google/spreadsheet/login"
}

function economic_calendar(){
    window.location.href = "/economic_calendar"
}