$(document).ready(function(){
var emailBox = $('#email')
var loginButton = $('#login-button')
var toggleLink = $('#register-toggle')
var toggleVar = $('#toggle')

function registrify() {
    emailBox.html("<input placeholder='Email' class='email-box' type='text' name='email' />")
    loginButton.attr('value', 'Register')
    toggleVar.attr('value', 'register')
    toggleLink.html('<a href=#>Login</a>')
}

function loginify() {
    emailBox.html('')
    loginButton.attr('value', 'Login')
    toggleVar.attr('value', 'login')
    toggleLink.html('<a href=#>Don\'t have an account? Sign up now</a>')
}

function togglify() {
    if(toggleVar.val() == 'login'){
        registrify()
    }
    else{
        loginify()
    }
}

toggleLink.on('click', function(){togglify()})


})
