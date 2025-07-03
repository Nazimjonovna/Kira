# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /code/

# Expose port 8000 (Django default)
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD sh -c "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"

