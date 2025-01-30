import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

# 1. Barcode Reading and OpenFoodFacts Logic -------------------------



def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_barcode(image_path):
    """
    Reads a barcode from a local image file and returns decoded data.
    Returns a list of tuples (barcode_data, barcode_type) if found,
    or None if no barcodes are detected.
    """
    img = cv2.imread(image_path)
    barcodes = decode(img)

    if not barcodes:
        return None

    results = []
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        results.append((barcode_data, barcode_type))
    return results

def get_product_from_openfoodfacts(barcode):
    """
    Fetches product details using the OpenFoodFacts API (Free).
    Returns a dictionary with product information if found, else None.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "product" in data and data["product"]:
            product = data["product"]
            title = product.get("product_name", "No product title found")
            brand = product.get("brands", "Unknown brand")
            description = product.get("generic_name", "No description available")
            ingredients = product.get("ingredients_text", "") or ""  # ensure string
            category = product.get("categories", "Unknown category")
            return {
                "barcode": barcode,
                "title": title,
                "brand": brand,
                "description": description,
                "ingredients": ingredients,
                "category": category
            }
    return None

def check_product_safety(product_info, user):
    """
    Checks product's ingredients against user's allergies or health conditions.
    Returns a dictionary with analysis results.
    - product_info: dict from OpenFoodFacts (title, ingredients, etc.)
    - user: a User object from the DB
    """
    if not product_info or not user:
        return {"status": "error", "message": "Invalid product or user."}

    # Convert user allergies and health conditions into lists
    user_allergies = [a.strip().lower() for a in user.allergies.split(",") if a.strip()]
    user_conditions = [h.strip().lower() for h in user.health_conditions.split(",") if h.strip()]

    # Convert product ingredients to lower for naive checking
    ingredients_lower = product_info["ingredients"].lower()

    # Find which allergies are present in ingredients
    conflicting_allergies = []
    for allergy in user_allergies:
        if allergy and allergy in ingredients_lower:
            conflicting_allergies.append(allergy)

    # In a more advanced approach, health conditions could lead to specific 
    # checks (like sugar or sodium content for Diabetes/Hypertension).
    # For demonstration, we do a naive check if condition name appears in the ingredients text.
    conflicting_conditions = []
    for condition in user_conditions:
        # This is a naive example. Real logic might be more sophisticated.
        if condition and condition in ingredients_lower:
            conflicting_conditions.append(condition)

    # Decide if product is "safe" or "not safe"
    is_safe = (not conflicting_allergies) and (not conflicting_conditions)

    return {
        "is_safe": is_safe,
        "conflicting_allergies": conflicting_allergies,
        "conflicting_conditions": conflicting_conditions,
        "product_name": product_info["title"],
        "product_brand": product_info["brand"],
        "product_ingredients": product_info["ingredients"]
    }

# 2. Flask + SQLAlchemy Setup ----------------------------------------

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "simplesecretkey")

db = SQLAlchemy(app)

# Suggested values
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



UPLOAD_FOLDER = 'uploads'  # Directory to temporarily store uploaded files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Allowed file types
# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)  # <-- ADDED
    name = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    allergies = db.Column(db.String(255), default="")
    health_conditions = db.Column(db.String(255), default="")

with app.app_context():
    db.create_all()

# 3. User Registration / Login ---------------------------------------

@app.route('/register_page', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        try:
            # Capture the form fields, including username:
            username = request.form.get('username')  # <-- ADDED
            name = request.form.get('name')
            mobile = request.form.get('mobile')
            age = request.form.get('age')

            # Adjust the validation to include 'username':
            if not all([username, name, mobile, age]):
                flash("Username, Name, Mobile, and Age are required fields.", "danger")
                return redirect(url_for('register_page'))

            # Check if username is already taken:
            if User.query.filter_by(username=username).first():
                flash("Username already exists. Please choose a different one.", "warning")
                return redirect(url_for('register_page'))

            # Handle allergies and health conditions as before:
            allergies = request.form.getlist('allergies')
            custom_allergy = request.form.get('custom_allergy')
            health_conditions = request.form.getlist('health_conditions')
            custom_health = request.form.get('custom_health')

            if custom_allergy:
                allergies.append(custom_allergy)
            if custom_health:
                health_conditions.append(custom_health)

            # Check if mobile is already registered:
            if User.query.filter_by(mobile=mobile).first():
                flash("Mobile number already exists. Try logging in instead.", "warning")
                return redirect(url_for('register_page'))

            # Create new user with username included:
            new_user = User(
                username=username,             # <-- ADDED
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
            flash("Mobile/Username already exists. Please try a different one.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", "danger")

    # If GET or registration fails, just render the form:
    return render_template(
        'register.html', 
        suggested_allergies=SUGGESTED_ALLERGIES, 
        suggested_health=SUGGESTED_HEALTH_CONDITIONS
    )

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

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('mobile', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login_page'))

# 4. Display & Update User Info --------------------------------------

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

        return render_template(
            'update_profile.html',
            user=user,
            suggested_allergies=SUGGESTED_ALLERGIES,
            suggested_health=SUGGESTED_HEALTH_CONDITIONS
        )
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")
        return redirect(url_for('login_page'))

# 5. Intelligent Suggester Routes ------------------------------------
#    Example 1: Using a local image path for demonstration
@app.route('/scan_barcode', methods=['GET', 'POST'])
def scan_barcode():
    mobile = session.get('mobile')
    if not mobile:
        flash("Unauthorized access. Please log in.", "danger")
        return redirect(url_for('login_page'))

    user = User.query.filter_by(mobile=mobile).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        if 'image_file' not in request.files:
            flash("No file part in the request.", "danger")
            return redirect(request.url)

        file = request.files['image_file']

        if file.filename == '':
            flash("No selected file.", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)  # Save the file temporarily

            # Process the barcode
            results = read_barcode(filepath)

            if not results:
                flash("No barcode detected in the uploaded image.", "danger")
                os.remove(filepath)  # Clean up the temporary file
                return redirect(request.url)

            barcode_data, barcode_type = results[0]
            product_info = get_product_from_openfoodfacts(barcode_data)

            os.remove(filepath)  # Clean up the temporary file

            if not product_info:
                flash(f"No product found for barcode {barcode_data}.", "warning")
                return redirect(request.url)

            safety_report = check_product_safety(product_info, user)

            return render_template('scan_barcode.html', 
                                   barcode=barcode_data, 
                                   barcode_type=barcode_type, 
                                   product=product_info, 
                                   safety_report=safety_report)

        else:
            flash("Unsupported file type. Please upload a PNG, JPG, or JPEG image.", "danger")
            return redirect(request.url)

    return render_template('scan_barcode.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)