from flask import Blueprint, render_template

main = Blueprint('main', __name__)

# Register
@main.route('/register')
def register_page():
    return render_template('register.html')

# Login
@main.route('/login')
def login_page():
    return render_template('login.html')

# Home do usuário normal
@main.route('/home')
def home():
    return render_template('home.html')
