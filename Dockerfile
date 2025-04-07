# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Update pip to the latest version
RUN pip install --upgrade pip

# Copy the requirements file first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (default Flask port is 5000)
EXPOSE 5000

# Set environment variables (optional, can also be set in docker-compose or runtime)
ENV FLASK_ENV=development
# ENV PORT=5000

# Command to run the Flask app using the built-in development server
CMD ["python", "app.py"]