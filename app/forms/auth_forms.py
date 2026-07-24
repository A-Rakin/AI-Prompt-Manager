from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

# ==============================================================================
# PromptForge - Authentication Forms (WTForms)
# ==============================================================================
# WTForms handles form generation, data extraction, and server-side validation.
#
# Key Concepts Explained:
# 1. Server-Side Validation: Checking user input on the server before database queries.
#    Client-side HTML5 validation can be bypassed by malicious users, so server-side check is required.
# 2. CSRF (Cross-Site Request Forgery) Token: Hidden input field embedded automatically by Flask-WTF
#    to verify that form requests originate from our actual application pages.
# 3. Custom Validators: Functions named `validate_<fieldname>` automatically executed by WTForms
#    to check business logic rules (e.g. checking if a username or email is already taken).
# ==============================================================================

class LoginForm(FlaskForm):
    """
    Form for user login supporting authentication via either Username or Email.
    """
    email_or_username = StringField(
        'Username or Email',
        validators=[DataRequired(message="Please enter your username or email address.")],
        render_kw={"placeholder": "e.g. alex_promptcraft or alex@example.com", "class": "form-control"}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message="Password is required.")],
        render_kw={"placeholder": "••••••••", "class": "form-control"}
    )
    remember_me = BooleanField('Keep me logged in for 7 days')
    submit = SubmitField('Sign In to PromptForge', render_kw={"class": "btn btn-primary w-100"})


class RegisterForm(FlaskForm):
    """
    Form for new user registration with unique username and email checks.
    """
    username = StringField(
        'Username',
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=30, message="Username must be between 3 and 30 characters.")
        ],
        render_kw={"placeholder": "Choose a unique username", "class": "form-control"}
    )
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message="Email address is required."),
            Email(message="Please enter a valid email address.")
        ],
        render_kw={"placeholder": "you@example.com", "class": "form-control"}
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required."),
            Length(min=6, message="Password must be at least 6 characters long.")
        ],
        render_kw={"placeholder": "Create a strong password", "class": "form-control"}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo('password', message="Passwords must match.")
        ],
        render_kw={"placeholder": "Repeat your password", "class": "form-control"}
    )
    submit = SubmitField('Create Account', render_kw={"class": "btn btn-primary w-100"})

    def validate_username(self, username):
        """Custom validator checking if username is already registered."""
        user = User.query.filter_by(username=username.data.strip()).first()
        if user:
            raise ValidationError("This username is already taken. Please choose another one.")

    def validate_email(self, email):
        """Custom validator checking if email is already registered."""
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError("An account with this email address already exists.")


class ProfileForm(FlaskForm):
    """
    Form for updating account profile information (Bio and Avatar).
    """
    username = StringField(
        'Username',
        render_kw={"readonly": True, "class": "form-control bg-dark-subtle"}
    )
    email = StringField(
        'Email Address',
        render_kw={"readonly": True, "class": "form-control bg-dark-subtle"}
    )
    bio = TextAreaField(
        'Bio / Short Description',
        validators=[Length(max=500, message="Bio cannot exceed 500 characters.")],
        render_kw={"placeholder": "Tell the community about your AI prompt engineering background...", "rows": 4, "class": "form-control"}
    )
    submit = SubmitField('Save Profile Changes', render_kw={"class": "btn btn-primary"})


class ChangePasswordForm(FlaskForm):
    """
    Form for securely updating account password.
    """
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired(message="Current password is required.")],
        render_kw={"placeholder": "••••••••", "class": "form-control"}
    )
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message="New password is required."),
            Length(min=6, message="New password must be at least 6 characters long.")
        ],
        render_kw={"placeholder": "Enter new password", "class": "form-control"}
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message="Please confirm your new password."),
            EqualTo('new_password', message="New passwords must match.")
        ],
        render_kw={"placeholder": "Repeat new password", "class": "form-control"}
    )
    submit = SubmitField('Update Password', render_kw={"class": "btn btn-warning"})
