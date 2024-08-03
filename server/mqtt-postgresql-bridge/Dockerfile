FROM python:3.12-slim

RUN apt update && apt install -y postgresql-client && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script into the container
COPY bridge.py .

# Run the Python script
CMD ["python", "bridge.py"]
