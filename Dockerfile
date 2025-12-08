# Use Python 3.9
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies (Flask + System Monitor + Database Driver)
RUN pip install flask psutil psycopg2-binary

# Run the app
CMD ["python", "app.py"]