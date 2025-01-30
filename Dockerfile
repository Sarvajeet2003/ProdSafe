# Use a lightweight Python base image
FROM python:3.11-slim

# Install dependencies required for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Set the working directory in the container
WORKDIR /app

# Copy all files to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 5000

# Set the default command to run the Flask app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
