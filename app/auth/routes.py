from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.models import db, User
from app.forms.auth_forms import LoginForm, RegisterForm, ProfileForm, ChangePasswordForm
from app.utils.helpers import log_activity

# ==============================================================================
# PromptForge - Authentication Routes
# ==============================================================================
# Handles user registration, authentication, session termination, profile edits,
# and password security updates.
# ==============================================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Renders the login page and processes login credentials.
    Supports authenticating with either username or email address.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.email_or_username.data.strip()
        password = form.password.data

        # Query database for user matching either username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            # Log user into Flask-Login session
            login_user(user, remember=form.remember_me.data)
            
            # Log activity to timeline
            log_activity(user.id, 'login', 'Signed into PromptForge account')

            flash(f"Welcome back, {user.username}!", "success")
            
            # Redirect to originally requested URL if user was intercepted by login_required
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash("Invalid credentials. Please double-check your username/email and password.", "danger")

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Renders the user registration form and registers new accounts.
    Hashes passwords securely before saving to database.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        # Log new account creation
        log_activity(user.id, 'register', 'Created PromptForge account')

        # Automatically log in new user after registration
        login_user(user)
        flash("Registration successful! Welcome to your new PromptForge dashboard.", "success")
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Ends user session and redirects to login page.
    """
    user_id = current_user.id
    logout_user()
    log_activity(user_id, 'logout', 'Logged out of account')
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Allows users to update profile details (bio, avatar) and change account password.
    """
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if request.method == 'POST':
        if 'submit_profile' in request.form and profile_form.validate():
            current_user.bio = profile_form.bio.data.strip()
            db.session.commit()

            log_activity(current_user.id, 'profile_update', 'Updated profile bio')
            flash("Profile information updated successfully!", "success")
            return redirect(url_for('auth.profile'))

        elif 'submit_password' in request.form and password_form.validate():
            if not current_user.check_password(password_form.current_password.data):
                flash("Current password is incorrect.", "danger")
            else:
                current_user.set_password(password_form.new_password.data)
                db.session.commit()

                log_activity(current_user.id, 'password_change', 'Changed account password')
                flash("Password updated successfully!", "success")
                return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', profile_form=profile_form, password_form=password_form)
