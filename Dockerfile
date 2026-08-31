# Use the official, lightweight Python 3.12 image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the frontend code
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Command to run Streamlit on port 8080
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]