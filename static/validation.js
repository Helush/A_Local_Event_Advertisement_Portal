

function validatePassword(password){
    if (password.length < 10) {
        return false;
    }

	if (!/[A-Z]/.test(password)) { //test for atleast one upper case
        return false;
    }
	if (!/[a-z]/.test(password)) { //test for atleast one lower case
        return false;
    }

	if (!/[0-9]/.test(password)) { //test for atleast one digit
        return false;
    }
	return true;

}

function validate(){
	var uname = document.forms["formRegistration"]["username"].value;
	var pwd = document.forms["formRegistration"]["password"].value;
	var pwd2 = document.forms["formRegistration"]["password2"].value;
	var fullname = document.forms["formRegistration"]["fullname"].value;
	var email = document.forms["formRegistration"]["email"].value;
	var errormessage = "";
	var rules = document.forms["formRegistration"]["rules"].checked;
	const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

	if (!rules) {
		errormessage += "You must accept the rules.<br/>";
	}

	if(uname == ""){
		errormessage += "The user name should be entered!<br/>";
	}

	if(pwd == ""){
		errormessage += "The password should be entered!<br/>";
	}

	if (pwd !== "" && !validatePassword(pwd)) {
		errormessage += "The password should include at least \n" +
			"one upper case letter, one lower case letter, and one digit and its length should be at least \n" +
			"ten.<br/>";
	}

	if(pwd2 == ""){
		errormessage += "The password should be entered again!<br/>";
	}

	if (pwd != pwd2){
		errormessage += "The passwords are not matching<br/>";
	}

	if(fullname == ""){
		errormessage += "The full name should be entered!<br/>";
	}

	if(email == ""){
		errormessage += "The email should be entered!<br/>";
	}

    if (!pattern.test(email)) {
    errormessage += "The email format is invalid!<br/>";
	}


	if(errormessage.length == 0)
		return true;
	else{
		document.getElementById("errorcode").innerHTML = errormessage;
		return false;
	}
}


function validateProfile(){
    var pwd = document.forms["profileUpdate"]["password"].value;
    var name = document.forms["profileUpdate"]["name"].value;
    var email = document.forms["profileUpdate"]["email"].value;
    var errormessage = "";
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if(pwd == ""){
       errormessage += "The password should be entered!<br/>";
    }

    if (pwd !== "" && !validatePassword(pwd)) {
		errormessage += "The password should include at least \n" +
			"one upper case letter, one lower case letter, and one digit and its length should be at least \n" +
			"ten.<br/>";    }



    if(name == ""){
       errormessage += "The name should be entered!<br/>";
    }

    if(email == ""){
       errormessage += "The email should be entered!<br/>";
    }

    if (!pattern.test(email)) {
       errormessage += "The email format is invalid!<br/>";
    }

    if(errormessage.length == 0)
       return true;
    else{
       document.getElementById("errorcode").innerHTML = errormessage;
       return false;
    }
}