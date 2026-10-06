# Use the official, lightweight Python 3.12 image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the frontend code
COPY . .

# Expose the dynamic port used by Cloud Run
EXPOSE 8080

# Command to run Streamlit dynamically on the port Cloud Run assigns
# Note: We use shell execution (sh -c) so the $PORT environment variable evaluates properly
CMD sh -c "streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false"