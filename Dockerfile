# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY app/requirements.txt .


# Install the Python dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install nano (update before installation to avoid issues)
RUN apt-get update && apt-get install -y nano && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code into the container
COPY . .

# Expose the port on which the app will run
EXPOSE 443

# Command to run the main application with Uvicorn and SSL
CMD ["python3", "main.py"]
