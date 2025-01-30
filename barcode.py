import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import webbrowser

# Function to read a barcode from an image
def read_barcode(image_path):
    """Reads a barcode from an image and returns decoded data."""
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

# Function to fetch product details from OpenFoodFacts API (Free)
def get_product_from_openfoodfacts(barcode):
    """Fetches product details using OpenFoodFacts API (Free)."""
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "product" in data:
            product = data["product"]
            title = product.get("product_name", "No product title found")
            brand = product.get("brands", "Unknown brand")
            description = product.get("generic_name", "No description available")
            ingredients = product.get("ingredients_text", "Ingredients not listed")
            category = product.get("categories", "Unknown category")
            return {
                "Product": title,
                "Brand": brand,
                "Description": description,
                "Ingredients": ingredients,
                "Category": category
            }
    
    return None


# Main script execution
image_path = "Unknown.png"  # Change this to your barcode image path
barcode_info = read_barcode(image_path)

if barcode_info:
    for barcode_data, barcode_type in barcode_info:
        print(f"\n📌 Barcode Detected: {barcode_data} (Type: {barcode_type})")
        
        # Fetch product details
        product_info = get_product_from_openfoodfacts(barcode_data)

        if product_info:
            print("\n📦 Product Details (OpenFoodFacts):")
            for key, value in product_info.items():
                print(f"{key}: {value}")

else:
    print("❌ No barcode detected in the image.")
