# Stage 1: Build the Python application
FROM python:3.12-alpine AS builder
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --upgrade pip
RUN pip install pipenv

# Install application dependencies
COPY Pipfile Pipfile.lock /app/

# We use the --system flag so packages are installed into the system python
# and not into a virtualenv. Docker containers don't need virtual environments.
RUN pipenv install --system --dev
# Copy the application files into the image
COPY . /app/

# Stage 2: Runtime image
FROM python:3.12-alpine

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Install Nginx
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Configure Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Create necessary directories
RUN mkdir -p /app/static/known_faces /app/temp && \
    chown -R www-data:www-data /app/static /app/temp && \
    chmod -R 755 /app/static /app/temp

# Expose ports
EXPOSE 80

# Start both Nginx and FastAPI
CMD (uvicorn app.main:app --host 0.0.0.0 --port 8000 &) && \
    nginx -g "daemon off;"