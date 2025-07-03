# Use a minimal, official image
FROM python:3.12-slim

# Set environment variables for security
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Add non-root user and group
RUN groupadd --gid 1001 aedile \
  && useradd --uid 1001 --gid aedile --shell /usr/sbin/nologin --create-home aedile

# Install security updates and dependencies. 
# Cleanup apt cache to minimize image size.
RUN apt-get update \
  && apt-get upgrade -y --no-install-recommends \
  && apt-get install -y --no-install-recommends \
  build-essential \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Use a dedicated working directory
WORKDIR /app

# Copy requirements and install dependencies as non-root (if possible)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Now copy only the minimal app files 
COPY . .

# Change file permissions and ownership to the non-root user
RUN chown -R aedile:aedile /app

# Switch to non-root user
USER aedile

# Specify a non-shell form for CMD for entry point hardening
CMD ["python", "src/main.py"]