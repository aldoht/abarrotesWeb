FROM python:3.9-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    gcc
    # libssl-dev \
    # libffi-dev \
    # python3-dev \
    # cargo \
    # && rm -rf /var/lib/apt/lists/*  # Clean up apt cache to reduce image size

COPY requirements.txt requirements.txt
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "app.py"]