# Same pattern as Phase 1 Dockerfile
FROM python:3.11-slim
 
WORKDIR /app
 
# Install dependencies BEFORE copying code (leverages Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy application code
COPY . .
 
# ChromaDB needs a directory to persist data
RUN mkdir -p /app/chroma_db
 
EXPOSE 8000
 
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
