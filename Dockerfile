# Stage 1: Build environment with dependencies
FROM python:3.11-slim as builder

WORKDIR /usr/src/app

# Install build dependencies if needed (e.g., for psycopg2)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev

# Install Python dependencies
COPY requirements.txt ./
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# Stage 2: Production environment
FROM python:3.11-slim

WORKDIR /usr/src/app

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Install runtime dependencies if needed (e.g., for psycopg2)
# RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

# Copy installed wheels from builder stage
COPY --from=builder /usr/src/app/wheels /wheels
# Install wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Ensure instance directory exists and set permissions
RUN mkdir -p instance && chown -R app:app instance /usr/src/app
VOLUME /usr/src/app/instance

# Switch to non-root user
USER app

# Expose port
EXPOSE 5000

# Set environment variables (can be overridden)
ENV FLASK_APP run.py
ENV FLASK_ENV production
ENV PYTHONUNBUFFERED 1 # Ensures logs print immediately

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]