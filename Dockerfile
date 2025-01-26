# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set a working directory
WORKDIR /app

# Copy requirements.txt first (for caching layers)
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . /app/

# By default, run main.py (CLI)
CMD ["python", "main.py"]
