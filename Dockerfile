# Use the official Python slim image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your FastAPI app runs on
EXPOSE 8070

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8070"]