# ProdSafe

# Intelligent Barcode Scanner & Product Safety Checker

This is a Flask-based web application that allows users to:
1. Register and maintain their profile (including allergies and health conditions).
2. Log in using their mobile number.
3. Upload an image containing a barcode.
4. Decode the barcode, fetch product information from [OpenFoodFacts](https://world.openfoodfacts.org/), and check whether the product is safe based on user-defined allergies and health conditions.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack and Requirements](#tech-stack-and-requirements)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Usage](#usage)
8. [Project Structure](#project-structure)
9. [License](#license)

---

## Overview

This project demonstrates:
- **User Management**: Register and log in with a mobile number and username.
- **Allergy/Health Condition Tracking**: Store multiple allergies and health conditions in a SQLite database.
- **Barcode Scanning**: Upload an image file (PNG/JPG/JPEG) and decode the barcode using [PyZbar](https://github.com/NaturalHistoryMuseum/pyzbar).
- **OpenFoodFacts Integration**: Fetch product details (title, brand, description, ingredients, etc.) via OpenFoodFacts API.
- **Safety Analysis**: Compare product ingredients to user allergies and health conditions, returning a simple "safe or not safe" message.

---

## Features

1. **User Registration**  
   - Collects username, name, mobile number, age, allergies, and health conditions.
   - Stores the information in a local SQLite database.

2. **User Login & Logout**  
   - Logs in via mobile number.
   - Utilizes Flask sessions to track the logged-in user.

3. **Profile Display & Update**  
   - Displays current user profile and allows updating allergies and health conditions.

4. **Barcode Scanning**  
   - Supports uploading an image file containing a barcode.
   - Decodes the barcode and fetches product info from OpenFoodFacts.

5. **Product Safety Check**  
   - Compares a product’s ingredients against the user’s allergies or health conditions.
   - Returns a safety report indicating any conflicts.

---

## Tech Stack and Requirements

- **Python 3.7+** (Recommended)
- **Flask** (Web framework)
- **Werkzeug** (Utilities for Flask, request handling)
- **Flask-SQLAlchemy** (ORM for database interactions)
- **PyZbar** (Barcode decoding)
- **OpenCV (cv2)** (Image processing library)
- **Requests** (HTTP requests for API calls)
- **python-dotenv** (For environment variables)
- **SQLite** (Local database for user info)

You can install these requirements with:

```bash
pip install flask flask_sqlalchemy pyzbar opencv-python requests python-dotenv
```

---

## Installation

1. **Clone or Download** this repository.

2. **Navigate** to the project folder:
   ```bash
   cd ProdSafe
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   > If you don’t have a `requirements.txt` file, install packages individually:
   > ```bash
   > pip install flask flask_sqlalchemy pyzbar opencv-python requests python-dotenv
   > ```

---

## Configuration

1. **Environment Variables**:  
   The app uses `python-dotenv` to load environment variables from a `.env` file. Create a `.env` file (if not present) with the following content:
   ```bash
   SECRET_KEY=your_secret_key_here
   PORT=9000
   ```
   - `SECRET_KEY` is used by Flask for session management. Replace `your_secret_key_here` with a secure, random string.
   - `PORT` (optional) can be used to customize the port the app runs on (defaults to 9000).

2. **Database**:  
   - This app uses a local SQLite database `users.db`. You do not need additional configuration if you’re okay with SQLite.  
   - By default, the database file `users.db` will be created in the project folder.

3. **Uploads Folder**:  
   - The project uses an `uploads` directory to temporarily store uploaded images.  
   - Make sure this folder is writable and present in the project root.

---

## Running the Application

1. **Initialize the Database** (if needed):
   ```bash
   python
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```
   Or simply run the app once; the code automatically creates the database tables on first run.

2. **Start the Flask Server**:
   ```bash
   python app.py
   ```
   The server will start on [http://0.0.0.0:9000](http://0.0.0.0:9000) (or the port specified in your `.env` file).

---

## Usage

1. **Register a New User**  
   - Go to `http://0.0.0.0:9000/register_page`
   - Fill in the form fields: username, name, mobile, age
   - Select or add any allergies or health conditions
   - Submit the form

2. **Login**  
   - Go to `http://0.0.0.0:9000/login_page`
   - Enter your mobile number
   - Submit

3. **View Profile**  
   - After logging in, click on “Go to Profile” or go to `http://0.0.0.0:9000/user_page`
   - View your current data (allergies, conditions, etc.)

4. **Update Profile**  
   - Click on “Update Profile” or go to `http://0.0.0.0:9000/update_profile_page`
   - Update your allergies and health conditions
   - Submit

5. **Scan Barcode**  
   - Go to `http://0.0.0.0:9000/scan_barcode`
   - Upload a PNG/JPG/JPEG image containing a barcode
   - The app will decode the barcode, fetch product details from OpenFoodFacts, and display a safety report.

6. **Logout**  
   - Hit the logout button (POST request to `/logout`), or go to the logout route to end your session.

---

## Project Structure

```
.
├── app.py                # Main Flask application
├── templates
│   ├── register.html
│   ├── login.html
│   ├── user.html
│   ├── update_profile.html
│   └── scan_barcode.html
├── static                # (Optional) static files (CSS, JS, etc.)
├── uploads               # Temporary folder for uploaded images
├── requirements.txt      # Required Python packages (if included)
├── .env                  # Environment variables (SECRET_KEY, etc.)
└── readme.md             # Documentation
```

---

## License

This project is provided for demonstration and educational purposes. You are free to use and modify it as needed.

---

**Enjoy building with the Intelligent Barcode Scanner & Product Safety Checker!**
