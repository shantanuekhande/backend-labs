FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy dependencies first (to use Docker's caching)
COPY requirements.txt .

# Install dependencies inside the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your local code into the container
COPY . .

# Set the default command to run Django on all network interfaces
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]