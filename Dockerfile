# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/scripts:$PATH"

# Set working directory
WORKDIR /app

# Install system deps (optional if needed for psycopg2, Pillow, etc.)
# RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .



# Expose port
EXPOSE 8000

# Use ENTRYPOINT + CMD pattern
CMD ["sh","run.sh"]
