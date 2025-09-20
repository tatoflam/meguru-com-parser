FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the scraper scripts and modules
COPY main.py .
COPY scrapers/ ./scrapers/

# Create output directory
RUN mkdir -p /app/output

# Set the default command
CMD ["python", "main.py", "all"]
