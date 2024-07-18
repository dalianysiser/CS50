// Document is ready
$(document).ready(function() {

    // Validate Username
    $("#usercheck").hide();
    let usernameError = true;
    $("#username").keyup(function() {
        validateUsername();
    });
    var user = document.getElementById("username");
    user.onblur = function() {
        validateUsername();
    }

	    // Validate Password
		$("#passcheck").hide();
		let passwordError = true;
		$("#password").keyup(function() {
			validatePass();
		});

		// Validate Confirm Password
		$("#conpasscheck").hide();
		let confirmPasswordError = true;
		$("#confirmation").keyup(function() {
			validateConfirmPassword();
		});

    function validateUsername() {
        let usernameValue = $("#username").val();
        if (usernameValue.length == "") {
            $("#usercheck").show();
            usernameError = false;
            return false;
        } else if (usernameValue.length < 3 || usernameValue.length > 10) {
            $("#usercheck").show();
            $("#usercheck").html("length of username must be between 3 and 10");
            usernameError = false;
            return false;
        } else {
			usernameError = true;
            $("#usercheck").hide();
        }
    }


    function validatePass() {
        var field_val = $('#password').val();
        let uppercase = /[A-Z]/g;
        let lowercase = /[a-z]/g;
        let digit = /[0-9]/g;
        let special_car = /[!@#$%^&.*()_]/g;
        if (field_val == '') {
			passwordError = false;
            $('#password_error').text('Password is requried');
            $('#password_error').css('color', 'crimson');
            $('#password').focus();
            return false;
        } else if (!field_val.match(uppercase)) {
			passwordError = false;
            $('#password_error').text('Please enter at least one capital letter.');
            $('#password_error').css('color', 'crimson');
            $('#password').focus();
            return false;
        } else if (!field_val.match(lowercase)) {
			passwordError = false;
            $('#password_error').text('Please enter at least one small letter.');
            $('#password_error').css('color', 'crimson');
            $('#password').focus();
            return false;
        } else if (!field_val.match(digit)) {
			passwordError = false;
            $('#password_error').text('Please enter at least one digit.');
            $('#password_error').css('color', 'crimson');
            $('#password').focus();
            return false;
        } else if (!field_val.match(special_car)) {
			passwordError = false;
            $('#password_error').text('Please enter at least one special character.');
            $('#password_error').css('color', 'crimson');
            $('#password').focus();
            return false;
        } else if (field_val.length < 8) {
			passwordError = false;
            $('#password_error').text('Please enter minimum eight character.');
            $('#password_error').css('color', 'crimson');
            $('#password').focus();
            return false;
        } else {
			passwordError = true;
            $('#password_error').text('');
        }
    }


    function validateConfirmPassword() {
        let confirmPasswordValue = $("#confirmation").val();
        let passwordValue = $("#password").val();
		if (passwordValue == '') {
			$("#conpasscheck").show();
            confirmPasswordError = false;
            return false;
		}
        if (passwordValue != confirmPasswordValue) {
            $("#conpasscheck").show();
            confirmPasswordError = false;
            return false;
        } else {
			confirmPasswordError = true;
            $("#conpasscheck").hide();
        }
    }

    // Submit button
    $("#submitbtn").click(function() {
        validateUsername();
        validatePass();
        validateConfirmPassword();
        if (
            usernameError == true &&
            passwordError == true &&
            confirmPasswordError == true
        ) {
			$('#form_data').submit();
			document.getElementById("form_data").submit();
            return true;
        } else {
            return false;
        }
    });
});
