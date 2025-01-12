FROM python:3.12-slim
ENV PYTHONUNBUFFERED 1
ENV PORT 8000
# Declare the build argument
# ARG DJANGO_SECRET_KEY

# Optionally, set it as an environment variable during build
# ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}

# Debug: Print environment variables
RUN echo "Environment Variables:" && env


# Example to confirm it's accessible
# RUN echo "Secret Key is: ${DJANGO_SECRET_KEY}"


# Install system dependencies
RUN apt-get update && apt-get install -y \
    zbar-tools \
    libzbar-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
 

RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy and set permissions for entrypoint scripts
COPY ./entrypoint.sh /
COPY ./celery-entrypoint.sh /
RUN chmod +x /entrypoint.sh /celery-entrypoint.sh