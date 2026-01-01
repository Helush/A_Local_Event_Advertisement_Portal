

function countDigits(pwd){
	var i;
	var counter = 0;
	for(i=0; i<pwd.length; i++){
		if("0123456789".search(pwd[i])!= -1)
			counter++;
	}
	return counter;
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

	if (pwd !== "" && countDigits(pwd) < 2) {
		errormessage += "The password should include at least two digits<br/>";
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

	if(pwd.length < 5){
		errormessage += "The length of the password should be at least 5<br/>";
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

    if (pwd !== "" && countDigits(pwd) < 2) {
       errormessage += "The password should include at least two digits<br/>";
    }

    if(pwd.length < 5){
       errormessage += "The length of the password should be at least 5<br/>";
    }

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