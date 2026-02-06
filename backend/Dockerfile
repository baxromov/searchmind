FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OCR and PDF processing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgomp1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Configure pip to bypass SSL verification (for Windows SSL issues)
RUN pip config set global.trusted-host "pypi.org pypi.python.org files.pythonhosted.org" && \
    pip config set global.timeout "300"

# Upgrade pip with trusted hosts to bypass SSL verification issues
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --upgrade pip setuptools certifi

# Install large packages first with extended timeout to avoid ReadTimeout
RUN pip install --no-cache-dir --timeout=600 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
    paddlepaddle>=2.6.0 \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install remaining Python dependencies with extended timeout
RUN pip install --no-cache-dir --timeout=600 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/uploads /app/data/faiss_index /app/data/temp

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]