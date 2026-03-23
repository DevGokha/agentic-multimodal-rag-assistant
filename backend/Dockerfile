# Step 1: Use Python 3.12 slim image as the base
FROM python:3.12-slim

# Step 2: Set working directory inside the container
WORKDIR /app

# Step 3: Copy requirements first (for better Docker cache layer)
COPY requirements.txt .

# Step 4: Install CPU-only PyTorch first (saves ~1.5GB vs GPU version)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Step 5: Install remaining Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the backend code
COPY . .

# Step 6: Create the data directories for uploads
RUN mkdir -p data/documents data/faiss_index

# Step 7: Expose port 8000 for the FastAPI server
EXPOSE 8000

# Step 8: Start the FastAPI server with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
