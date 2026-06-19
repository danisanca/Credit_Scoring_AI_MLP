FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# Instala o PyTorch CPU separadamente (menor e mais rapido que a versao GPU)
COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY api/ ./api/
COPY data/ ./data/

# Create models directory
RUN mkdir -p /app/models

# Generate synthetic data and train model on first build
RUN python data/generate_data.py && \
    python src/train.py

# Expose FastAPI port
EXPOSE 8000

# Start API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
