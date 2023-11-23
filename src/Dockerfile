# Use the official Python image for ARM architectures
FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy only the necessary files
COPY serial_socket.py requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the server will listen on
EXPOSE 12345

# Run the script when the container starts
CMD ["python", "serial_socket.py"]