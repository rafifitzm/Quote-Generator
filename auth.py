from extensions import db, login_manager
from models import User
from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = generate_password_hash(password, method='sha256')

        # Store the hashed password in the database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))  # Runs if POST
    return render_template('register.html')  # Runs if GET

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by the provided username
        user = User.query.filter_by(username=username).first()

        # Verify the password
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))  # Runs if POST AND user
        return render_template('login.html', error="Invalid credentials")  # Runs if POST AND NOT user
    return render_template('login.html')  # Runs if GET

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
