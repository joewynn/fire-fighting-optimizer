FROM python:3.11-slim

# Install System Dependencies for Geospatial (GDAL, GEOS, Proj)
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    libgeos-dev \
    libproj-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL Environment Variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

# Copy and Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
COPY . .

# Create directories for runtime data
RUN mkdir -p data results

# Expose Streamlit Port
EXPOSE 8501

# Healthcheck (Optional but professional)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]