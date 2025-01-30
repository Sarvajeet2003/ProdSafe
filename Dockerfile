# Use a lightweight Python base image
FROM python:3.11-slim

# Install required system dependencies (zbar and OpenCV dependencies)
RUN apt-get update && apt-get install -y \
    zbar \
    libgl1-mesa-glx \
    libglib2.0-0 && \
    apt-get clean

# Set the working directory inside the container
WORKDIR /app

# Copy the application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Run the application using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
