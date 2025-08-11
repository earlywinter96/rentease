from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from .models import User

class RegistrationForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(message="Please enter your name.")]
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Please enter your email address."),
            Email(message="Enter a valid email address.")
        ]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Please enter a password.")]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo("password", message="Passwords must match.")
        ]
    )
    role = SelectField(
        "Role",
        choices=[
            ("user", "Customer"),
            ("owner", "Facility Owner")
        ],
        validators=[DataRequired(message="Please select a role.")]
    )
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        # Check if email already exists in the database
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already in use. Please choose a different one.")

    
from wtforms import BooleanField

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")  # ✅ Add this line
    submit = SubmitField("Login")
