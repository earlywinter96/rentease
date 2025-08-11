# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm
from app.utils import generate_otp, send_email_smtp
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Register new user, send OTP to email."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        # Create new user
        user = User(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)

        # Generate OTP
        otp_code = generate_otp()
        user.set_otp(otp_code)

        db.session.add(user)
        db.session.commit()

        # Send OTP to email
        try:
            html_body = f"<h3>Your OTP Code</h3><p><b>{otp_code}</b></p><p>This code is valid for 5 minutes.</p>"
            send_email_smtp("Your OTP Code", user.email, html_body)
            flash("OTP sent to your email. Please verify.", "info")
        except Exception as e:
            flash(f"Failed to send OTP email: {str(e)}", "danger")

        return redirect(url_for("auth.verify_otp", email=user.email))

    return render_template("auth/register.html", form=form)


@bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    email = request.args.get("email")
    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Invalid verification link.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        entered_otp = request.form.get("otp")

        if (
            user.otp_code
            and entered_otp == user.otp_code
            and datetime.utcnow() < user.otp_expiry
        ):
            # ✅ Mark user as verified & activate
            user.otp_code = None
            user.otp_expiry = None
            user.is_active = True
            db.session.commit()

            # ✅ Log the user in only after OTP passes
            login_user(user, remember=True)

            flash("OTP verified successfully!", "success")

            # Redirect based on role
            if user.role == "admin":
                return redirect(url_for("facility.facility_approvals"))
            else:
                return redirect(url_for("main.dashboard"))

        flash("Invalid or expired OTP. Please try again.", "danger")

    return render_template("auth/verify_otp.html", email=email)



@bp.route("/resend-otp")
def resend_otp():
    """Resend OTP to the user."""
    email = request.args.get("email")
    if not email:
        flash("Email is required to resend OTP.", "danger")
        return redirect(url_for("auth.register"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.register"))

    # Generate new OTP
    otp_code = generate_otp()
    user.set_otp(otp_code)
    db.session.commit()

    try:
        html_body = f"<h3>Your New OTP Code</h3><p><b>{otp_code}</b></p><p>This code is valid for 5 minutes.</p>"
        send_email_smtp("Your New OTP Code", user.email, html_body)
        flash("A new OTP has been sent to your email.", "info")
    except Exception as e:
        flash(f"Failed to send OTP email: {str(e)}", "danger")

    return redirect(url_for("auth.verify_otp", email=email))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        # Already logged in, send to correct page
        if current_user.role == "admin":
            return redirect(url_for("facility.facility_approvals"))
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            if user.role == "admin":
                # ✅ Directly log in admin, skip OTP
                login_user(user, remember=True)
                flash("Welcome back, admin!", "success")
                return redirect(url_for("facility.facility_approvals"))
            else:
                # Normal user — OTP flow
                otp_code = generate_otp()
                user.set_otp(otp_code)
                db.session.commit()
                try:
                    html_body = f"<h3>Your OTP Code</h3><p><b>{otp_code}</b></p><p>This code is valid for 5 minutes.</p>"
                    send_email_smtp("Your OTP Code", user.email, html_body)
                    flash("OTP sent to your email. Please verify.", "info")
                except Exception as e:
                    flash(f"Failed to send OTP email: {str(e)}", "danger")
                return redirect(url_for("auth.verify_otp", email=user.email))

        flash("Invalid email or password", "danger")

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    """Log out current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/profile")
@login_required
def profile():
    """User profile page."""
    return render_template("auth/profile.html", user=current_user)

@bp.route("/manage-users")
@login_required
def manage_users():
    if current_user.role != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("main.dashboard"))

    users = User.query.all()
    return render_template("auth/manage_users.html", users=users)
