from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "simplesecretkey")  # Needed for session management

# Initialize extensions
db = SQLAlchemy(app)

# Suggested values
# Updated suggested values with more comprehensive allergies and health conditions
SUGGESTED_ALLERGIES = [
    "Peanuts", "Dust", "Pollen", "Gluten", "Dairy", "Eggs", "Fish", "Shellfish",
    "Soy", "Wheat", "Tree Nuts", "Corn", "Sesame", "Mustard", "Sulfites",
    "Nightshades", "Legumes", "Citrus", "Bananas", "Chocolate", "Alcohol",
    "Histamine", "Salicylates", "Mushrooms", "Lactose"
]

SUGGESTED_HEALTH_CONDITIONS = [
    "Diabetes", "Hypertension", "Asthma", "Thyroid", "Celiac Disease",
    "Kidney Disease", "Gout", "Lactose Intolerance", "IBS", "Histamine Intolerance",
    "Alpha-gal Syndrome", "Hypersensitivity", "Oral Allergy Syndrome",
    "Shellfish Allergy", "Fish Allergy", "Gluten Sensitivity", "Insulin Resistance",
    "Autoimmune Diseases", "Heart Disease", "High Cholesterol"
]

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    allergies = db.Column(db.String(255), default="")
    health_conditions = db.Column(db.String(255), default="")

# Create tables
with app.app_context():
    db.create_all()

# User Registration (Web Page)
@app.route('/register_page', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            mobile = request.form.get('mobile')
            age = request.form.get('age')

            if not all([name, mobile, age]):
                flash("Name, Mobile, and Age are required fields.", "danger")
                return redirect(url_for('register_page'))

            allergies = request.form.getlist('allergies')
            custom_allergy = request.form.get('custom_allergy')
            health_conditions = request.form.getlist('health_conditions')
            custom_health = request.form.get('custom_health')

            if custom_allergy:
                allergies.append(custom_allergy)
            if custom_health:
                health_conditions.append(custom_health)

            if User.query.filter_by(mobile=mobile).first():
                flash("Mobile number already exists. Try logging in.", "warning")
                return redirect(url_for('register_page'))

            new_user = User(
                name=name,
                mobile=mobile,
                age=int(age),
                allergies=", ".join(allergies),
                health_conditions=", ".join(health_conditions)
            )

            db.session.add(new_user)
            db.session.commit()
            flash("User registered successfully!", "success")
            return redirect(url_for('login_page'))

        except IntegrityError:
            db.session.rollback()
            flash("Mobile number already exists. Please use a different one.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", "danger")

    return render_template('register.html', 
                           suggested_allergies=SUGGESTED_ALLERGIES, 
                           suggested_health=SUGGESTED_HEALTH_CONDITIONS)

# User Login (Web Page)
@app.route('/login_page', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        try:
            mobile = request.form.get('mobile')

            if not mobile:
                flash("Mobile number is required.", "danger")
                return redirect(url_for('login_page'))

            user = User.query.filter_by(mobile=mobile).first()
            if user:
                session['mobile'] = user.mobile
                flash("Logged in successfully!", "success")
                return redirect(url_for('get_user_page'))

            flash("User not found. Please register first.", "danger")
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", "danger")

    return render_template('login.html')

# User Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('mobile', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login_page'))

# Get User Info (Web Page - Protected)
@app.route('/user_page', methods=['GET'])
def get_user_page():
    try:
        mobile = session.get('mobile')
        if not mobile:
            flash("Unauthorized access. Please log in.", "danger")
            return redirect(url_for('login_page'))

        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('login_page'))

        return render_template('user.html', user=user)
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")
        return redirect(url_for('login_page'))

# **NEW: Update Profile Page (Separate)**
@app.route('/update_profile_page', methods=['GET', 'POST'])
def update_profile_page():
    try:
        mobile = session.get('mobile')
        if not mobile:
            flash("Unauthorized access. Please log in.", "danger")
            return redirect(url_for('login_page'))

        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('login_page'))

        if request.method == 'POST':
            allergies = request.form.getlist('allergies')
            custom_allergy = request.form.get('custom_allergy')
            health_conditions = request.form.getlist('health_conditions')
            custom_health = request.form.get('custom_health')

            if custom_allergy:
                allergies.append(custom_allergy)
            if custom_health:
                health_conditions.append(custom_health)

            user.allergies = ", ".join(allergies)
            user.health_conditions = ", ".join(health_conditions)
            db.session.commit()

            flash("Profile updated successfully!", "success")
            return redirect(url_for('update_profile_page'))

        return render_template('update_profile.html', user=user, 
                               suggested_allergies=SUGGESTED_ALLERGIES,
                               suggested_health=SUGGESTED_HEALTH_CONDITIONS)
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")
        return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)
